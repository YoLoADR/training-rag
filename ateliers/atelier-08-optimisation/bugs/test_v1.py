"""
Test Bug v1 At.08 — base_k == top_n (l'entonnoir du reranking est cassé)

Logique :
- Le bug ramène RERANK_BASE_K de 20 à 5 (== RERANK_TOP_N).
- Conséquence : le retriever de base ne fournit plus QUE 5 candidats, et le
  reranker en garde 5 → il n'a plus rien à FILTRER (il ne fait que réordonner).
- Ce test vérifie que le pool de candidats (base_retriever) est STRICTEMENT
  plus grand que la sortie finale (top_n). C'est la définition de l'entonnoir.
- Bug actif (base_k=5)   : base == final → test ECHOUE.
- Corrigé (base_k=20)    : base (20) > final (5) → test PASSE.

Comment utiliser :
1. git apply ateliers/atelier-08-optimisation/bugs/v1.patch
2. pytest ateliers/atelier-08-optimisation/bugs/test_v1.py -v   (doit ECHOUER)
3. Répare : RERANK_BASE_K doit rester nettement > RERANK_TOP_N (ex. 20 vs 5)
4. pytest  (doit PASSER)
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from homebutler import config
from homebutler.rag.ingestion import load_pdf_with_metadata, chunk_recursive
from homebutler.rag.vectorstore_faiss import build_faiss_index

QUESTION = "Quelle est la marque de ma chaudière ?"


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


def test_funnel_base_k_greater_than_top_n():
    """L'entonnoir : le pool de candidats doit être plus grand que la sortie."""
    _ensure_index()
    pytest.importorskip("flashrank")
    from homebutler.rag.reranking import get_reranked_retriever

    retriever = get_reranked_retriever()  # utilise les défauts RERANK_BASE_K / TOP_N
    base_docs = retriever.base_retriever.invoke(QUESTION)
    final_docs = retriever.invoke(QUESTION)

    print(f"\ncandidats (base_k) = {len(base_docs)}  |  finaux (top_n) = {len(final_docs)}")

    assert len(base_docs) > len(final_docs), (
        f"Pas d'entonnoir : base_retriever renvoie {len(base_docs)} candidats "
        f"et la sortie en garde {len(final_docs)} — le reranker ne FILTRE plus rien.\n"
        "Indice : RERANK_BASE_K doit être nettement plus grand que RERANK_TOP_N.\n"
        "Valeur correcte : RERANK_BASE_K=20 (pool large) vs RERANK_TOP_N=5 (sortie)."
    )
