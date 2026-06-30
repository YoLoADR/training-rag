import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Provider ──────────────────────────────────────────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "homebutler")

# ── Observabilité ─────────────────────────────────────────────────────────────
LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "homebutler-ai")
TRACING_PROVIDER: str = os.getenv("TRACING_PROVIDER", "langsmith")
LANGFUSE_HOST: str = os.getenv("LANGFUSE_HOST", "http://localhost:3300")
LANGFUSE_PUBLIC_KEY: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY: str = os.getenv("LANGFUSE_SECRET_KEY", "")

# ── Bases vectorielles ────────────────────────────────────────────────────────
CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./data/chroma_db")
FAISS_PATH: str = os.getenv("FAISS_PATH", "./data/faiss_index")

# ── Services ──────────────────────────────────────────────────────────────────
OPEN_METEO_CACHE_TTL: int = int(os.getenv("OPEN_METEO_CACHE_TTL", "3600"))
DATA_DIR: str = os.getenv("DATA_DIR", "./data")
DOCUMENTS_DIR: str = os.path.join(DATA_DIR, "documents")
ENERGY_CSV: str = os.path.join(DATA_DIR, "energy", "consumption.csv")
PRODUCERS_JSON: str = os.path.join(DATA_DIR, "marketplace", "producers.json")

# ── API ───────────────────────────────────────────────────────────────────────
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
API_KEY: str = os.getenv("API_KEY", "homebutler-dev-key")

# ── Azure AI Search (Atelier 09 — module avancé, optionnel) ────────────────────
# Vides par défaut : n'impacte aucun autre atelier. Renseignés via azure_provision.sh.
AZURE_SEARCH_ENDPOINT: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
AZURE_SEARCH_KEY: str = os.getenv("AZURE_SEARCH_KEY", "")
AZURE_SEARCH_INDEX: str = os.getenv("AZURE_SEARCH_INDEX", "homebutler-index")

# Propagate LangSmith env vars if tracing enabled
if LANGCHAIN_TRACING_V2:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    if LANGCHAIN_PROJECT:
        os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
