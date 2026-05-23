"""
Bug v3 -- Absence de validation split (100/0/0 au lieu de 80/10/10).

Le test verifie que :
  1. Le fichier val.jsonl est bien cree apres prepare_dataset.py
  2. Le fichier val.jsonl n'est pas vide
  3. Le fichier test.jsonl n'est pas vide non plus

Contexte (langage non-tech) :
"J'ai omis le fichier de validation -- le modele s'entraine sans qu'on
surveille s'il apprend par coeur ou s'il generalise. On decouvre l'overfitting
seulement au test final, quand il est trop tard. C'est comme passer un examen
sans jamais faire de controles blancs."

Lance : python ateliers/atelier-04-finetuning/prepare_dataset.py
Puis  : pytest ateliers/atelier-04-finetuning/bugs/test_v3.py -v
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATASET_DIR = BASE_DIR / "data" / "qa_dataset"
VAL_FILE = DATASET_DIR / "concierge_qa_val.jsonl"
TEST_FILE = DATASET_DIR / "concierge_qa_test.jsonl"
TRAIN_FILE = DATASET_DIR / "concierge_qa_train.jsonl"
PREPARE_SCRIPT = BASE_DIR / "ateliers" / "atelier-04-finetuning" / "prepare_dataset.py"


def run_prepare_dataset():
    """Execute prepare_dataset.py pour generer les splits."""
    result = subprocess.run(
        [sys.executable, str(PREPARE_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    return result


class TestValidationSplit:
    @pytest.fixture(autouse=True)
    def generate_splits(self):
        """Genere les splits avant chaque test."""
        run_prepare_dataset()

    def test_val_file_exists(self):
        """Le fichier val.jsonl doit exister apres prepare_dataset.py."""
        assert VAL_FILE.exists(), (
            f"Fichier absent : {VAL_FILE}\n\n"
            "En langage non-tech : le set de validation n'a pas ete cree.\n"
            "Sans validation, le modele s'entraine 'en aveugle' -- on ne detecte pas\n"
            "l'overfitting (apprentissage par coeur) avant qu'il soit trop tard.\n\n"
            "Corrige split_train_val_test() : n_val = int(n * 0.1)"
        )

    def test_val_file_not_empty(self):
        """Le fichier val.jsonl doit contenir au moins 5 paires."""
        if not VAL_FILE.exists():
            pytest.fail(f"Fichier absent : {VAL_FILE}")

        with VAL_FILE.open() as f:
            pairs = [json.loads(line) for line in f if line.strip()]

        assert len(pairs) >= 5, (
            f"val.jsonl contient {len(pairs)} paire(s) (minimum attendu : 5).\n\n"
            "En langage non-tech : le controle blanc est trop court pour etre significatif.\n"
            "Avec 150 paires et un split 80/10/10, on attend ~15 paires en validation.\n\n"
            "Corrige split_train_val_test() : n_val = int(n * 0.1)"
        )

    def test_test_file_not_empty(self):
        """Le fichier test.jsonl doit contenir au moins 5 paires."""
        if not TEST_FILE.exists():
            pytest.fail(f"Fichier absent : {TEST_FILE}")

        with TEST_FILE.open() as f:
            pairs = [json.loads(line) for line in f if line.strip()]

        assert len(pairs) >= 5, (
            f"test.jsonl contient {len(pairs)} paire(s) (minimum attendu : 5).\n"
            "Le set de test (jamais vu pendant le training) doit etre non vide."
        )

    def test_train_val_test_sizes_coherent(self):
        """Les tailles de train/val/test doivent etre coherentes (proche 80/10/10)."""
        if not all(f.exists() for f in [TRAIN_FILE, VAL_FILE, TEST_FILE]):
            pytest.skip("Fichiers split absents.")

        def count_lines(path):
            with path.open() as f:
                return sum(1 for line in f if line.strip())

        n_train = count_lines(TRAIN_FILE)
        n_val = count_lines(VAL_FILE)
        n_test = count_lines(TEST_FILE)
        total = n_train + n_val + n_test

        if total == 0:
            pytest.fail("Aucune paire dans les fichiers split.")

        val_ratio = n_val / total
        assert val_ratio >= 0.05, (
            f"val ratio = {val_ratio:.1%} ({n_val}/{total}) -- trop faible.\n"
            "Le split attendu est 80/10/10 : le val set doit representer au moins 5% du total.\n"
            "Corrige : n_val = int(n * 0.1)"
        )
