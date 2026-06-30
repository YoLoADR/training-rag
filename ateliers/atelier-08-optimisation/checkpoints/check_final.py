"""
Checkpoint Final — Atelier 08 Optimisation du pipeline RAG
5 questions : reranking, métriques (Recall@1/MRR), multi-query, HyDE, coût/latence.
Score >= 4/5 → Bonus | Score < 3/5 → Sprint
"""

QUESTIONS = [
    {
        "question": (
            "Sur le corpus HomeButler, Recall@5 est déjà à ~90-100% avant reranking. "
            "Quelle métrique montre alors le mieux le gain du reranking ?"
        ),
        "options": {
            "A": "Recall@5, toujours",
            "B": (
                "Recall@1 et MRR : le reranking remonte le BON chunk vers le sommet, "
                "donc ce sont les métriques de tête de liste qui bougent"
            ),
            "C": "La latence",
            "D": "Le nombre de chunks dans l'index",
        },
        "correct": "B",
        "explication": (
            "Sur un petit corpus, Recall@5 sature (le bon doc est presque toujours dans "
            "le top-5). Le reranking agit sur l'ORDRE : il fait passer le bon chunk du "
            "rang 3 au rang 1. Donc Recall@1 et MRR (Mean Reciprocal Rank) sont les bons "
            "indicateurs. Mesuré ici : Recall@1 40%→70%, MRR 0.617→0.833."
        ),
    },
    {
        "question": "Pourquoi des questions en langage NATUREL/familier révèlent-elles le gain du reranking ?",
        "options": {
            "A": "Parce qu'elles sont plus courtes",
            "B": (
                "Parce que leur vocabulaire diverge de celui des documents : le bi-encodeur "
                "se trompe d'ordre, et le cross-encoder (qui lit la paire question/chunk) "
                "rétablit la pertinence"
            ),
            "C": "Parce qu'elles contiennent des fautes d'orthographe",
            "D": "Parce qu'elles sont posées en anglais",
        },
        "correct": "B",
        "explication": (
            "Sur une question 'mot pour mot' du document, le bi-encodeur trouve déjà le bon "
            "chunk en tête → rien à gagner. Sur 'mon linge ressort trempé' (≠ 'essorage'), "
            "le bi-encodeur hésite ; le cross-encoder comprend le lien sémantique fin et "
            "reclasse correctement. Le reranking brille sur le vocabulaire divergent."
        ),
    },
    {
        "question": "Quelle est la complémentarité entre multi-query et reranking ?",
        "options": {
            "A": "Ils font exactement la même chose",
            "B": (
                "Multi-query augmente le RAPPEL (union de docs sur plusieurs reformulations) ; "
                "reranking augmente la PRÉCISION (réordonne/filtre). On les chaîne souvent : "
                "multi-query → reranking"
            ),
            "C": "Le multi-query remplace le reranking",
            "D": "Le reranking génère les reformulations",
        },
        "correct": "B",
        "explication": (
            "Multi-query ratisse plus large (plusieurs angles de la question → plus de bons "
            "chunks candidats). Reranking resserre (garde les meilleurs, dans le bon ordre). "
            "Pipeline avancé : retriever → multi-query (rappel) → reranking (précision)."
        ),
    },
    {
        "question": "Qu'est-ce que HyDE (Hypothetical Document Embeddings) ?",
        "options": {
            "A": "Un algorithme de chiffrement des embeddings",
            "B": (
                "On demande au LLM de générer une RÉPONSE hypothétique à la question, puis on "
                "embedde ce paragraphe (au lieu de la question) pour la recherche vectorielle"
            ),
            "C": "Un format de compression d'index FAISS",
            "D": "Une métrique d'évaluation du retrieval",
        },
        "correct": "B",
        "explication": (
            "HyDE part du constat qu'une question courte ressemble peu aux chunks (longs, "
            "déclaratifs). On génère une réponse hypothétique plausible, dont l'embedding "
            "est plus proche des vrais chunks → meilleur rappel sur questions vagues. "
            "Coût : un appel LLM de plus par requête."
        ),
    },
    {
        "question": "Pourquoi n'applique-t-on PAS le cross-encoder directement à tout le corpus ?",
        "options": {
            "A": "Parce que le cross-encoder ne supporte que 5 documents maximum",
            "B": "Parce qu'il faut une clé API pour chaque document",
            "C": (
                "Parce que le cross-encoder score chaque paire (question, chunk) : appliqué à "
                "des milliers de chunks à chaque requête, ce serait beaucoup trop lent. D'où "
                "l'étage 1 bi-encodeur qui pré-filtre à base_k candidats"
            ),
            "D": "Parce que FAISS l'interdit",
        },
        "correct": "C",
        "explication": (
            "Le cross-encoder est précis mais lent (un forward pass par paire). Le scorer sur "
            "tout le corpus à chaque requête est inutilisable à l'échelle. L'architecture en "
            "2 étages résout ça : bi-encodeur rapide pour réduire à base_k candidats, puis "
            "cross-encoder précis sur ces seuls candidats."
        ),
    },
]

SCORE_BONUS = 4
SCORE_SPRINT = 3


def run_quiz() -> None:
    print("\n" + "=" * 60)
    print("CHECKPOINT FINAL — Atelier 08 : Optimisation du pipeline RAG")
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
        print("   Défis : tuning base_k/top_n, multi-query + reranking chaînés, HyDE.")
    elif score < SCORE_SPRINT:
        print(f"=> SPRINT (score {score}/5 < {SCORE_SPRINT}/5)")
        print("   Rattrape : entonnoir base_k/top_n et bi vs cross-encoder.")
    else:
        print(f"=> ENTRE LES DEUX (score {score}/5)")
        print("   Relis le concept raté (Carnet de bord), puis pars en Bonus.")
    print("=" * 60)


if __name__ == "__main__":
    run_quiz()
