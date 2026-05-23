"""
Test Bug v2 — max_tokens=50 (réponse tronquée)

Logique :
- Le bug introduit max_tokens=50 → les réponses sont coupées à ~200 caractères
- Ce test vérifie que la réponse dépasse 100 caractères
- Avec max_tokens=50 (bug actif) : réponse < 100 chars → test ECHOUE
- Avec max_tokens corrigé (≥ 256) : réponse ≥ 100 chars → test PASSE

Comment utiliser :
1. Applique le patch : git apply ateliers/atelier-01-llm-baseline/bugs/v2.patch
2. Lance : pytest ateliers/atelier-01-llm-baseline/bugs/test_v2.py -v  (doit ECHOUER)
3. Répare : dans solution.py, supprime max_tokens=50 (ou mets max_tokens=1024)
4. Relance : pytest (doit PASSER)

Note : nécessite ANTHROPIC_API_KEY ou Ollama.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from langchain_core.messages import HumanMessage

# Question qui devrait normalement recevoir une réponse longue (> 100 chars)
QUESTION_LONGUE = "Comment purger un radiateur ? Explique-moi les étapes en détail."
LONGUEUR_MINIMALE = 100  # caractères attendus dans une réponse complète


def test_reponse_non_tronquee():
    """
    La réponse à une question factuelle doit faire plus de 100 caractères.

    Ce test PASSE quand max_tokens est correct (≥ 256).
    Ce test ECHOUE quand max_tokens=50 (bug actif) car la réponse est tronquée.
    """
    from homebutler.llm.provider import get_llm
    llm = get_llm(temperature=0.1)

    response = llm.invoke([HumanMessage(content=QUESTION_LONGUE)])
    longueur = len(response.content)

    print(f"\nLongueur réponse : {longueur} caractères")
    print(f"Début de la réponse : {response.content[:150]}")

    assert longueur >= LONGUEUR_MINIMALE, (
        f"La réponse est trop courte ({longueur} chars < {LONGUEUR_MINIMALE} attendus).\n"
        f"Réponse obtenue : '{response.content}'\n"
        "Indice : vérifie la valeur de max_tokens dans les appels get_llm().\n"
        "max_tokens=50 produit des réponses systématiquement tronquées."
    )
