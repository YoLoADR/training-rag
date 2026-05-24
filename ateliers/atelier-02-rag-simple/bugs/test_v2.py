"""
Test Bug v2 At.02 — chunk_overlap=0 dans solution.py

Analyse statique :
- Le bug remplace chunk_overlap=50 par chunk_overlap=0.
- En etat propre : chunk_overlap=0 ne doit PAS apparaitre dans solution.py.

Ce test PASSE en etat propre.
Ce test ECHOUE quand le bug est actif.
"""

import pathlib

SOLUTION = pathlib.Path(__file__).parent.parent / "solution.py"


def test_pas_de_chunk_overlap_0():
    """
    En etat de reference, chunk_overlap=0 ne doit pas apparaitre dans solution.py.
    """
    source = SOLUTION.read_text(encoding="utf-8")
    assert "chunk_overlap=0" not in source, (
        "chunk_overlap=0 trouve dans solution.py. "
        "Indice : remplace chunk_overlap=0 par chunk_overlap=50 dans les appels "
        "chunk_fixed_size() et chunk_recursive()."
    )
