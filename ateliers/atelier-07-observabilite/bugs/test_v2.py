"""
Test Bug v2 At.07 — `reference` absent du dataset RAGAS (→ context_recall NaN)

Logique :
- context_recall et context_precision (variantes "with reference") EXIGENT le champ
  `reference` (ground truth). S'il manque, RAGAS renvoie NaN pour ces métriques.
- Le bug fait que build_eval_dataset n'inclut PAS `reference` dans les SingleTurnSample.
- Test comportemental SANS LLM : on construit un dataset depuis un échantillon complet
  et on vérifie que `reference` est bien propagé.
- Bug actif : sample.reference is None → test ECHOUE.
- Corrigé : sample.reference == "..." → test PASSE.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))


def test_reference_propage_dans_dataset():
    from homebutler.eval.ragas_eval import build_eval_dataset

    sample = {
        "user_input": "Quelle est la durée du bail ?",
        "response": "3 ans.",
        "retrieved_contexts": ["Le bail est conclu pour 3 ans."],
        "reference": "3 ans pour un logement vide (loi de 1989).",
    }
    dataset = build_eval_dataset([sample])
    built = dataset.samples[0]
    print(f"\nreference dans le sample construit : {built.reference!r}")

    assert built.reference, (
        "Le champ `reference` (ground truth) est absent du dataset RAGAS.\n"
        "context_recall et context_precision renverront NaN sans lui.\n"
        "Indice : build_eval_dataset doit transmettre `reference` à SingleTurnSample."
    )
