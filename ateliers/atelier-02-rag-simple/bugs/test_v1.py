"""
Test Bug v1 At.02 — chunk_size=2000 dans solution.py

Analyse statique :
- Le bug remplace chunk_size=512 par chunk_size=2000.
- En etat propre : chunk_size=2000 ne doit PAS apparaitre dans solution.py.

Ce test PASSE en etat propre.
Ce test ECHOUE quand le bug est actif.
"""

import pathlib

SOLUTION = pathlib.Path(__file__).parent.parent / "solution.py"


def test_pas_de_chunk_size_2000():
    """
    En etat de reference, chunk_size=2000 ne doit pas apparaitre dans solution.py.
    """
    source = SOLUTION.read_text(encoding="utf-8")
    assert "chunk_size=2000" not in source, (
        "chunk_size=2000 trouve dans solution.py. "
        "Indice : remplace chunk_size=2000 par chunk_size=512 dans les appels "
        "chunk_fixed_size() et chunk_recursive()."
    )
