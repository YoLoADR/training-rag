"""
Test Bug v2 — max_tokens=50 dans solution.py

Analyse statique de solution.py :
- Le bug introduit max_tokens=50 dans les deux appels get_llm().
- En etat propre : max_tokens=50 ne doit PAS apparaitre dans solution.py.

Ce test PASSE en etat propre (pas de max_tokens=50).
Ce test ECHOUE quand le bug est actif.
"""

import pathlib

SOLUTION = pathlib.Path(__file__).parent.parent / "solution.py"


def test_pas_de_max_tokens_50():
    """
    En etat de reference, max_tokens=50 ne doit pas apparaitre dans solution.py.
    """
    source = SOLUTION.read_text(encoding="utf-8")
    assert "max_tokens=50" not in source, (
        "max_tokens=50 trouve dans solution.py. "
        "Indice : supprime le parametre max_tokens=50 des appels get_llm()."
    )
