"""
Bug v1 -- Dataset 100% categorie "autres" (zero marketplace, zero equipements...).

Le test verifie que la distribution des categories dans le dataset genere
contient au moins 2 categories distinctes avec un minimum de paires chacune.

Contexte : si la fonction categorize() classe tout en "autres",
le modele FT ne verra jamais de questions sur la marketplace ou les equipements.
Il sera totalement muet sur ces sujets apres fine-tuning.

Lance apres avoir applique v1.patch pour voir l'echec.
Lance apres correction de categorize() pour voir le succes.
"""

import json
from collections import Counter
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATASET = BASE_DIR / "data" / "qa_dataset" / "concierge_qa.jsonl"


def categorize(pair: dict) -> str:
    """Reproduit la logique de categorize() depuis prepare_dataset.py (reload dynamique)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "prepare_dataset",
        BASE_DIR / "ateliers" / "atelier-04-finetuning" / "prepare_dataset.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.categorize(pair)


def load_dataset():
    if not DATASET.exists():
        pytest.skip(f"Dataset absent : {DATASET} -- lance d'abord prepare_dataset.py")
    with DATASET.open() as f:
        return [json.loads(line) for line in f if line.strip()]


class TestDatasetBalance:
    def test_at_least_two_distinct_categories(self):
        """Le dataset doit contenir au moins 2 categories distinctes."""
        pairs = load_dataset()
        cats = Counter(categorize(p) for p in pairs)
        n_categories = len(cats)
        assert n_categories >= 2, (
            f"Seulement {n_categories} categorie(s) : {dict(cats)}\n"
            "Le dataset est 100% dans une seule categorie -- catastrophe pour le fine-tuning.\n"
            "Le modele apprendrait uniquement cette categorie et serait muet sur toutes les autres.\n"
            "Corrige la fonction categorize() dans prepare_dataset.py."
        )

    def test_no_category_dominates_entirely(self):
        """Aucune categorie ne doit representer 100% du dataset."""
        pairs = load_dataset()
        cats = Counter(categorize(p) for p in pairs)
        total = sum(cats.values())
        for cat, count in cats.items():
            ratio = count / total
            assert ratio < 0.95, (
                f"La categorie '{cat}' represente {ratio:.1%} du dataset ({count}/{total} paires).\n"
                "Un dataset presque entierement dans une categorie = modele qui ne generalise pas.\n"
                "Fix : corriger categorize() pour que les mots-cles metier soient bien detectes."
            )

    def test_marketplace_category_present(self):
        """La categorie 'marketplace' doit etre representee (au moins 1 paire)."""
        pairs = load_dataset()
        cats = Counter(categorize(p) for p in pairs)
        marketplace_count = cats.get("marketplace", 0)
        assert marketplace_count >= 1, (
            f"Categorie 'marketplace' absente (0 paires).\n"
            "Les questions sur les producteurs locaux et artisans ne sont pas classifiees.\n"
            "Verifie que categorize() detecte bien les mots-cles : "
            "'producteur', 'artisan', 'plombier', 'legumes', 'marketplace', 'boulanger'."
        )
