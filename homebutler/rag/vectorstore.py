"""
Compatibilité (atelier 02 — FAISS only).
Réexporte les helpers FAISS depuis vectorstore_faiss.py.
Le second backend (filtres métadonnées) est introduit à l'atelier 03.
"""

from homebutler.rag.vectorstore_faiss import (
    EMBEDDING_MODEL,
    get_embeddings,
    build_faiss_index,
    load_faiss_index,
)

__all__ = [
    "EMBEDDING_MODEL",
    "get_embeddings",
    "build_faiss_index",
    "load_faiss_index",
]
