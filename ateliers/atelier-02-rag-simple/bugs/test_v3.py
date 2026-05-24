"""
Test Bug v3 At.02 — force_rebuild=True dans la boucle de requetes

Analyse statique :
- Le bug ajoute build_faiss_index(force_rebuild=True) dans la boucle Recall@k.
- En etat propre : force_rebuild=True n'apparait qu'UNE seule fois dans solution.py
  (hors boucle, pour la construction initiale de l'index).
- Avec le bug : force_rebuild=True apparait 2 fois.

Ce test PASSE en etat propre (1 seule occurrence).
Ce test ECHOUE quand le bug est actif (2 occurrences).
"""

import pathlib

SOLUTION = pathlib.Path(__file__).parent.parent / "solution.py"


def test_force_rebuild_hors_boucle():
    """
    En etat de reference, force_rebuild=True n'apparait qu'une seule fois
    dans solution.py (construction initiale hors boucle).
    """
    source = SOLUTION.read_text(encoding="utf-8")
    occurrences = source.count("force_rebuild=True")
    assert occurrences <= 1, (
        f"force_rebuild=True apparait {occurrences} fois dans solution.py "
        f"(attendu <= 1). "
        "Indice : l'index doit etre construit UNE SEULE FOIS avant la boucle Recall@k, "
        "pas a chaque iteration."
    )
