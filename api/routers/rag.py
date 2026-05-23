"""
Router /rag — Endpoints pédagogiques RAG
  POST /rag/retrieve           — chunks récupérés pour une query (transparence)
  POST /rag/evaluate           — benchmark Recall@1/@3/@5 sur QA dataset
  POST /rag/compare-strategies — même query via 3 stratégies de chunking
"""

import json
import os
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/rag", tags=["rag"])

# Atelier 05 scope guard — routes comparaison réservées à l'atelier 06
_ENABLE_COMPARE = os.getenv("ENABLE_COMPARE_ROUTES", "false").lower() == "true"


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


class EvaluateRequest(BaseModel):
    strategy: Literal["fixed", "recursive", "ensemble"] = "ensemble"
    sample_size: int = Field(default=20, ge=5, le=50)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _retrieve_with_strategy(query: str, strategy: str, k: int) -> list:
    """Retrieval selon la stratégie choisie."""
    from homebutler.rag.retriever import (
        retrieve, get_faiss_retriever, get_chroma_retriever
    )

    if strategy == "ensemble":
        return retrieve(query, use_ensemble=True, k=k)
    elif strategy == "fixed":
        # FAISS seulement (index construit en récursif mais simule le fixed pour la démo)
        retriever = get_faiss_retriever(k=k)
        return retriever.invoke(query)
    else:  # recursive
        retriever = get_faiss_retriever(k=k)
        return retriever.invoke(query)


def _keywords_from_output(output: str) -> list[str]:
    """Extrait des mots-clés significatifs d'une réponse de référence."""
    stopwords = {
        "le", "la", "les", "un", "une", "des", "du", "de", "et", "ou", "est",
        "en", "à", "au", "par", "sur", "avec", "pour", "que", "qui", "il",
        "elle", "je", "vous", "nous", "se", "son", "sa", "ses", "votre", "mon",
        "ma", "mes", "ce", "cette", "ces", "tout", "tous", "plus", "très",
    }
    words = output.lower().replace(",", " ").replace(".", " ").split()
    return [w for w in words if len(w) > 4 and w not in stopwords][:10]


# ── POST /rag/retrieve ────────────────────────────────────────────────────────

@router.post("/retrieve", response_model=dict)
async def rag_retrieve(req: RetrieveRequest):
    """
    Retourne les chunks récupérés pour une query avec la stratégie choisie.
    Pédagogie J1 après-midi : transparence sur ce que le RAG récupère.
    Permet de comparer visuellement l'effet du chunking sur le retrieval.
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


# ── POST /rag/evaluate ────────────────────────────────────────────────────────

@router.post("/evaluate", response_model=dict, include_in_schema=_ENABLE_COMPARE)
async def rag_evaluate(req: EvaluateRequest):
    """
    Calcule Recall@1/@3/@5 sur les N premières paires du dataset QA.
    Pédagogie TP J1 : 'Quelle stratégie de découpage offre le meilleur rappel ?'
    Ground truth : si ≥1 chunk contient des mots-clés de la réponse de référence → hit.
    Réservée à l'atelier 06 — activer ENABLE_COMPARE_ROUTES=true dans .env
    """
    if not _ENABLE_COMPARE:
        raise HTTPException(status_code=404, detail="Route réservée à l'atelier 06. Définir ENABLE_COMPARE_ROUTES=true dans .env")
    import asyncio
    from homebutler import config

    qa_path = os.path.join(config.DATA_DIR, "qa_dataset", "concierge_qa.jsonl")
    if not os.path.exists(qa_path):
        raise HTTPException(status_code=404, detail=f"Dataset QA non trouvé : {qa_path}")

    with open(qa_path, encoding="utf-8") as f:
        pairs = [json.loads(line) for line in f if line.strip()]

    pairs = pairs[: req.sample_size]
    loop = asyncio.get_event_loop()

    hits_at = {1: 0, 3: 0, 5: 0}
    per_question = []
    total_chunks = 0

    for pair in pairs:
        question = pair.get("input", "")
        reference = pair.get("output", "")
        keywords = _keywords_from_output(reference)

        try:
            docs = await loop.run_in_executor(
                None, _retrieve_with_strategy, question, req.strategy, 5
            )
        except Exception:
            docs = []

        total_chunks += len(docs)
        sources_returned = list({d.metadata.get("source", "?") for d in docs})
        found_at = None

        for rank, doc in enumerate(docs, 1):
            content_lower = doc.page_content.lower()
            if any(kw in content_lower for kw in keywords):
                found_at = rank
                break

        for k in [1, 3, 5]:
            if found_at is not None and found_at <= k:
                hits_at[k] += 1

        per_question.append({
            "question": question[:80],
            "found_at_rank": found_at,
            "keywords_used": keywords[:5],
            "sources_returned": sources_returned,
        })

    n = len(pairs)
    return {
        "strategy": req.strategy,
        "questions_tested": n,
        "recall_at_1": round(hits_at[1] / n, 3) if n else 0,
        "recall_at_3": round(hits_at[3] / n, 3) if n else 0,
        "recall_at_5": round(hits_at[5] / n, 3) if n else 0,
        "avg_chunks_retrieved": round(total_chunks / n, 1) if n else 0,
        "per_question": per_question,
    }


# ── POST /rag/compare-strategies ─────────────────────────────────────────────

@router.post("/compare-strategies", response_model=dict, include_in_schema=_ENABLE_COMPARE)
async def compare_strategies(query: str):
    """
    Lance fixed + recursive + ensemble sur la même query.
    Pédagogie J1 après-midi : montre que les stratégies retournent des chunks différents.
    Réservée à l'atelier 06 — activer ENABLE_COMPARE_ROUTES=true dans .env
    """
    if not _ENABLE_COMPARE:
        raise HTTPException(status_code=404, detail="Route réservée à l'atelier 06. Définir ENABLE_COMPARE_ROUTES=true dans .env")
    results = {}
    for strategy in ["fixed", "recursive", "ensemble"]:
        try:
            docs = _retrieve_with_strategy(query, strategy, k=4)
            results[strategy] = {
                "chunks_count": len(docs),
                "sources": list({d.metadata.get("source", "?") for d in docs}),
                "top_excerpt": docs[0].page_content[:200] if docs else "",
            }
        except Exception as e:
            results[strategy] = {"error": str(e)}

    return {"query": query, "strategies": results}
