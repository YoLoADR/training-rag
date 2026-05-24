"""
Bug v1 — Fuite de clé API dans la réponse /chat (analyse statique).

Le bug : le champ `api_key` est ajouté au modèle ChatResponse et retourné
dans chaque réponse JSON, exposant la clé Anthropic au frontend.

Applique le patch : git apply ateliers/atelier-05-deploiement/bugs/v1.patch
Lance ensuite   : pytest ateliers/atelier-05-deploiement/bugs/test_v1.py -v

Le test ECHOUE si le bug est actif (api_key dans ChatResponse).
Le test PASSE quand le champ api_key est absent du modèle.

Pas d'appel LLM — analyse statique de api/routers/chat.py.
"""

import pathlib


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent
CHAT_ROUTER = BASE_DIR / "api" / "routers" / "chat.py"


def _get_source() -> str:
    return CHAT_ROUTER.read_text(encoding="utf-8")


def test_api_key_not_in_chat_response_model():
    """Le champ api_key ne doit pas apparaître dans la classe ChatResponse."""
    source = _get_source()

    # Compter les occurrences de "api_key" dans ChatResponse
    # Le bug introduit : api_key: str = ""  dans la classe et
    #                    api_key=os.getenv(...) dans l'instanciation
    assert "api_key" not in source, (
        "BUG ACTIF : 'api_key' trouvé dans api/routers/chat.py.\n"
        "Le champ api_key dans ChatResponse expose la clé Anthropic au frontend.\n"
        "Supprime le champ 'api_key: str = \"\"' de ChatResponse\n"
        "et retire 'api_key=os.getenv(...)' du constructeur ChatResponse(...)."
    )


def test_anthropic_key_not_retrieved_in_response():
    """os.getenv('ANTHROPIC_API_KEY') ne doit pas alimenter la réponse JSON."""
    source = _get_source()

    # Vérification spécifique : le getenv de la clé ne doit pas être dans
    # une instanciation de ChatResponse
    suspicious = (
        'api_key=os.getenv("ANTHROPIC_API_KEY"' in source
        or "api_key=os.getenv('ANTHROPIC_API_KEY'" in source
    )
    assert not suspicious, (
        "BUG ACTIF : la clé Anthropic est récupérée via os.getenv et injectée "
        "dans la réponse JSON.\n"
        "Retire 'api_key=os.getenv(\"ANTHROPIC_API_KEY\", \"\")' "
        "du constructeur ChatResponse(...)."
    )
