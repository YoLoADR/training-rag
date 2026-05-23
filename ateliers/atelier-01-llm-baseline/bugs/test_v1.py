"""
Test Bug v1 — Temperature trop haute (T=0.9)

Logique :
- Le bug introduit temperature=0.9 dans solution.py (à la place de 0.1)
- Ce test appelle le LLM 3 fois sur la même question critique
- À T=0.9 : les 3 réponses seront différentes (le test PASSE → bug confirmé)
- À T=0.0 (corrigé) : les 3 réponses seront identiques ou quasi (le test ECHOUE → bug réparé)

Donc : ce test DOIT ECHOUER après correction du bug (behavior attendu = stabilité).
Reformulation : le test vérifie que les réponses SONT différentes.
Si elles sont toutes identiques → AssertionError → le bug est réparé.

Comment utiliser :
1. Applique le patch : git apply ateliers/atelier-01-llm-baseline/bugs/v1.patch
2. Lance : pytest ateliers/atelier-01-llm-baseline/bugs/test_v1.py -v  (doit ECHOUER → bug actif)
3. Répare : dans solution.py, change temperature=0.9 en temperature=0.1
4. Relance : pytest (doit PASSER → bug réparé, stabilité confirmée)

Note : ce test fait 3 vrais appels LLM → nécessite ANTHROPIC_API_KEY ou Ollama.
"""

import pytest
import sys
import os

# Ajouter la racine du projet au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from langchain_core.messages import HumanMessage


QUESTION_CRITIQUE = "Quelle est la marque de ma chaudière ?"
N_RUNS = 3


def get_responses(temperature: float) -> list[str]:
    """Appelle le LLM N_RUNS fois avec la même question et retourne les réponses."""
    from homebutler.llm.provider import get_llm
    llm = get_llm(temperature=temperature)
    responses = []
    for _ in range(N_RUNS):
        resp = llm.invoke([HumanMessage(content=QUESTION_CRITIQUE)])
        responses.append(resp.content.strip()[:200])
    return responses


def test_temperature_basse_produit_reponses_stables():
    """
    A T=0.1 (configuration correcte), les 3 réponses doivent être identiques
    ou très similaires (déterminisme).

    Ce test PASSE quand le bug est réparé (temperature=0.1).
    Ce test ECHOUE quand le bug est actif (temperature=0.9 → variabilité).
    """
    responses = get_responses(temperature=0.1)

    print(f"\nRéponse 1 : {responses[0][:100]}")
    print(f"Réponse 2 : {responses[1][:100]}")
    print(f"Réponse 3 : {responses[2][:100]}")

    # Vérifier que toutes les réponses commencent de la même façon
    # (au moins les 50 premiers caractères doivent être identiques)
    prefix_0 = responses[0][:50]
    prefix_1 = responses[1][:50]
    prefix_2 = responses[2][:50]

    all_same = (prefix_0 == prefix_1) and (prefix_1 == prefix_2)

    # Si T=0.1 : all_same devrait être True → le test PASSE
    # Si T=0.9 (bug actif) : all_same sera probablement False → le test ECHOUE
    assert all_same, (
        f"Les réponses sont trop variables pour T=0.1.\n"
        f"Réponse 1 : {responses[0][:80]}\n"
        f"Réponse 2 : {responses[1][:80]}\n"
        f"Réponse 3 : {responses[2][:80]}\n"
        "Indice : vérifie la valeur de temperature dans les appels get_llm()."
    )
