"""
Checkpoint Final — Atelier 01 LLM Baseline
5 questions sur l'ensemble de l'atelier.
Score ≥ 80% (4/5) → Bonus | Score < 60% (< 3/5) → Sprint
"""

QUESTIONS = [
    {
        "question": (
            "Le PM te demande : 'Est-ce qu'on peut utiliser un LLM sans RAG pour "
            "répondre aux questions des locataires sur leur logement ?' Quelle est ta réponse ?"
        ),
        "options": {
            "A": "Oui, si on utilise temperature=0 le LLM sera toujours correct",
            "B": "Non — le LLM hallucine sur les données privées car il ne les a jamais vues",
            "C": "Oui, si on utilise un modèle plus puissant comme Opus",
            "D": "Cela dépend du nombre de tokens dans le prompt",
        },
        "correct": "B",
        "explication": (
            "Un LLM ne connaît pas les données privées (marque de chaudière, numéro de bail...) "
            "car ces informations n'étaient pas dans son dataset d'entraînement. "
            "Peu importe la temperature ou la puissance du modèle — "
            "sans injection de contexte (RAG), il hallucine."
        ),
    },
    {
        "question": "Quelle est la différence principale entre un system prompt et un user prompt ?",
        "options": {
            "A": "Le system prompt coûte plus cher en tokens",
            "B": "Le user prompt est visible dans les logs, pas le system prompt",
            "C": (
                "Le system prompt définit le rôle et les contraintes de l'assistant ; "
                "le user prompt contient la question de l'utilisateur"
            ),
            "D": "Il n'y a aucune différence fonctionnelle, c'est juste une convention de nommage",
        },
        "correct": "C",
        "explication": (
            "Le system prompt = fiche de poste (rôle, périmètre, ton). "
            "Le user prompt = la requête concrète de l'utilisateur. "
            "Ensemble, ils forment le contexte complet envoyé au LLM. "
            "Sans system prompt, le LLM adopte un comportement généraliste non maîtrisé."
        ),
    },
    {
        "question": (
            "Tu poses la même question 5 fois à temperature=0.9. Les réponses sont différentes. "
            "Tu passes à temperature=0. Que se passe-t-il ?"
        ),
        "options": {
            "A": "Les réponses deviennent plus courtes car le modèle est moins créatif",
            "B": "Les réponses deviennent identiques (ou très similaires) — le modèle est déterministe",
            "C": "Le LLM refuse de répondre aux questions répétées",
            "D": "La latence augmente car le modèle réfléchit plus",
        },
        "correct": "B",
        "explication": (
            "À temperature=0, le LLM choisit toujours le token le plus probable → "
            "résultat déterministe et reproductible. "
            "À temperature=0.9, le sampling est aléatoire → variabilité. "
            "La latence et la longueur ne sont pas directement affectées par la temperature."
        ),
    },
    {
        "question": "Qu'est-ce que le knowledge cutoff d'un LLM ?",
        "options": {
            "A": "Le nombre maximum de tokens qu'un LLM peut traiter en une fois",
            "B": "La date à partir de laquelle le modèle n'a plus reçu de données d'entraînement",
            "C": "Le seuil de confiance en dessous duquel le LLM refuse de répondre",
            "D": "La limite de requêtes par heure de l'API",
        },
        "correct": "B",
        "explication": (
            "Le knowledge cutoff = date de fin du dataset d'entraînement. "
            "Tout document, événement ou information postérieure à cette date "
            "est inconnu du modèle. C'est une des raisons pour lesquelles "
            "les données privées du logement (DPE de 2024, bail signé récemment) "
            "ne sont jamais connues du LLM."
        ),
    },
    {
        "question": (
            "Ton script utilise max_tokens=50 et le LLM s'arrête en plein milieu d'une phrase. "
            "Quelle est la meilleure correction ?"
        ),
        "options": {
            "A": "Ajouter un retry automatique quand la réponse est tronquée",
            "B": "Passer à temperature=0 pour que le modèle fasse des phrases plus courtes",
            "C": "Augmenter max_tokens à 1024 (ou supprimer la limite pour les réponses conversationnelles)",
            "D": "Utiliser un modèle plus puissant qui gère mieux la longueur",
        },
        "correct": "C",
        "explication": (
            "max_tokens est un plafond de tokens en sortie. "
            "50 tokens ≈ 200 caractères : insuffisant pour une réponse descriptive. "
            "La correction = augmenter max_tokens (1024 est une valeur courante pour un assistant). "
            "Le coût ne change que si la réponse réelle est plus longue — "
            "max_tokens n'est pas facturé si non atteint."
        ),
    },
]

SCORE_BONUS = 4    # >= 4/5 → Bonus
SCORE_SPRINT = 3   # < 3/5 → Sprint


def run_quiz() -> None:
    print("\n" + "=" * 60)
    print("CHECKPOINT FINAL — Atelier 01 : LLM Baseline complet")
    print("=" * 60)
    print("5 questions — score ≥ 4/5 → Bonus | score < 3/5 → Sprint\n")

    score = 0
    details = []

    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n[{i}/5] {q['question']}")
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
    print(f"SCORE FINAL : {score}/5")
    print("=" * 60)

    print("\nExplications des réponses :")
    for num, correct, explication in details:
        statut = "OK" if correct else "RATÉ"
        print(f"\n[{num}] {statut} — {explication}")

    print("\n" + "=" * 60)
    if score >= SCORE_BONUS:
        print(f"=> BONUS  (score {score}/5 >= {SCORE_BONUS}/5)")
        print("   Rends-toi dans la section BONUS du guide.")
        print("   Défis : Sonnet vs Haiku, few-shot prompting.")
    elif score < SCORE_SPRINT:
        print(f"=> SPRINT (score {score}/5 < {SCORE_SPRINT}/5)")
        print("   Rends-toi dans la section SPRINT du guide.")
        print("   Rattrape les 2 concepts : temperature + system prompt.")
    else:
        print(f"=> ENTRE LES DEUX (score {score}/5)")
        print("   Prends 5 min, relis le concept raté dans le Carnet de bord.")
        print("   Puis pars en BONUS.")
    print("=" * 60)


if __name__ == "__main__":
    run_quiz()
