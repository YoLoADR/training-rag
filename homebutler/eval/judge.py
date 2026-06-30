"""
LLM-as-judge déterministe (Atelier 07).

Un LLM note la qualité d'une réponse RAG sur une échelle 1-5, renvoyée normalisée
en [0,1]. Point CRUCIAL : le juge doit être DÉTERMINISTE (temperature=0). Avec une
température > 0, les scores fluctuent d'un run à l'autre → évaluation non reproductible.
"""

import re

from homebutler.llm.provider import get_llm

JUDGE_PROMPT = """Tu es un évaluateur RAG rigoureux et IMPARTIAL.
On te donne une QUESTION, le CONTEXTE récupéré, et la RÉPONSE produite.
Note la qualité GLOBALE de la réponse sur une échelle de 1 à 5 :
  5 = répond exactement, ancrée dans le contexte, sans rien inventer
  3 = partiellement correcte ou incomplète
  1 = hors-sujet ou inventée (non supportée par le contexte)
Réponds par UN SEUL chiffre entre 1 et 5, rien d'autre.

QUESTION :
{question}

CONTEXTE :
{context}

RÉPONSE :
{answer}

Note (1-5) :"""


def _parse_score(text: str) -> float:
    """Extrait un entier 1-5 et le normalise en [0,1]. 0.0 si illisible."""
    m = re.search(r"[1-5]", text)
    if not m:
        return 0.0
    return (int(m.group(0)) - 1) / 4.0  # 1→0.0 ... 5→1.0


def llm_as_judge(question: str, answer: str, contexts) -> float:
    """Note la réponse via un LLM juge déterministe. Retourne un score dans [0,1].

    `contexts` : liste de chaînes (chunks récupérés) ou une chaîne déjà formatée.
    """
    context = "\n\n".join(contexts) if isinstance(contexts, (list, tuple)) else str(contexts)
    judge = get_llm(temperature=0)  # DÉTERMINISTE — ne jamais mettre temperature > 0 ici
    prompt = JUDGE_PROMPT.format(question=question, context=context, answer=answer)
    resp = judge.invoke(prompt)
    text = resp.content if hasattr(resp, "content") else str(resp)
    return _parse_score(text)
