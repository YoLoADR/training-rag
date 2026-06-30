"""
Test Bug v3 At.08 — top_n non passé au reranker (sortie non bornée à top_n)

Logique :
- get_reranked_retriever doit transmettre top_n à FlashrankRerank pour borner
  la sortie aux N meilleurs documents reclassés.
- Le bug instancie FlashrankRerank SANS top_n → flashrank applique sa valeur par
  défaut (3) au lieu des 5 attendus → la sortie n'a pas la taille voulue.
- Test : la sortie finale doit contenir exactement RERANK_TOP_N documents.
- Bug actif : len(final) == 3 (défaut flashrank) → test ECHOUE.
- Corrigé : len(final) == RERANK_TOP_N (5) → test PASSE.

Comment utiliser :
1. git apply ateliers/atelier-08-optimisation/bugs/v3.patch
2. pytest ateliers/atelier-08-optimisation/bugs/test_v3.py -v   (doit ECHOUER)
3. Répare : passe top_n=top_n à FlashrankRerank(...)
4. pytest  (doit PASSER)
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from homebutler import config
from homebutler.rag.ingestion import load_pdf_with_metadata, chunk_recursive
from homebutler.rag.vectorstore_faiss import build_faiss_index

QUESTION = "Comment purger les radiateurs ?"


def _ensure_index():
    docs_dir = config.DOCUMENTS_DIR
    if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
        pytest.skip("PDFs absents — lancer python scripts/generate_documents.py")
    if not os.path.exists(config.FAISS_PATH):
        pages = []
        for f in sorted(os.listdir(docs_dir)):
            if f.endswith(".pdf"):
                pages.extend(load_pdf_with_metadata(os.path.join(docs_dir, f)))
        build_faiss_index(chunk_recursive(pages, chunk_size=512, chunk_overlap=50),
                          force_rebuild=True)


def test_sortie_bornee_a_top_n():
    _ensure_index()
    pytest.importorskip("flashrank")
    from homebutler.rag.reranking import get_reranked_retriever, RERANK_TOP_N

    final_docs = get_reranked_retriever(base_k=20, top_n=RERANK_TOP_N).invoke(QUESTION)
    print(f"\ndocuments finaux = {len(final_docs)} (attendu {RERANK_TOP_N})")

    assert len(final_docs) == RERANK_TOP_N, (
        f"La sortie contient {len(final_docs)} documents au lieu de {RERANK_TOP_N}.\n"
        "Le reranker n'a pas reçu top_n → il applique sa valeur par défaut.\n"
        "Indice : passe top_n=top_n à FlashrankRerank(model=..., top_n=top_n)."
    )
