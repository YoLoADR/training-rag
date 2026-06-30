"""
Observabilité — handler Langfuse + scoring des traces.

Atelier 07. Deux usages :
  1. TRACER  : passer le handler en callback à l'agent/la chaîne → chaque appel
     (prompt, réponse, latence, tokens, coût) apparaît dans Langfuse.
  2. NOTER   : attacher un score (LLM-as-judge, faithfulness…) à une trace.

SDK Langfuse v2 (`langfuse==2.57.1`) :
  - handler : `from langfuse.callback import CallbackHandler`  (PAS `langfuse.langchain` = v3)
  - client  : `from langfuse import Langfuse` → `.score(...)`, `.flush()`

Sans clés (LANGFUSE_PUBLIC_KEY/SECRET_KEY) → tout devient no-op silencieux : le reste
de l'atelier (RAGAS, judge) fonctionne quand même. En formation, on privilégie Langfuse
Cloud (déjà câblé en AT05) ; le self-host Docker est en bonus (docker-compose.langfuse.yml).
"""

from homebutler import config


def _keys_present() -> bool:
    return bool(config.LANGFUSE_PUBLIC_KEY and config.LANGFUSE_SECRET_KEY)


def get_langfuse_handler():
    """Retourne un CallbackHandler Langfuse (v2) à passer en `callbacks=[...]`.
    None si les clés ne sont pas configurées."""
    if not _keys_present():
        return None
    from langfuse.callback import CallbackHandler  # SDK v2 (ne pas utiliser l'API v3)
    return CallbackHandler(
        public_key=config.LANGFUSE_PUBLIC_KEY,
        secret_key=config.LANGFUSE_SECRET_KEY,
        host=config.LANGFUSE_HOST,
    )


def get_langfuse_client():
    """Client Langfuse bas niveau (pour scorer une trace). None si pas de clés."""
    if not _keys_present():
        return None
    from langfuse import Langfuse
    return Langfuse(
        public_key=config.LANGFUSE_PUBLIC_KEY,
        secret_key=config.LANGFUSE_SECRET_KEY,
        host=config.LANGFUSE_HOST,
    )


def flush_traces(handler=None) -> None:
    """Force l'envoi des traces en attente (l'envoi est asynchrone par défaut).
    À appeler en fin de script, sinon les dernières traces peuvent être perdues."""
    # Le handler v2 expose flush() ; le client aussi. On flush les deux si présents.
    if handler is not None and hasattr(handler, "flush"):
        try:
            handler.flush()
        except Exception:
            pass
    client = get_langfuse_client()
    if client is not None:
        try:
            client.flush()
        except Exception:
            pass


def score_trace(trace_id: str, name: str, value: float, comment: str = "") -> bool:
    """Attache un score (0-1) à une trace Langfuse. Retourne True si envoyé.
    No-op (False) si pas de clés ou pas de trace_id."""
    client = get_langfuse_client()
    if client is None or not trace_id:
        return False
    try:
        client.score(trace_id=trace_id, name=name, value=value, comment=comment)
        return True
    except Exception:
        return False
