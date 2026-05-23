"""
Router /chat — HomeButler AI
Endpoints :
  POST /chat          — 3 modes : agent | rag_only | llm_only
  POST /chat/compare  — même question dans les 3 modes (J3 TP comparaison)
  GET  /chat/stream   — SSE streaming token par token (J3 déploiement)
"""

import asyncio
import os
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from api.limiter import limiter

router = APIRouter(prefix="/chat", tags=["chat"])

# Atelier 05 scope guard — route comparaison réservée à l'atelier 06
_ENABLE_COMPARE = os.getenv("ENABLE_COMPARE_ROUTES", "false").lower() == "true"


# ── Modèles Pydantic ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default="default")
    mode: Literal["agent", "rag_only", "llm_only"] = "agent"
    debug: bool = False


class SourceDoc(BaseModel):
    source: str
    page: int | None = None
    excerpt: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
    llm_provider: str
    mode: str
    sources: list[SourceDoc] = []
    token_usage: dict | None = None
    steps: list[str] = []


# ── Helpers privés ────────────────────────────────────────────────────────────

def _docs_to_sources(docs: list) -> list[SourceDoc]:
    return [
        SourceDoc(
            source=d.metadata.get("source", "inconnu"),
            page=d.metadata.get("page"),
            excerpt=d.page_content[:150],
        )
        for d in docs
    ]


def _extract_token_usage(result) -> dict | None:
    usage = getattr(result, "usage_metadata", None)
    if isinstance(usage, dict) and usage:
        return {
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "cache_read": usage.get("input_token_details", {}).get("cache_read", 0),
        }
    return None


async def _call_llm_only(message: str) -> dict:
    """Mode llm_only : pas de contexte documentaire → démontre les hallucinations (J1 matin)."""
    from homebutler.llm.provider import get_llm
    from homebutler.llm.prompts import BARE_LLM_TEMPLATE

    loop = asyncio.get_event_loop()
    llm = get_llm(temperature=0.1)
    chain = BARE_LLM_TEMPLATE | llm
    result = await loop.run_in_executor(None, chain.invoke, {"question": message})
    return {
        "response": result.content,
        "token_usage": _extract_token_usage(result),
        "sources": [],
        "steps": [],
    }


async def _call_rag_only(message: str) -> dict:
    """Mode rag_only : retrieval + LLM sans agent → RAG pur (J1 après-midi)."""
    from homebutler.llm.provider import get_llm_cached
    from homebutler.llm.prompts import RAG_QA_TEMPLATE
    from homebutler.rag.retriever import retrieve, format_docs_for_context

    loop = asyncio.get_event_loop()
    docs = await loop.run_in_executor(None, retrieve, message)
    context = format_docs_for_context(docs)
    llm = get_llm_cached(temperature=0.1)
    chain = RAG_QA_TEMPLATE | llm
    result = await loop.run_in_executor(
        None, chain.invoke, {"question": message, "context": context}
    )
    return {
        "response": result.content,
        "token_usage": _extract_token_usage(result),
        "sources": [s.model_dump() for s in _docs_to_sources(docs)],
        "steps": [],
    }


async def _call_agent(message: str, session_id: str, debug: bool = False) -> dict:
    """Mode agent : ReAct avec mémoire de session et outils."""
    from homebutler.agent.react_agent import get_session_agent, get_session_agent_debug

    loop = asyncio.get_event_loop()
    agent = get_session_agent_debug(session_id) if debug else get_session_agent(session_id)
    result = await loop.run_in_executor(
        None, agent.invoke, {"input": message, "chat_history": []}
    )
    response_text = result.get("output", "Je n'ai pas pu générer de réponse.")

    # Extraire les sources depuis les steps intermédiaires si disponibles
    sources = []
    steps_log = []
    if debug and "intermediate_steps" in result:
        for action, observation in result["intermediate_steps"]:
            steps_log.append(
                f"Action: {action.tool} | Input: {str(action.tool_input)[:80]}"
            )
            steps_log.append(f"Observation: {str(observation)[:120]}")

    return {
        "response": response_text,
        "token_usage": None,
        "sources": sources,
        "steps": steps_log,
    }


# ── POST /chat ────────────────────────────────────────────────────────────────

@router.post("", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(request: Request, req: ChatRequest):
    """
    Endpoint principal. Modes :
    - agent    : ReAct avec 4 outils + mémoire session (défaut)
    - rag_only : RAG pur, retourne les sources utilisées
    - llm_only : LLM sans contexte, démontre les hallucinations (J1 matin)
    debug=True : retourne les steps intermédiaires de l'agent.
    """
    from homebutler import config

    try:
        if req.mode == "llm_only":
            data = await _call_llm_only(req.message)
        elif req.mode == "rag_only":
            data = await _call_rag_only(req.message)
        else:
            data = await _call_agent(req.message, req.session_id, debug=req.debug)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur {req.mode} : {str(e)}")

    return ChatResponse(
        response=data["response"],
        session_id=req.session_id,
        llm_provider=config.LLM_PROVIDER,
        mode=req.mode,
        sources=[SourceDoc(**s) for s in data.get("sources", [])],
        token_usage=data.get("token_usage"),
        steps=data.get("steps", []),
    )


# ── POST /chat/compare ────────────────────────────────────────────────────────

@router.post("/compare", include_in_schema=_ENABLE_COMPARE)
async def chat_compare(req: ChatRequest):
    """
    Lance la même question dans les 3 modes en parallèle.
    Démo pédagogique centrale J3 : évaluation comparative LLM seul vs RAG vs agent.
    Correspond à la grille de décision (draft.md) : LLM seul → hallucine | RAG → factuel | agent → orchestré.
    Réservée à l'atelier 06 — activer ENABLE_COMPARE_ROUTES=true dans .env
    """
    if not _ENABLE_COMPARE:
        raise HTTPException(status_code=404, detail="Route réservée à l'atelier 06. Définir ENABLE_COMPARE_ROUTES=true dans .env")
    from homebutler import config

    try:
        llm_result, rag_result, agent_result = await asyncio.gather(
            _call_llm_only(req.message),
            _call_rag_only(req.message),
            _call_agent(req.message, f"compare-{req.session_id}", debug=True),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur compare : {str(e)}")

    return {
        "question": req.message,
        "llm_provider": config.LLM_PROVIDER,
        "llm_only": llm_result,
        "rag_only": rag_result,
        "agent": agent_result,
    }


# ── GET /chat/stream ──────────────────────────────────────────────────────────

@router.get("/stream")
async def chat_stream(message: str, session_id: str = "default"):
    """
    Streaming SSE token par token (J3 matin — déploiement réel).
    Utilise BARE_LLM_TEMPLATE sans contexte documentaire (démo vitesse).
    curl -N 'http://localhost:8000/chat/stream?message=Bonjour'
    """
    from homebutler.llm.provider import get_llm
    from homebutler.llm.prompts import BARE_LLM_TEMPLATE
    from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler

    handler = AsyncIteratorCallbackHandler()
    llm = get_llm(temperature=0.1, streaming=True)
    llm.callbacks = [handler]
    chain = BARE_LLM_TEMPLATE | llm

    async def event_generator():
        task = asyncio.create_task(
            chain.ainvoke({"question": message})
        )
        try:
            async for token in handler.aiter():
                yield f"data: {token}\n\n"
        except Exception:
            pass
        await task
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
