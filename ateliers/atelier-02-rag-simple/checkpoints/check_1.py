"""
Checkpoint 1 — Atelier 02 RAG Simple FAISS
QCM 3 questions sur Embedding, Chunking (fixed vs recursive).
Passe/fail binaire (score ≥ 2/3).
"""

QUESTIONS = [
    {
        "question": (
            "Qu'est-ce qu'un embedding dans le contexte du RAG ?"
        ),
        "options": {
            "A": "Un token spécial inséré dans le prompt pour améliorer la réponse",
            "B": "Une transformation d'un texte en vecteur de nombres (ex: 384 dimensions)",
            "C": "Un fichier binaire qui stocke les PDFs compressés",
            "D": "Un paramètre de configuration pour le modèle Anthropic",
        },
        "correct": "B",
        "explication": (
            "Un embedding transforme un texte en un vecteur de N nombres (ici 384). "
            "Deux textes sémantiquement proches → vecteurs proches géométriquement. "
            "Analogie : coordonnées GPS à 384 dimensions. "
            "C'est la base du retrieval sémantique."
        ),
    },
    {
        "question": (
            "Quelle est la principale différence entre fixed-size chunking et recursive chunking ?"
        ),
        "options": {
            "A": "Le recursive chunking est toujours plus rapide à calculer",
            "B": (
                "Le fixed-size coupe tous les X caractères sans tenir compte des séparateurs ; "
                "le recursive essaie de couper aux séparateurs naturels (paragraphe, phrase, mot)"
            ),
            "C": "Le fixed-size ne fonctionne qu'avec des PDFs, pas avec du texte brut",
            "D": "Il n'y a aucune différence pratique sur les PDFs courts",
        },
        "correct": "B",
        "explication": (
            "Fixed-size = coupe brutalement tous les chunk_size caractères (peut couper une phrase). "
            "Recursive = essaie d'abord \\n\\n, puis \\n, puis '.', puis espace. "
            "Résultat : le recursive préserve mieux la cohérence sémantique des chunks. "
            "Recommandé pour la plupart des documents textuels."
        ),
    },
    {
        "question": (
            "Pourquoi utilise-t-on chunk_overlap (chevauchement entre chunks consécutifs) ?"
        ),
        "options": {
            "A": "Pour réduire le nombre total de chunks et accélérer l'indexation",
            "B": "Pour permettre au modèle d'embeddings de mieux calculer les vecteurs",
            "C": (
                "Pour éviter de perdre les informations à la frontière entre deux chunks "
                "(une phrase coupée en deux serait inaccessible sans overlap)"
            ),
            "D": "Parce que FAISS requiert des chunks de taille identique",
        },
        "correct": "C",
        "explication": (
            "chunk_overlap=50 signifie que les 50 derniers caractères du chunk N "
            "sont les 50 premiers du chunk N+1. "
            "Si une information clé (ex: 'Le code erreur F4 signifie...') se trouve "
            "à cheval entre deux chunks, l'overlap garantit qu'elle est entière dans l'un d'eux. "
            "L'overhead (~10%) est faible par rapport au gain qualité."
        ),
    },
]

SCORE_MIN = 2


def run_quiz() -> None:
    print("\n" + "=" * 60)
    print("CHECKPOINT 1 — Atelier 02 : Embedding, Chunking")
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
        print("=> Continue vers l'Etape 2 (FAISS + retriever).")
    else:
        print(f"\nRESULTAT : A RENFORCER ({score}/3 < {SCORE_MIN}/3)")
        print("=> Relis le Carnet de bord (Embedding, Fixed vs Recursive, chunk_overlap)")
        print("=> Puis relance ce checkpoint.")


if __name__ == "__main__":
    run_quiz()
