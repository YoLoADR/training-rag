"""
Bug v3 — Test : l'API doit répondre dans un délai raisonnable (timeout < 30s).

Applique d'abord le patch : git apply ateliers/atelier-05-deploiement/bugs/v3.patch
Lance ensuite : pytest ateliers/atelier-05-deploiement/bugs/test_v3.py -v

Le test ne REUSSIT pas automatiquement avec ce bug (le timeout est None → l'appel
peut ne jamais revenir). En pratique, ce test vérifie que le code de l'API inclut
un timeout explicite côté asyncio. Inspecte la source après application du patch.

Pré-requis : API démarrée sur localhost:8000
"""

import httpx
import pytest


@pytest.mark.asyncio
async def test_chat_responds_within_timeout():
    """L'endpoint /chat doit répondre dans les 35 secondes (timeout client)."""
    async with httpx.AsyncClient(timeout=35.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/chat",
                json={"message": "Bonjour, quelle est la marque de ma chaudière ?", "mode": "llm_only"},
            )
            # Si on arrive ici, la réponse est arrivée dans les 35s
            assert response.status_code in (200, 429), (
                f"Code HTTP inattendu : {response.status_code}"
            )
        except httpx.ReadTimeout:
            pytest.fail(
                "TIMEOUT : l'API n'a pas répondu dans 35s. "
                "Vérifie que asyncio.wait_for() a un timeout explicite (ex: 30.0) "
                "dans _call_llm_only(), _call_rag_only() et _call_agent()."
            )


def test_timeout_code_present():
    """Vérifie que le code source contient un timeout explicite dans chat.py."""
    import pathlib
    chat_source = pathlib.Path("api/routers/chat.py").read_text()
    assert "timeout=None" not in chat_source, (
        "BUG ACTIF : 'timeout=None' trouvé dans api/routers/chat.py. "
        "Un timeout=None dans asyncio.wait_for() désactive complètement le timeout. "
        "Remplace par timeout=30.0 (ou une valeur depuis config)."
    )
    assert "wait_for" in chat_source, (
        "Pas de asyncio.wait_for() trouvé dans chat.py — assure-toi qu'un timeout est bien défini."
    )
