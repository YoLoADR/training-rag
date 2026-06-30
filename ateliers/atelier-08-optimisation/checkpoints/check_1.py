"""
Checkpoint 1 — Atelier 08 Optimisation du pipeline RAG
QCM 3 questions sur bi-encodeur vs cross-encoder, entonnoir, multi-query.
Passe/fail binaire (score >= 2/3).
"""

QUESTIONS = [
    {
        "question": "Quelle est la différence entre le bi-encodeur (embeddings) et le cross-encoder (reranker) ?",
        "options": {
            "A": "Le bi-encodeur est plus précis, le cross-encoder est plus rapide",
            "B": (
                "Le bi-encodeur encode question et chunk SÉPARÉMENT (rapide, scalable, "
                "appliqué à tout le corpus) ; le cross-encoder encode la PAIRE "
                "(question, chunk) ensemble (lent mais précis, appliqué à peu de candidats)"
            ),
            "C": "Ce sont deux noms pour la même technique",
            "D": "Le cross-encoder ne fonctionne qu'avec un GPU",
        },
        "correct": "B",
        "explication": (
            "Bi-encodeur : embeddings calculés une fois par chunk, recherche par similarité "
            "vectorielle (O(corpus), très rapide). Cross-encoder : lit la paire (question, chunk) "
            "ensemble et sort un score de pertinence (beaucoup plus précis, mais coûteux). "
            "D'où l'architecture en 2 étages : bi-encodeur pour ratisser large, cross-encoder "
            "pour reclasser un petit pool. flashrank tourne sur CPU."
        ),
    },
    {
        "question": "Pourquoi faut-il que base_k soit nettement plus grand que top_n dans le reranking ?",
        "options": {
            "A": "Pour consommer plus de mémoire et accélérer FAISS",
            "B": "Parce que flashrank exige base_k = 4 × top_n exactement",
            "C": (
                "Pour que le reranker ait un VRAI choix : repêcher un bon chunk situé au "
                "rang 8-15 du retrieval initial et le faire entrer dans le top-n final. "
                "Si base_k == top_n, il n'a plus rien à filtrer"
            ),
            "D": "Pour réduire le nombre d'appels au LLM",
        },
        "correct": "C",
        "explication": (
            "L'entonnoir : on récupère large (base_k=20) puis on resserre (top_n=5). "
            "Le gain du reranking vient de sa capacité à remonter un bon chunk mal classé "
            "par le bi-encodeur. Si base_k == top_n, il ne reste que le même ensemble : "
            "le reranker réordonne sans pouvoir filtrer → bénéfice quasi nul."
        ),
    },
    {
        "question": "D'où vient la diversité des reformulations dans un MultiQueryRetriever ?",
        "options": {
            "A": "De la température élevée du LLM (sampling aléatoire)",
            "B": (
                "De la CONSIGNE du prompt : on demande explicitement N reformulations "
                "différentes, générées en un seul appel LLM"
            ),
            "C": "Du nombre de chunks dans l'index FAISS",
            "D": "De l'algorithme MMR appliqué après coup",
        },
        "correct": "B",
        "explication": (
            "Le MultiQueryRetriever génère toutes ses variantes dans UN appel, piloté par "
            "le prompt ('génère 3 reformulations différentes'). La diversité est demandée, "
            "pas obtenue par hasard. On garde temperature=0 pour la reproductibilité. "
            "Multi-query améliore le RAPPEL (union des docs), le reranking la PRÉCISION."
        ),
    },
]

SCORE_MIN = 2


def run_quiz() -> None:
    print("\n" + "=" * 60)
    print("CHECKPOINT 1 — Atelier 08 : reranking, entonnoir, multi-query")
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
        print("=> Continue vers l'Étape 2 (mesurer le gain reranking).")
    else:
        print(f"\nRESULTAT : A RENFORCER ({score}/3 < {SCORE_MIN}/3)")
        print("=> Relis le Carnet de bord (bi/cross-encoder, entonnoir, multi-query).")


if __name__ == "__main__":
    run_quiz()
