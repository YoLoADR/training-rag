import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Provider (atelier 01 — 6 variables seulement) ─────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "homebutler")
DATA_DIR: str = os.getenv("DATA_DIR", "./data")
