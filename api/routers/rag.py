"""
Router /rag — Endpoints pédagogiques RAG (atelier 05 : retrieve seul)
  POST /rag/retrieve  — chunks récupérés pour une query (transparence)

Note : les endpoints /rag/evaluate et /rag/compare-strategies sont introduits
en atelier 06 (Fine-tuning vs RAG).
"""

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/rag", tags=["rag"])


# ── Modèles ───────────────────────────────────────────────────────────────────

class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    strategy: Literal["fixed", "recursive", "ensemble"] = "ensemble"
    k: int = Field(default=5, ge=1, le=10)


class ChunkResult(BaseModel):
    rank: int
    source: str
    page: int | None = None
    excerpt: str
    char_count: int


# ── Helpers ───────────────────────────────────────────────────────────────────

def _retrieve_with_strategy(query: str, strategy: str, k: int) -> list:
    """
    Retrieval selon la stratégie choisie.
    - fixed     : FAISS seul (dense similarity, chunks figés)
    - recursive : ChromaDB seul (chunking sémantique, filtres metadata)
    - ensemble  : FAISS 60% + ChromaDB 40% (meilleur rappel)
    """
    from homebutler.rag.retriever import (
        retrieve, get_faiss_retriever, get_chroma_retriever
    )

    if strategy == "ensemble":
        return retrieve(query, use_ensemble=True, k=k)
    elif strategy == "fixed":
        retriever = get_faiss_retriever(k=k)
        return retriever.invoke(query)
    else:  # recursive → ChromaDB pour montrer des chunks différents
        try:
            retriever = get_chroma_retriever(k=k)
            return retriever.invoke(query)
        except FileNotFoundError:
            retriever = get_faiss_retriever(k=k)
            return retriever.invoke(query)


# ── POST /rag/retrieve ────────────────────────────────────────────────────────

@router.post("/retrieve", response_model=dict)
async def rag_retrieve(req: RetrieveRequest):
    """
    Retourne les chunks récupérés pour une query avec la stratégie choisie.
    Pédagogie J3 atelier 05 : transparence sur ce que le RAG récupère.
    """
    try:
        docs = _retrieve_with_strategy(req.query, req.strategy, req.k)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    chunks = [
        ChunkResult(
            rank=i + 1,
            source=d.metadata.get("source", "inconnu"),
            page=d.metadata.get("page"),
            excerpt=d.page_content[:200],
            char_count=len(d.page_content),
        ).model_dump()
        for i, d in enumerate(docs)
    ]

    return {
        "query": req.query,
        "strategy": req.strategy,
        "k_requested": req.k,
        "chunks_found": len(chunks),
        "results": chunks,
    }
