"""
Checkpoint Final — Atelier 02 RAG Simple FAISS
5 questions sur l'ensemble : FAISS, MMR, Recall@k, faithfulness, chunking strategy.
Score ≥ 4/5 → Bonus | Score < 3/5 → Sprint
"""

QUESTIONS = [
    {
        "question": (
            "Le PM te demande : 'Notre Recall@5 est à 65% — quels paramètres "
            "dois-tu d'abord ajuster ?' Quelle est ta réponse ?"
        ),
        "options": {
            "A": "Passer à un LLM plus puissant (Opus au lieu de Sonnet)",
            "B": (
                "Réduire chunk_size (ex: 512 → 400) et augmenter k (ex: 4 → 6) "
                "pour donner plus de chances au retriever de trouver le bon chunk"
            ),
            "C": "Augmenter la temperature du LLM pour qu'il soit plus créatif",
            "D": "Ajouter plus de PDFs dans data/documents/",
        },
        "correct": "B",
        "explication": (
            "Recall@k est une métrique de RETRIEVAL, pas de génération. "
            "Le LLM n'y peut rien : si le retriever rate, le LLM ne peut pas deviner. "
            "Pour améliorer Recall@5 : ajuster chunk_size, chunk_overlap, k, "
            "ou changer de stratégie de chunking. "
            "Passer à Opus n'aide pas si le bon chunk n'est pas récupéré."
        ),
    },
    {
        "question": (
            "Qu'est-ce que FAISS et pourquoi est-ce utile pour le RAG ?"
        ),
        "options": {
            "A": "Un modèle de langage développé par Meta pour générer du texte",
            "B": "Un outil de chiffrement pour sécuriser les PDFs avant indexation",
            "C": (
                "Une bibliothèque d'indexation vectorielle qui trouve les k voisins "
                "les plus proches d'un vecteur requête en O(log n) via ANN"
            ),
            "D": "Un format de fichier pour stocker les embeddings",
        },
        "correct": "C",
        "explication": (
            "FAISS (Facebook AI Similarity Search) indexe des vecteurs (embeddings) "
            "et retrouve les plus proches approximativement (ANN = Approximate Nearest Neighbors). "
            "Sans FAISS : comparer chaque requête à tous les chunks = O(n). "
            "Avec FAISS : O(log n) → quelques millisecondes sur des millions de vecteurs. "
            "Analogie : index alphabétique vs feuilleter toutes les pages."
        ),
    },
    {
        "question": (
            "Quelle est la différence entre search_type='similarity' et search_type='mmr' "
            "dans un retriever FAISS ?"
        ),
        "options": {
            "A": "similarity est plus rapide ; mmr donne de meilleurs scores de Recall@k",
            "B": (
                "similarity retourne les k chunks les plus proches (peut-être des doublons) ; "
                "mmr retourne k chunks pertinents ET diversifiés (pénalise la redondance)"
            ),
            "C": "mmr nécessite une clé API supplémentaire pour fonctionner",
            "D": "Il n'y a aucune différence sur des corpus < 1000 chunks",
        },
        "correct": "B",
        "explication": (
            "similarity = retourne les k plus proches voisins → risque de doublons "
            "(même info répétée dans le PDF = k fois le même chunk). "
            "MMR (Maximal Marginal Relevance) pré-filtre fetch_k candidats puis "
            "sélectionne k chunks à la fois pertinents ET diversifiés. "
            "Analogie : 4 magazines différents plutôt que 4 fois le même."
        ),
    },
    {
        "question": (
            "Que mesure la 'faithfulness' dans un pipeline RAG ?"
        ),
        "options": {
            "A": "Le temps de réponse du LLM en millisecondes",
            "B": "Le nombre de tokens consommés par requête",
            "C": (
                "Si la réponse du LLM s'appuie réellement sur les documents récupérés "
                "ou si elle invente au-delà du contexte injecté"
            ),
            "D": "La similarité cosinus entre la question et le chunk le plus proche",
        },
        "correct": "C",
        "explication": (
            "Faithfulness = fidélité de la réponse au contexte RAG. "
            "Score entre 0 et 1 : 1.0 = chaque affirmation de la réponse est vérifiable "
            "dans les chunks récupérés. 0.0 = la réponse est entièrement inventée. "
            "Un LLM à faithfulness faible 'hallucine au-delà' du contexte : "
            "il ajoute des informations qui ne sont pas dans les docs."
        ),
    },
    {
        "question": (
            "Pourquoi ne faut-il PAS appeler build_faiss_index(force_rebuild=True) "
            "à chaque requête ?"
        ),
        "options": {
            "A": "Parce que FAISS ne supporte pas plus de 100 reconstructions par jour",
            "B": (
                "Parce que la construction de l'index = calcul de tous les embeddings "
                "(10-30s sur nos PDFs) → catastrophique en prod. "
                "L'index doit être construit une fois, sauvegardé, et rechargé."
            ),
            "C": "Parce que force_rebuild=True change les vecteurs aléatoirement",
            "D": "Pour des raisons de licence : FAISS gratuit limite les reconstructions",
        },
        "correct": "B",
        "explication": (
            "Construction = calcul d'un embedding par chunk = opération CPU coûteuse "
            "(10-30s sur nos PDFs, beaucoup plus sur de gros corpus). "
            "Retrieval = recherche ANN dans l'index existant = < 1s. "
            "Pattern correct : construire une fois au démarrage (ou lors d'un changement de docs), "
            "puis réutiliser l'index pour toutes les requêtes. "
            "FAISS.save_local() / load_local() permettent de persister l'index sur disque."
        ),
    },
]

SCORE_BONUS = 4
SCORE_SPRINT = 3


def run_quiz() -> None:
    print("\n" + "=" * 60)
    print("CHECKPOINT FINAL — Atelier 02 : RAG Simple FAISS complet")
    print("=" * 60)
    print("5 questions — score >= 4/5 → Bonus | score < 3/5 → Sprint\n")

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
        print("   Défis : variation chunk_size, MMR vs similarity.")
    elif score < SCORE_SPRINT:
        print(f"=> SPRINT (score {score}/5 < {SCORE_SPRINT}/5)")
        print("   Rends-toi dans la section SPRINT du guide.")
        print("   Rattrape : chunk_overlap et persistance de l'index FAISS.")
    else:
        print(f"=> ENTRE LES DEUX (score {score}/5)")
        print("   Relis le concept raté dans le Carnet de bord (5 min).")
        print("   Puis pars en BONUS.")
    print("=" * 60)


if __name__ == "__main__":
    run_quiz()
