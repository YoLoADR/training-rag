"""
Test Bug v2 At.08 — multi-query qui ne demande qu'UNE reformulation

Logique :
- La diversité du MultiQueryRetriever vient du PROMPT (on demande N variantes),
  PAS de la température (un seul appel LLM génère toutes les variantes).
- Le bug réécrit MULTIQUERY_PROMPT pour ne demander qu'1 reformulation → plus
  aucune diversité de requêtes → le multi-query n'apporte rien.
- Test d'analyse statique (pas d'appel LLM, donc déterministe et sans réseau) :
  on vérifie que le prompt demande bien PLUSIEURS reformulations.
- Bug actif : prompt demande "1 reformulation" → test ECHOUE.
- Corrigé : prompt demande "3 reformulations" → test PASSE.

Comment utiliser :
1. git apply ateliers/atelier-08-optimisation/bugs/v2.patch
2. pytest ateliers/atelier-08-optimisation/bugs/test_v2.py -v   (doit ECHOUER)
3. Répare : redemande plusieurs reformulations (ex. 3) dans MULTIQUERY_PROMPT
4. pytest  (doit PASSER)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))


def _prompt_text() -> str:
    from homebutler.rag.reranking import MULTIQUERY_PROMPT
    # ChatPromptTemplate → on récupère le texte du template
    return MULTIQUERY_PROMPT.format(question="test").lower()


def test_multiquery_demande_plusieurs_reformulations():
    text = _prompt_text()
    print(f"\nPrompt multi-query :\n{text}\n")

    # On cible la CONSIGNE de génération ("génère N ...") pour ne pas confondre
    # avec "Une reformulation par ligne" qui décrit juste le format de sortie.
    asks_one = "génère 1 reformulation" in text
    asks_several = any(f"génère {n} reformulation" in text for n in ("2", "3", "4")) \
        or "génère plusieurs reformulation" in text

    assert asks_several and not asks_one, (
        "Le prompt multi-query ne demande pas plusieurs reformulations.\n"
        "La diversité vient de la CONSIGNE (demander N versions), pas de la température.\n"
        "Indice : MULTIQUERY_PROMPT doit demander 3 reformulations DIFFÉRENTES."
    )
