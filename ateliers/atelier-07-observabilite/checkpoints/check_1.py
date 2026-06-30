"""
Checkpoint 1 — Atelier 07 Observabilité & Évaluation
QCM 3 questions : tracing vs évaluation, métriques RAGAS, juge déterministe.
Passe/fail binaire (score >= 2/3).
"""

QUESTIONS = [
    {
        "question": "Quelle est la différence entre OBSERVABILITÉ (tracing) et ÉVALUATION ?",
        "options": {
            "A": "Ce sont deux mots pour la même chose",
            "B": (
                "L'observabilité TRACE ce qui se passe (prompt, latence, tokens, coût) pour "
                "debugger/superviser ; l'évaluation NOTE la QUALITÉ des réponses (faithfulness, "
                "pertinence) selon des métriques"
            ),
            "C": "L'observabilité sert en dev, l'évaluation est interdite en prod",
            "D": "L'évaluation remplace l'observabilité",
        },
        "correct": "B",
        "explication": (
            "Tracing (Langfuse) = QUE s'est-il passé (visibilité ops : latence, tokens, coût, "
            "étapes). Évaluation (RAGAS/judge) = est-ce BON (qualité mesurée). Les deux sont "
            "complémentaires : on trace en continu, et on note la qualité régulièrement."
        ),
    },
    {
        "question": "Pourquoi context_recall renvoie-t-il NaN si `reference` est absent ?",
        "options": {
            "A": "Parce que RAGAS a besoin d'une clé OpenAI pour cette métrique",
            "B": "Parce que context_recall est une métrique de latence",
            "C": (
                "Parce que context_recall (variante with-reference) COMPARE les contextes "
                "récupérés à la réponse de référence : sans référence, rien à comparer → NaN"
            ),
            "D": "Parce que le dataset est trop petit",
        },
        "correct": "C",
        "explication": (
            "context_recall et context_precision (with reference) exigent `reference` (ground "
            "truth). faithfulness et answer_relevancy, non. Dans notre dataset, reference vient "
            "du champ `output` (mapping input→user_input, output→reference)."
        ),
    },
    {
        "question": "Pourquoi le LLM-as-judge doit-il être à temperature=0 ?",
        "options": {
            "A": "Pour qu'il réponde plus vite",
            "B": (
                "Pour qu'il soit DÉTERMINISTE : la même (question, réponse) doit recevoir le "
                "même score, sinon l'évaluation n'est pas reproductible dans le temps"
            ),
            "C": "Pour économiser des tokens",
            "D": "Parce que RAGAS l'impose techniquement",
        },
        "correct": "B",
        "explication": (
            "Un juge à température élevée échantillonne : le score fluctue d'un run à l'autre. "
            "temperature=0 → déterminisme → on peut comparer deux exécutions et suivre une "
            "dérive de qualité. La température contrôle l'aléa, pas la compétence."
        ),
    },
]

SCORE_MIN = 2


def run_quiz() -> None:
    print("\n" + "=" * 60)
    print("CHECKPOINT 1 — Atelier 07 : Observabilité & Évaluation")
    print("=" * 60)
    print(f"3 questions — score minimum pour valider : {SCORE_MIN}/3\n")

    score = 0
    details = []
    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n[{i}/3] {q['question']}")
        for lettre, texte in q["options"].items():
            print(f"   {lettre}) {texte}")
        reponse = input("\nTa réponse (A/B/C/D) : ").strip().upper()
        if reponse == q["correct"]:
            print("   CORRECT ✓")
            score += 1
            details.append((i, True, q["explication"]))
        else:
            print(f"   INCORRECT. Bonne réponse : {q['correct']}")
            details.append((i, False, q["explication"]))

    print("\n" + "=" * 60)
    print(f"SCORE : {score}/3")
    print("=" * 60)
    print("\nExplications :")
    for num, correct, explication in details:
        statut = "OK" if correct else "RATÉ"
        print(f"\n[{num}] {statut} — {explication}")

    if score >= SCORE_MIN:
        print(f"\nRESULTAT : VALIDE ({score}/3 >= {SCORE_MIN}/3)")
        print("=> Continue vers l'Étape 2 (RAGAS + scoring des traces).")
    else:
        print(f"\nRESULTAT : A RENFORCER ({score}/3 < {SCORE_MIN}/3)")
        print("=> Relis le Carnet de bord (tracing vs éval, métriques RAGAS, juge déterministe).")


if __name__ == "__main__":
    run_quiz()
