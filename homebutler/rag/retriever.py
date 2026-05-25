"""
Retriever composé : EnsembleRetriever FAISS + ChromaDB.
FAISS  → recherche dense par similarité (MMR pour diversité)
Chroma → recherche avec filtre sur métadonnées

Poids : FAISS 0.6, Chroma 0.4
"""

import os
from langchain.retrievers import EnsembleRetriever
from langchain_core.vectorstores import VectorStoreRetriever
from homebutler import config


def get_faiss_retriever(k: int = 4, fetch_k: int = 20) -> VectorStoreRetriever:
    """
    Retriever FAISS avec MMR (Maximal Marginal Relevance) pour diversifier les résultats.
    fetch_k : nombre de candidats avant reclassement MMR
    k       : nombre de documents finaux retournés
    """
    from homebutler.rag.vectorstore import load_faiss_index

    faiss_path = config.FAISS_PATH
    if not os.path.exists(faiss_path):
        raise FileNotFoundError(
            f"Index FAISS non trouvé : {faiss_path}\n"
            "Lancez d'abord l'indexation RAG (voir README)."
        )

    vectorstore = load_faiss_index(faiss_path)
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k},
    )


def get_chroma_retriever(collection: str = "homebutler_docs", k: int = 3) -> VectorStoreRetriever:
    """
    Retriever ChromaDB — supporte les filtres sur métadonnées (source, page).
    """
    from homebutler.rag.vectorstore import load_chroma_db

    chroma_path = config.CHROMA_PATH
    if not os.path.exists(chroma_path):
        raise FileNotFoundError(
            f"Base ChromaDB non trouvée : {chroma_path}\n"
            "Lancez d'abord l'indexation RAG (voir README)."
        )

    vectorstore = load_chroma_db(collection=collection)
    return vectorstore.as_retriever(search_kwargs={"k": k})


def get_ensemble_retriever(faiss_k: int = 4, chroma_k: int = 3) -> EnsembleRetriever:
    """
    EnsembleRetriever qui combine FAISS (60%) et ChromaDB (40%).
    Retourne jusqu'à faiss_k + chroma_k documents dédupliqués.

    Concept Atelier 03 : "hybrid retrieval" = combiner plusieurs retrievers
    avec des poids pour balancer leurs forces. Ici FAISS apporte la
    recherche dense (sens), ChromaDB apporte la filtrabilité métadonnées.

    --- Indice léger ---
    Construis les 2 retrievers via `get_faiss_retriever(k=...)` et
    `get_chroma_retriever(k=...)`, puis emballe-les dans
    `EnsembleRetriever(retrievers=[...], weights=[...])` (LangChain — déjà importé).
    Le poids 0.6 pour FAISS / 0.4 pour ChromaDB est celui décidé dans le
    cours — FAISS est plus précis sur la sémantique brute, donc favorisé.

    --- Indice fort ---
    ```python
    faiss_retriever = get_faiss_retriever(k=faiss_k)
    chroma_retriever = get_chroma_retriever(k=chroma_k)
    return EnsembleRetriever(
        retrievers=[faiss_retriever, chroma_retriever],
        weights=[0.6, 0.4],   # FAISS dominant — voir docstring
    )
    ```
    """
    raise NotImplementedError(
        "Atelier 03 § 3.3 — EnsembleRetriever. "
        "Solution : git diff student/03-pipeline-agent atelier/03-pipeline-agent -- homebutler/rag/retriever.py"
    )


def retrieve(query: str, use_ensemble: bool = True, k: int = 4) -> list:
    """
    Point d'entrée simple pour le retrieval.
    Retourne une liste de Documents LangChain.
    """
    if use_ensemble:
        retriever = get_ensemble_retriever(faiss_k=k, chroma_k=max(k - 1, 2))
    else:
        retriever = get_faiss_retriever(k=k)

    return retriever.invoke(query)


def format_docs_for_context(docs: list) -> str:
    """Formate les documents récupérés pour l'injection dans un prompt LLM."""
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "inconnu")
        page = doc.metadata.get("page", "")
        page_str = f" p.{page}" if page else ""
        parts.append(f"[{source}{page_str}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)
