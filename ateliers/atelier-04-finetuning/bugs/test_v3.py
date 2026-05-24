"""
Bug v3 -- n_val = 0 dans split_train_val_test() de prepare_dataset.py.

Analyse statique :
- Le bug change n_train = n et n_val = 0 (pas de split val/test).
- En etat propre : "n_val   = 0" ne doit PAS apparaitre dans prepare_dataset.py.

Ce test PASSE en etat propre.
Ce test ECHOUE quand le bug est actif.
"""

import pathlib

PREPARE = pathlib.Path(__file__).parent.parent / "prepare_dataset.py"


def test_n_val_non_nul():
    """
    En etat de reference, n_val = 0 ne doit pas apparaitre dans prepare_dataset.py.
    """
    source = PREPARE.read_text(encoding="utf-8")
    assert "n_val   = 0" not in source and "n_val = 0" not in source, (
        "n_val = 0 trouve dans prepare_dataset.py. "
        "Le split de validation est vide : le modele s'entraine sans supervision. "
        "Indice : corrige split_train_val_test() avec n_val = int(n * 0.1)."
    )
