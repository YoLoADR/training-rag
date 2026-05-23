"""
Bug v2 — Test : le header CORS ne doit pas être wildcard (*).

Applique d'abord le patch : git apply ateliers/atelier-05-deploiement/bugs/v2.patch
Lance ensuite : pytest ateliers/atelier-05-deploiement/bugs/test_v2.py -v

Le test ECHOUE si CORS=* (bug actif).
Le test PASSE quand tu as restreint les origines à une liste explicite.

Pré-requis : API démarrée sur localhost:8000
"""

import subprocess


def test_cors_not_wildcard():
    """Le header Access-Control-Allow-Origin ne doit pas valoir '*' en prod."""
    result = subprocess.run(
        [
            "curl", "-s", "-I",
            "-H", "Origin: https://evil-site.example.com",
            "http://localhost:8000/health",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    headers = result.stdout.lower()

    # Cherche le header CORS dans la réponse preflight ou simple
    cors_wildcard = "access-control-allow-origin: *" in headers
    assert not cors_wildcard, (
        "BUG ACTIF : le header 'Access-Control-Allow-Origin: *' est présent. "
        "Restreins allow_origins dans api/main.py à une liste explicite "
        "ex: ['http://localhost:8501', 'http://localhost:3000']"
    )
