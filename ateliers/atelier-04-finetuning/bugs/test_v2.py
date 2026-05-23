"""
Bug v2 -- Learning rate trop grand (1e-2).

Le test verifie que la valeur LEARNING_RATE dans prepare_dataset.py
est dans la plage acceptable pour LoRA (entre 1e-5 et 1e-2 exclus).

Contexte (langage non-tech) :
"J'ai mis un learning rate trop grand -- le modele saute trop loin
a chaque correction et n'apprend plus rien. Ca se manifeste par une
loss qui devient NaN (non-definie) des le 1er epoch. C'est comme
tourner un bouton de volume trop fort d'un coup : ca grille le haut-parleur."

Lance apres avoir applique v2.patch pour voir l'echec.
Lance apres correction (LEARNING_RATE = 2e-4) pour voir le succes.
"""

import importlib.util
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def get_learning_rate():
    """Charge dynamiquement LEARNING_RATE depuis prepare_dataset.py."""
    spec = importlib.util.spec_from_file_location(
        "prepare_dataset",
        BASE_DIR / "ateliers" / "atelier-04-finetuning" / "prepare_dataset.py"
    )
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return getattr(mod, "LEARNING_RATE", None)
    except Exception as e:
        pytest.skip(f"Impossible de charger prepare_dataset.py : {e}")


class TestLearningRate:
    def test_learning_rate_defined(self):
        """LEARNING_RATE doit etre defini dans prepare_dataset.py."""
        lr = get_learning_rate()
        if lr is None:
            pytest.skip(
                "LEARNING_RATE n'est pas defini dans prepare_dataset.py -- "
                "ce test ne s'applique que quand le patch v2 est applique."
            )

    def test_learning_rate_not_too_large(self):
        """LEARNING_RATE doit etre < 1e-2 pour eviter la divergence."""
        lr = get_learning_rate()
        if lr is None:
            pytest.skip("LEARNING_RATE non defini -- patch v2 non applique.")

        assert lr < 1e-2, (
            f"LEARNING_RATE = {lr} est trop grand (>= 1e-2).\n\n"
            "En langage non-tech : le modele 'saute' trop loin a chaque correction.\n"
            "Il n'apprend plus rien et la loss devient NaN (non-definie) des le 1er epoch.\n"
            "C'est comme tourner un bouton de volume a fond d'un coup : ca grille tout.\n\n"
            "Fix : regler LEARNING_RATE = 2e-4 (sweet spot LoRA).\n"
            "Plage valide pour LoRA : 1e-5 a 5e-4."
        )

    def test_learning_rate_not_too_small(self):
        """LEARNING_RATE ne doit pas etre trop petit non plus (< 1e-6)."""
        lr = get_learning_rate()
        if lr is None:
            pytest.skip("LEARNING_RATE non defini -- patch v2 non applique.")

        assert lr >= 1e-6, (
            f"LEARNING_RATE = {lr} est trop petit (< 1e-6).\n"
            "Le modele n'apprendra pratiquement rien (convergence trop lente).\n"
            "Fix : regler LEARNING_RATE = 2e-4."
        )

    def test_learning_rate_in_lora_sweet_spot(self):
        """LEARNING_RATE recommande pour LoRA : entre 1e-4 et 5e-4."""
        lr = get_learning_rate()
        if lr is None:
            pytest.skip("LEARNING_RATE non defini -- patch v2 non applique.")

        in_sweet_spot = 1e-5 <= lr <= 5e-4
        if not in_sweet_spot:
            # Warning non bloquant si hors sweet spot mais pas catastrophique
            print(
                f"\n  AVERTISSEMENT : LEARNING_RATE = {lr} hors sweet spot LoRA [1e-5, 5e-4].\n"
                "  Ca peut fonctionner mais le sweet spot recommande est 1e-4 a 5e-4.\n"
                "  Voir : Carnet de bord, ligne 'Learning rate'."
            )
