"""
API FastAPI HomeButler AI.
Endpoints : /chat, /consumption/analyze, /products/search, /order, /rag/*
Sécurité  : filtre prompt injection (19 patterns), rate limiting, clé API optionnelle
"""

import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from homebutler import config
from api.limiter import limiter

# ── Patterns de détection prompt injection ────────────────────────────────────
# 19 patterns couvrant FR + EN (J3 atelier sécurité)
_INJECTION_PATTERNS = [
    # Français — instruction override
    r"ignore\s+(tes|les|toutes|mes|vos)\s+instructions",
    r"oublie\s+(le|ton|tes|votre|toutes)\s+(contexte|instructions?|prompt)",
    r"répète\s+tes\s+instructions",
    r"tu\s+es\s+maintenant",
    r"désactive\s+tes\s+restrictions",
    r"fais\s+semblant",
    r"jeu\s+de\s+r[oô]le",
    r"en\s+tant\s+qu.IA\s+sans\s+restrictions",
    # Français — extraction système
    r"montre.moi\s+(ton|le)\s+prompt",
    r"dis.moi\s+tes\s+instructions",
    # Anglais — jailbreak classiques
    r"jailbreak",
    r"DAN\s+mode",
    r"developer\s+mode",
    r"act\s+as\s+",
    r"pretend\s+(you\s+are|to\s+be)",
    r"simulate\s+(being|you\s+are)",
    r"roleplay\s+as",
    r"disregard\s+(all|your|previous)",
    r"ignore\s+all\s+previous",
    r"system\s*prompt",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)

# ── API Key (optionnel — pour simuler l'auth en production) ──────────────────
_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(_API_KEY_HEADER)):
    """Validation clé API optionnelle (activée si API_KEY est défini dans .env)."""
    if config.API_KEY and config.API_KEY != "homebutler-dev-key" and api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Clé API invalide ou manquante.")


# ── Lifespan : initialisation au démarrage ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("HomeButler AI — démarrage de l'API")
    try:
        from homebutler.agent.react_agent import get_singleton_agent
        get_singleton_agent(verbose=False)
        print("  ✓ Agent ReAct initialisé")
    except Exception as e:
        print(f"  ⚠ Agent non initialisé (index RAG manquant ?) : {e}")
    yield
    print("HomeButler AI — arrêt de l'API")


app = FastAPI(
    title="HomeButler AI API",
    description="Conciergerie domestique intelligente — Formation RAFT",
    version="1.1.0",
    lifespan=lifespan,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — permissif pour le développement (à restreindre en production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Middleware : filtre prompt injection ──────────────────────────────────────
@app.middleware("http")
async def prompt_injection_filter(request: Request, call_next):
    if request.method == "POST":
        body_bytes = await request.body()
        body_text = body_bytes.decode("utf-8", errors="ignore")

        if _INJECTION_RE.search(body_text):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "security_filter",
                    "message": "Requête refusée par le filtre de sécurité.",
                },
            )
        request._body = body_bytes

    return await call_next(request)


# ── Routes ────────────────────────────────────────────────────────────────────
from api.routers import chat, consumption, products, orders, rag  # noqa: E402

app.include_router(chat.router)
app.include_router(consumption.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(rag.router)


@app.get("/", tags=["health"])
async def root():
    return {
        "service": "HomeButler AI API",
        "version": "1.1.0",
        "llm_provider": config.LLM_PROVIDER,
        "status": "ok",
        "endpoints": {
            "chat": "POST /chat (modes: agent|rag_only|llm_only)",
            "stream": "GET /chat/stream",
            "rag_retrieve": "POST /rag/retrieve",
        },
    }


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
