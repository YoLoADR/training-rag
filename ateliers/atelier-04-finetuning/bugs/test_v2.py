"""
Bug v2 -- LEARNING_RATE = 1e-2 dans prepare_dataset.py.

Analyse statique :
- Le bug ajoute LEARNING_RATE = 1e-2 en tete de prepare_dataset.py.
- En etat propre : LEARNING_RATE = 1e-2 ne doit PAS apparaitre.

Ce test PASSE en etat propre.
Ce test ECHOUE quand le bug est actif.
"""

import pathlib

PREPARE = pathlib.Path(__file__).parent.parent / "prepare_dataset.py"


def test_pas_de_learning_rate_trop_grand():
    """
    En etat de reference, LEARNING_RATE = 1e-2 ne doit pas apparaitre dans prepare_dataset.py.
    """
    source = PREPARE.read_text(encoding="utf-8")
    assert "LEARNING_RATE = 1e-2" not in source, (
        "LEARNING_RATE = 1e-2 trouve dans prepare_dataset.py. "
        "Ce learning rate est trop grand pour LoRA (provoque NaN). "
        "Indice : supprime ou corrige LEARNING_RATE (valeur correcte : 2e-4)."
    )
