"""
Test Bug v3 — Pas de system prompt (modèle off-topic / non cadré)

Logique :
- Le bug supprime le system prompt → le LLM n'est plus cadré dans son rôle
- Sans system prompt, sur une question privée, le LLM invente librement
  (ou répond en mode "assistant généraliste" sans se limiter à HomeButler)
- Avec system prompt correct : le LLM répond poliment qu'il n'a pas accès
  aux données privées → la réponse contient "je n'ai pas" ou "n'ai pas accès"
  ou "je ne dispose pas" ou "je ne suis pas en mesure"

Ce test vérifie que la réponse avec system prompt contient un refus poli.
- Avec system prompt (correct) : réponse = refus poli → PASSE
- Sans system prompt (bug actif) : réponse = hallucination ou hors-rôle → ECHOUE

Comment utiliser :
1. Applique le patch : git apply ateliers/atelier-01-llm-baseline/bugs/v3.patch
2. Lance : pytest ateliers/atelier-01-llm-baseline/bugs/test_v3.py -v  (doit ECHOUER)
3. Répare : ajoute le SystemMessage dans les appels llm.invoke()
4. Relance : pytest (doit PASSER)

Note : nécessite ANTHROPIC_API_KEY ou Ollama.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from langchain_core.messages import HumanMessage, SystemMessage

SYSTEM_PROMPT = (
    "Tu es un assistant maison HomeButler. "
    "Tu aides les locataires avec leurs questions sur leur logement. "
    "Si tu ne disposes pas des informations privées du logement, "
    "réponds poliment que tu n'as pas accès à ces données."
)

QUESTION_PRIVEE = "Quelle est la marque exacte de ma chaudière personnelle ?"

# Mots-clés attendus dans un refus poli cadré (présence de l'un suffit)
MOTS_REFUS_POLIS = [
    "n'ai pas accès",
    "ne dispose pas",
    "je ne sais pas",
    "n'ai pas d'accès",
    "pas accès",
    "informations privées",
    "données personnelles",
    "ne peux pas savoir",
    "je ne suis pas en mesure",
    "je n'ai pas les informations",
    "mes données ne contiennent pas",
]


def test_system_prompt_cadre_le_refus():
    """
    Avec un system prompt HomeButler correctement configuré, la réponse
    à une question sur les données privées du logement doit contenir
    un refus poli explicite.

    Ce test PASSE quand le system prompt est présent (bug réparé).
    Ce test ECHOUE quand le system prompt est absent (bug actif).
    """
    from homebutler.llm.provider import get_llm
    llm = get_llm(temperature=0.1)

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=QUESTION_PRIVEE),
    ])

    reponse_lower = response.content.lower()
    print(f"\nRéponse obtenue : {response.content[:300]}")

    refus_detecte = any(mot in reponse_lower for mot in MOTS_REFUS_POLIS)

    assert refus_detecte, (
        f"Le LLM ne refuse pas poliment la question privée.\n"
        f"Réponse : '{response.content[:200]}'\n"
        f"Attendu : l'un de ces mots-clés : {MOTS_REFUS_POLIS[:5]}\n"
        "Indice : vérifie que le SystemMessage avec SYSTEM_PROMPT est bien inclus\n"
        "dans l'appel llm.invoke([SystemMessage(...), HumanMessage(...)])."
    )
