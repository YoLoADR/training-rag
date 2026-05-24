"""
Bug v2 — CORS wildcard (*) dans api/main.py (analyse statique).

Le bug : allow_origins=["*"] autorise n'importe quel domaine à appeler l'API,
ce qui est dangereux en production (CSRF, data exfiltration).

Applique le patch : git apply ateliers/atelier-05-deploiement/bugs/v2.patch
Lance ensuite   : pytest ateliers/atelier-05-deploiement/bugs/test_v2.py -v

Le test ECHOUE si allow_origins=["*"] est présent.
Le test PASSE quand les origines sont restreintes à une liste explicite.

Pas d'appel réseau — analyse statique de api/main.py.
"""

import pathlib


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent
MAIN_PY = BASE_DIR / "api" / "main.py"


def _get_source() -> str:
    return MAIN_PY.read_text(encoding="utf-8")


def test_cors_not_wildcard():
    """allow_origins ne doit pas être ['*'] dans api/main.py."""
    source = _get_source()

    assert 'allow_origins=["*"]' not in source, (
        "BUG ACTIF : 'allow_origins=[\"*\"]' trouvé dans api/main.py.\n"
        "Un CORS wildcard autorise tous les domaines — dangereux en production.\n"
        "Remplace par une liste explicite :\n"
        '  allow_origins=["http://localhost:8501", "http://localhost:3000"]'
    )


def test_cors_has_explicit_origins():
    """allow_origins doit contenir au moins une origine explicite (localhost)."""
    source = _get_source()

    has_explicit = (
        "http://localhost:8501" in source
        or "http://localhost:3000" in source
    )
    assert has_explicit, (
        "Aucune origine localhost explicite trouvée dans api/main.py.\n"
        "Ajoute au moins 'http://localhost:8501' ou 'http://localhost:3000' "
        "dans allow_origins du CORSMiddleware."
    )
