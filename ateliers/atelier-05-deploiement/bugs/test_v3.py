"""
Bug v3 — Timeout manquant dans asyncio.wait_for (analyse statique).

Le bug : timeout=None dans asyncio.wait_for() désactive le timeout.
Un appel LLM bloqué peut immobiliser le worker FastAPI indéfiniment.

Applique le patch : git apply ateliers/atelier-05-deploiement/bugs/v3.patch
Lance ensuite   : pytest ateliers/atelier-05-deploiement/bugs/test_v3.py -v

Le test ECHOUE si timeout=None est présent dans chat.py.
Le test PASSE quand un timeout numérique explicite est défini.

Pas d'appel LLM — analyse statique de api/routers/chat.py.
"""

import pathlib


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent
CHAT_ROUTER = BASE_DIR / "api" / "routers" / "chat.py"


def _get_source() -> str:
    return CHAT_ROUTER.read_text(encoding="utf-8")


def test_no_timeout_none():
    """timeout=None ne doit pas apparaître dans api/routers/chat.py."""
    source = _get_source()

    assert "timeout=None" not in source, (
        "BUG ACTIF : 'timeout=None' trouvé dans api/routers/chat.py.\n"
        "asyncio.wait_for() avec timeout=None ne limite pas la durée d'attente — "
        "un appel LLM bloqué peut immobiliser le worker indéfiniment.\n"
        "Remplace par un timeout numérique, par exemple timeout=30.0."
    )


def test_wait_for_present():
    """asyncio.wait_for() doit être utilisé dans _call_llm_only."""
    source = _get_source()

    assert "wait_for" in source, (
        "asyncio.wait_for() absent de api/routers/chat.py.\n"
        "Ajoute asyncio.wait_for(..., timeout=30.0) autour de l'appel LLM "
        "dans _call_llm_only() pour protéger le worker contre les appels bloquants."
    )


def test_timeout_is_numeric():
    """Le timeout doit être une valeur numérique explicite (pas None, pas absent)."""
    source = _get_source()

    # Vérifie qu'un timeout numérique est présent (ex: 30.0, 60.0, etc.)
    import re
    has_numeric_timeout = bool(
        re.search(r"timeout=\d+(\.\d+)?", source)
    )
    assert has_numeric_timeout, (
        "Aucun timeout numérique trouvé dans api/routers/chat.py.\n"
        "asyncio.wait_for() doit avoir un timeout explicite, ex: timeout=30.0."
    )
