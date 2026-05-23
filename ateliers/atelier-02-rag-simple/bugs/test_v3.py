"""
Test Bug v3 At.02 — reconstruction index à chaque query (latence catastrophique)

Logique :
- Le bug appelle build_faiss_index(force_rebuild=True) à l'intérieur d'une boucle de requêtes
- Chaque requête déclenche une reconstruction complète de l'index (10-30s sur les PDFs HomeButler)
- Ce test mesure la latence de 2 requêtes consécutives
- Bug actif : latence > 5s par requête → le test ECHOUE sur l'assertion de latence
- Bug réparé : index construit une fois, latence < 2s → test PASSE

Note : ce test nécessite le modèle d'embeddings (fastembed) et les PDFs.

Comment utiliser :
1. git apply ateliers/atelier-02-rag-simple/bugs/v3.patch
2. pytest ateliers/atelier-02-rag-simple/bugs/test_v3.py -v  (doit ECHOUER — très lent)
3. Répare : construire l'index UNE FOIS en dehors de la boucle de requêtes
4. pytest  (doit PASSER rapidement)
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from homebutler import config
from homebutler.rag.ingestion import load_pdf_with_metadata, chunk_recursive
from homebutler.rag.vectorstore_faiss import build_faiss_index

LATENCE_MAX_PAR_REQUETE = 5.0  # secondes — retrieval pur doit être < 5s

QUESTIONS_TEST = [
    "Quelle est la marque de ma chaudière ?",
    "Quelle est la durée du bail ?",
]


def load_pages() -> list:
    docs_dir = config.DOCUMENTS_DIR
    if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
        pytest.skip("PDFs absents — lancer python scripts/generate_documents.py")
    pages = []
    for f in sorted(os.listdir(docs_dir)):
        if f.endswith(".pdf"):
            pages.extend(load_pdf_with_metadata(os.path.join(docs_dir, f)))
    return pages


def test_retrieval_rapide_apres_construction():
    """
    Après construction de l'index (une seule fois), chaque requête de retrieval
    doit s'exécuter en moins de LATENCE_MAX_PAR_REQUETE secondes.

    Avec bug v3 (force_rebuild=True dans la boucle) :
    - Chaque requête reconstruit l'index complètement → > 10s par requête → ECHOUE

    Avec le fix (index construit une seule fois, réutilisé) :
    - La requête n'est qu'une recherche ANN → < 1s → PASSE
    """
    pages = load_pages()
    chunks = chunk_recursive(pages, chunk_size=512, chunk_overlap=50)

    # Construction initiale (une seule fois — c'est la version CORRECTE)
    print(f"\nConstruction index sur {len(chunks)} chunks...")
    t_build = time.time()
    store = build_faiss_index(chunks, force_rebuild=True)
    build_time = time.time() - t_build
    print(f"Construction : {build_time:.1f}s")

    # Maintenant, mesure la latence de retrieval SANS reconstruction
    latences = []
    for q in QUESTIONS_TEST:
        t0 = time.time()
        results = store.similarity_search(q, k=5)
        latence = time.time() - t0
        latences.append(latence)
        print(f"  Requête '{q[:40]}...' : {latence:.3f}s ({len(results)} résultats)")

    latence_max_observee = max(latences)
    latence_moyenne = sum(latences) / len(latences)

    print(f"\nLatence max : {latence_max_observee:.3f}s (limite : {LATENCE_MAX_PAR_REQUETE}s)")
    print(f"Latence moyenne : {latence_moyenne:.3f}s")

    assert latence_max_observee < LATENCE_MAX_PAR_REQUETE, (
        f"Latence de retrieval trop élevée : {latence_max_observee:.1f}s > {LATENCE_MAX_PAR_REQUETE}s.\n"
        "Cause probable : l'index FAISS est reconstruit à chaque requête (force_rebuild=True dans la boucle).\n"
        "Fix : construire l'index UNE SEULE FOIS avant la boucle de requêtes :\n"
        "  faiss_store = build_faiss_index(chunks, force_rebuild=True)  # hors boucle\n"
        "  for q in questions:\n"
        "      results = faiss_store.similarity_search(q, k=5)  # retrieval rapide"
    )
