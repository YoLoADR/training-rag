"""
Checkpoint Final — Atelier 07 Observabilité & Évaluation
5 questions à RÉPONSE LIBRE notées par mots-clés (l'élève argumente).
Score >= 80% : prêt · 60-79% : ok · < 60% : Sprint.
"""

QUESTIONS = [
    {
        "question": (
            "En production, à quoi sert Langfuse AU-DELÀ du simple debug ? Cite au moins "
            "3 usages."
        ),
        "keywords": ["coût", "cout", "latence", "tokens", "dérive", "derive", "qualité",
                     "qualite", "alerte", "session", "replay", "p95"],
        "min_hits": 3,
        "explanation": (
            "Langfuse en prod : suivi des COÛTS (tokens/€), de la LATENCE (p50/p95), détection "
            "de DÉRIVE de qualité, ALERTES, replay de SESSIONS, scoring continu. C'est de "
            "l'observabilité produit, pas seulement du debug ponctuel."
        ),
    },
    {
        "question": (
            "Quelles métriques RAGAS exigent une réponse de référence (ground truth) et "
            "lesquelles non ? Pourquoi ?"
        ),
        "keywords": ["context_recall", "context_precision", "reference", "référence",
                     "faithfulness", "answer_relevancy", "relevanc"],
        "min_hits": 3,
        "explanation": (
            "context_recall et context_precision (with reference) EXIGENT `reference` (elles "
            "comparent les contextes à la vérité terrain). faithfulness (ancrage dans les "
            "contextes) et answer_relevancy (pertinence vs question) n'en ont PAS besoin."
        ),
    },
    {
        "question": (
            "Pourquoi un LLM-as-judge doit-il être déterministe, et comment l'obtient-on ?"
        ),
        "keywords": ["temperature", "température", "0", "déterministe", "deterministe",
                     "reproductib", "même score", "meme score", "variance"],
        "min_hits": 2,
        "explanation": (
            "Un juge non déterministe (temperature>0) donne des scores variables d'un run à "
            "l'autre → évaluation non reproductible, impossible de suivre une dérive. On met "
            "temperature=0 (et éventuellement on moyenne plusieurs notations)."
        ),
    },
    {
        "question": (
            "Que mesure 'faithfulness' et en quoi diffère-t-elle de 'answer_relevancy' ?"
        ),
        "keywords": ["ancr", "contexte", "context", "invent", "halluc", "supporté", "supporte",
                     "répond", "repond", "question", "pertinence"],
        "min_hits": 2,
        "explanation": (
            "faithfulness = la réponse est-elle ANCRÉE dans les contextes (ne pas inventer "
            "au-delà) ? answer_relevancy = la réponse RÉPOND-elle vraiment à la question ? "
            "Une réponse peut être fidèle mais hors-sujet, ou pertinente mais inventée."
        ),
    },
    {
        "question": (
            "Quelle est la différence entre tracing (observabilité) et évaluation, et "
            "pourquoi les combiner ?"
        ),
        "keywords": ["trace", "tracing", "observ", "latence", "coût", "cout", "qualité",
                     "qualite", "évalu", "evalu", "score", "métrique", "metrique", "continu"],
        "min_hits": 3,
        "explanation": (
            "Tracing = QUE s'est-il passé (latence, tokens, coût, étapes). Évaluation = est-ce "
            "BON (qualité mesurée). Combinés : on TRACE chaque appel ET on attache un SCORE "
            "(judge/RAGAS) à la trace → suivi continu de la qualité en production."
        ),
    },
]


def run_quiz() -> None:
    print("\n" + "=" * 60)
    print("CHECKPOINT FINAL — Atelier 07 : Observabilité & Évaluation")
    print("=" * 60)
    print("5 questions à réponse libre (notées par mots-clés).\n")

    score = 0
    details = []
    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n[{i}/5] {q['question']}")
        answer = input("\nTa réponse : ").strip().lower()
        hits = sum(1 for kw in q["keywords"] if kw.lower() in answer)
        ok = hits >= q["min_hits"]
        if ok:
            print(f"   VALIDÉ ({hits} mots-clés trouvés)")
            score += 1
        else:
            print(f"   INSUFFISANT ({hits}/{q['min_hits']} mots-clés attendus)")
        details.append((i, ok, q["explanation"]))

    pct = round(100 * score / len(QUESTIONS))
    print("\n" + "=" * 60)
    print(f"SCORE FINAL : {score}/{len(QUESTIONS)} ({pct}%)")
    print("=" * 60)
    print("\nExplications :")
    for num, ok, expl in details:
        print(f"\n[{num}] {'OK' if ok else 'RATÉ'} — {expl}")

    print("\n" + "=" * 60)
    if pct >= 80:
        print(f"=> PRÊT ({pct}%) — pars en Bonus 🏆 (Langfuse self-host, RAGAS sur 20 Q, PII scrubbing).")
    elif pct >= 60:
        print(f"=> OK ({pct}%) — relis les 1-2 concepts ratés puis Bonus.")
    else:
        print(f"=> SPRINT ({pct}%) — reprends tracing vs éval, métriques RAGAS, juge déterministe.")
        import sys
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    run_quiz()
