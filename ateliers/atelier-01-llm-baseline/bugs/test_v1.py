"""
Test Bug v1 — Temperature trop haute (T=0.9) dans run_1

Analyse statique de solution.py :
- En etat propre : get_llm(temperature=0.1 dans run_1 -> le pattern
  get_llm(temperature=0.9 ne doit apparaitre qu UNE seule fois (dans run_2).
- Avec le bug actif : get_llm(temperature=0.9 apparait 2 fois.

Ce test PASSE en etat propre.
Ce test ECHOUE quand le bug est actif (run_1 utilise temperature=0.9).
"""

import pathlib

SOLUTION = pathlib.Path(__file__).parent.parent / "solution.py"


def test_run_1_temperature_correcte():
    """
    En etat de reference, get_llm(temperature=0.9 n apparait qu une seule fois
    (dans run_2). Si le bug est actif, il apparait 2 fois.
    """
    source = SOLUTION.read_text(encoding="utf-8")
    occurrences = source.count("get_llm(temperature=0.9")
    assert occurrences <= 1, (
        f"get_llm(temperature=0.9 apparait {occurrences} fois dans solution.py "
        f"(attendu <= 1). "
        "Indice : run_1 doit utiliser temperature=0.1, pas 0.9."
    )
