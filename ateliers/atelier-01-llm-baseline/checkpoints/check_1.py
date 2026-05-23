"""
Checkpoint 1 — Atelier 01 LLM Baseline
QCM 3 questions sur LLM, temperature et token.
Passe/fail binaire (score ≥ 2/3).
"""

QUESTIONS = [
    {
        "question": "Qu'est-ce qu'une hallucination LLM ?",
        "options": {
            "A": "Un bug du code Python qui fait planter le script",
            "B": "Une réponse fausse mais plausible produite par le LLM faute d'informations réelles",
            "C": "Une erreur réseau lors de l'appel à l'API Anthropic",
            "D": "Un token généré deux fois consécutivement",
        },
        "correct": "B",
        "explication": (
            "Un LLM prédit statistiquement le prochain token sans vérifier la vérité factuelle. "
            "Sur des données privées inconnues, il 'invente' une réponse plausible — c'est l'hallucination."
        ),
    },
    {
        "question": "À temperature=0, que se passe-t-il si on pose la même question 3 fois au même LLM ?",
        "options": {
            "A": "Les 3 réponses sont toujours différentes car le LLM est aléatoire par nature",
            "B": "Les 3 réponses sont identiques ou quasi-identiques (déterminisme)",
            "C": "Le LLM refuse de répondre après la première fois (rate limit)",
            "D": "La latence augmente exponentiellement",
        },
        "correct": "B",
        "explication": (
            "À temperature=0, le LLM sélectionne toujours le token le plus probable — "
            "le résultat est déterministe et reproductible. "
            "C'est la configuration recommandée pour les tests et les assistants factuels."
        ),
    },
    {
        "question": "Qu'est-ce qu'un token dans le contexte d'un LLM ?",
        "options": {
            "A": "Un mot complet (la phrase 'Je vais bien' = 3 tokens)",
            "B": "Une clé API secrète pour s'authentifier",
            "C": "Une unité de texte d'environ 3-4 caractères — la 'syllabe' du modèle",
            "D": "Un identifiant unique pour chaque requête",
        },
        "correct": "C",
        "explication": (
            "Un token ≈ 4 caractères en anglais, ≈ 3-4 en français. "
            "'chaudière' ≈ 3 tokens. Le coût API est facturé en tokens (input + output). "
            "max_tokens = nombre maximum de tokens en sortie."
        ),
    },
]

SCORE_MIN = 2  # score minimum pour valider


def run_quiz() -> None:
    print("\n" + "=" * 60)
    print("CHECKPOINT 1 — Atelier 01 : LLM, temperature, token")
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
            print(f"   CORRECT ✓")
            score += 1
            details.append((i, True, q["explication"]))
        else:
            print(f"   INCORRECT. La bonne réponse était : {q['correct']}")
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
        print("=> Continue vers l'Etape 2 du Tronc Commun.")
    else:
        print(f"\nRESULTAT : A RENFORCER ({score}/3 < {SCORE_MIN}/3)")
        print("=> Relis le Carnet de bord (LLM, hallucination, temperature, token)")
        print("=> Puis relance ce checkpoint.")


if __name__ == "__main__":
    run_quiz()
