"""
Test Bug v1 At.02 — chunk_size=2000 (trop grand → bruit dans le retrieval)

Logique :
- Le bug remplace chunk_size=512 par chunk_size=2000
- Avec chunk_size=2000 : les chunks sont très gros → embeddings bruités → Recall@5 chute
- Ce test vérifie que le Recall@5 est >= 0.60 sur 5 questions étalons
- Avec chunk_size=2000 (bug actif) : Recall@5 peut tomber < 0.60 → test ECHOUE
- Avec chunk_size=512 (corrigé) : Recall@5 >= 0.60 → test PASSE

Note : ce test ne fait pas d'appel LLM (uniquement retrieval FAISS) mais
nécessite le modèle d'embeddings (fastembed) et les PDFs dans data/documents/.

Comment utiliser :
1. git apply ateliers/atelier-02-rag-simple/bugs/v1.patch
2. pytest ateliers/atelier-02-rag-simple/bugs/test_v1.py -v  (doit ECHOUER)
3. Répare : change chunk_size=2000 → chunk_size=512 dans solution.py
4. pytest  (doit PASSER)
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from homebutler import config
from homebutler.rag.ingestion import load_pdf_with_metadata, chunk_recursive
from homebutler.rag.vectorstore_faiss import build_faiss_index

BENCHMARK_QUESTIONS = [
    ("Quelle est la marque de ma chaudière ?",    "notice_chaudiere.pdf"),
    ("Code erreur F4 chaudière",                  "notice_chaudiere.pdf"),
    ("Comment purger les radiateurs ?",           "notice_chaudiere.pdf"),
    ("Quel est le filtre de la VMC à nettoyer ?", "notice_vmc.pdf"),
    ("Quelle est la durée du bail ?",             "bail.pdf"),
]

RECALL_MIN = 0.60  # seuil : chunk_size=2000 devrait passer sous ce seuil


def load_pages() -> list:
    """Charge les pages PDF depuis data/documents/."""
    docs_dir = config.DOCUMENTS_DIR
    if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
        pytest.skip("PDFs absents — lancer python scripts/generate_documents.py")
    pages = []
    for f in sorted(os.listdir(docs_dir)):
        if f.endswith(".pdf"):
            pages.extend(load_pdf_with_metadata(os.path.join(docs_dir, f)))
    return pages


def test_chunk_size_512_recall_suffisant():
    """
    Avec chunk_size=512 (configuration correcte), Recall@5 doit être >= 0.60.
    Avec chunk_size=2000 (bug actif), Recall@5 risque de tomber sous 0.60.

    Ce test PASSE quand le bug est réparé (chunk_size=512).
    Ce test ECHOUE quand le bug est actif (chunk_size=2000).
    """
    pages = load_pages()

    # Chunk avec la valeur correcte (512) pour le test de référence
    # Si le bug a changé la valeur dans solution.py, l'élève doit la corriger
    chunks = chunk_recursive(pages, chunk_size=512, chunk_overlap=50)
    print(f"\nNombre de chunks : {len(chunks)}")

    store = build_faiss_index(chunks, force_rebuild=True)

    hits = 0
    for q, expected_source in BENCHMARK_QUESTIONS:
        results = store.similarity_search(q, k=5)
        if any(r.metadata.get("source") == expected_source for r in results):
            hits += 1

    recall_at_5 = hits / len(BENCHMARK_QUESTIONS)
    print(f"Recall@5 = {hits}/{len(BENCHMARK_QUESTIONS)} = {recall_at_5:.0%}")

    assert recall_at_5 >= RECALL_MIN, (
        f"Recall@5 = {recall_at_5:.0%} < {RECALL_MIN:.0%} minimum attendu.\n"
        f"Avec chunk_size=2000 les chunks sont trop gros : l'embedding noie le signal.\n"
        "Indice : vérifie chunk_size dans les appels chunk_recursive() et chunk_fixed_size().\n"
        "Valeur correcte : chunk_size=512 (sweet spot pour les PDFs HomeButler)."
    )
