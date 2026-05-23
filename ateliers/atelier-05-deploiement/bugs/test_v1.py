"""
Bug v1 — Test : clé API ne doit pas apparaître dans la réponse /chat.

Applique d'abord le patch : git apply ateliers/atelier-05-deploiement/bugs/v1.patch
Lance ensuite : pytest ateliers/atelier-05-deploiement/bugs/test_v1.py -v

Le test ECHOUE si le bug est actif (la clé fuit).
Le test PASSE quand tu as réparé le bug.

Pré-requis : API démarrée sur localhost:8000
"""

import json
import subprocess
import sys


def test_api_key_not_in_response():
    """La réponse JSON de /chat ne doit pas contenir de clé Anthropic."""
    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST", "http://localhost:8000/chat",
            "-H", "Content-Type: application/json",
            "-d", '{"message": "Bonjour", "mode": "llm_only"}',
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    try:
        body = json.loads(result.stdout)
    except json.JSONDecodeError:
        sys.exit(f"Réponse non JSON : {result.stdout[:200]}")

    # Le champ api_key ne doit pas exister
    assert "api_key" not in body, (
        f"BUG ACTIF : le champ 'api_key' est présent dans la réponse JSON : {list(body.keys())}"
    )

    # Aucune valeur ne doit ressembler à une clé Anthropic
    body_str = json.dumps(body)
    assert "sk-ant" not in body_str, (
        "BUG ACTIF : la valeur de la clé Anthropic (sk-ant...) apparaît dans la réponse !"
    )
    assert "ANTHROPIC" not in body_str.upper() or "provider" in body_str.lower(), (
        "BUG ACTIF : la chaîne ANTHROPIC apparaît dans la réponse de façon suspecte."
    )
