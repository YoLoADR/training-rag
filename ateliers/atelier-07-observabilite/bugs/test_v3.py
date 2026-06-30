"""
Test Bug v3 At.07 — LLM-as-judge non déterministe (temperature > 0)

Logique :
- Un juge doit être DÉTERMINISTE (temperature=0) : sinon les scores fluctuent d'un run
  à l'autre et l'évaluation n'est pas reproductible.
- Le bug met temperature=1.0 dans llm_as_judge.
- Test d'analyse statique (déterministe) : le juge instancie le LLM à temperature=0.
- Bug actif : temperature=1.0 → test ECHOUE.
- Corrigé : temperature=0 → test PASSE.
"""

import inspect
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))


def test_judge_deterministe():
    import homebutler.eval.judge as judge
    src = inspect.getsource(judge.llm_as_judge).replace(" ", "")
    print(f"\nSource llm_as_judge (compacte) :\n{src}")
    assert "get_llm(temperature=0)" in src, (
        "Le LLM-as-judge n'est pas déterministe.\n"
        "Un juge avec temperature > 0 produit des scores non reproductibles.\n"
        "Indice : instancie le juge avec get_llm(temperature=0)."
    )
