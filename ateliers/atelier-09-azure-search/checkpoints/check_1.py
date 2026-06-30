"""
Checkpoint 1 — Atelier 09 Azure AI Search
QCM 3 questions : control plane vs data plane, dimension vectorielle, hybrid search.
Passe/fail binaire (score >= 2/3).
"""

QUESTIONS = [
    {
        "question": "Que gère la CLI `az search` (control plane) vs le SDK Python (data plane) ?",
        "options": {
            "A": "az search gère tout, le SDK est optionnel",
            "B": (
                "az search gère le SERVICE (créer/scaler/clés) ; le SDK gère le CONTENU "
                "(index, vecteurs, ingestion, requêtes). Aucune commande az search pour le contenu"
            ),
            "C": "Le SDK gère le service, az search gère les requêtes",
            "D": "Les deux font exactement la même chose",
        },
        "correct": "B",
        "explication": (
            "Control plane (az search) = le service. Data plane (SDK azure-search-documents) = "
            "index/ingestion/requêtes. Il n'existe AUCUNE commande az search pour créer un index "
            "ou ingérer — tout le RAG est en SDK/REST, donc scriptable au terminal."
        ),
    },
    {
        "question": "Pourquoi la dimension du champ vectoriel doit-elle être 384 dans notre schéma ?",
        "options": {
            "A": "C'est la valeur par défaut d'Azure",
            "B": "Pour économiser du stockage",
            "C": (
                "Parce qu'on utilise fastembed (MiniLM) qui produit des vecteurs de 384 dims : "
                "le schéma DOIT matcher l'embedding, sinon Azure rejette l'upload"
            ),
            "D": "Parce que 384 est la dimension maximale autorisée",
        },
        "correct": "C",
        "explication": (
            "La dimension est dictée par le modèle d'embedding : 384 pour MiniLM, 1536 pour "
            "text-embedding-3-small/ada-002. Schéma ≠ embedding → upload rejeté (Bug v1)."
        ),
    },
    {
        "question": "Qu'apporte la recherche 'hybrid' par rapport à 'similarity' (vecteur seul) ?",
        "options": {
            "A": "Elle est plus rapide",
            "B": (
                "Elle combine BM25 (mots-clés) + vecteurs (sens), fusionnés par RRF → rattrape "
                "le vocabulaire divergent et les termes exacts (codes, marques) que le vecteur rate"
            ),
            "C": "Elle chiffre les requêtes",
            "D": "Elle ne marche que sur le tier gratuit",
        },
        "correct": "B",
        "explication": (
            "hybrid = vecteur + BM25 fusionnés (RRF). 'similarity' = vecteur pur. L'hybride gagne "
            "sur les corpus techniques (codes erreur, marques). semantic_hybrid ajoute le semantic "
            "ranker (tier Basic+)."
        ),
    },
]

SCORE_MIN = 2


def run_quiz() -> None:
    print("\n" + "=" * 60)
    print("CHECKPOINT 1 — Atelier 09 : Azure AI Search")
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
        print(f"\n[{num}] {'OK' if correct else 'RATÉ'} — {explication}")

    if score >= SCORE_MIN:
        print(f"\nRESULTAT : VALIDE ({score}/3 >= {SCORE_MIN}/3)")
        print("=> Continue : créer l'index (SDK) + ingérer + requêter.")
    else:
        print(f"\nRESULTAT : A RENFORCER ({score}/3 < {SCORE_MIN}/3)")
        print("=> Relis le Carnet (control/data plane, dimension, hybrid) + CLI-VS-PORTAIL.md.")


if __name__ == "__main__":
    run_quiz()
