"""
Checkpoint Final — Atelier 09 Azure AI Search
5 questions (QCM). Score >= 4/5 → Bonus | score < 3/5 → Sprint.
"""

QUESTIONS = [
    {
        "question": "Quelle tâche n'est PAS réalisable avec la CLI `az search` ?",
        "options": {
            "A": "Créer le service de recherche",
            "B": "Récupérer la clé admin",
            "C": "Créer un index vectoriel et y ingérer des documents",
            "D": "Supprimer le service",
        },
        "correct": "C",
        "explication": (
            "Créer un index / ingérer = DATA PLANE → SDK/REST uniquement. az search ne touche "
            "que le service (control plane)."
        ),
    },
    {
        "question": "Tu pousses des vecteurs de 384 dims dans un index déclaré à 1536. Que se passe-t-il ?",
        "options": {
            "A": "Azure tronque les vecteurs à 384",
            "B": "L'upload est REJETÉ (la dimension du vecteur doit égaler celle du champ)",
            "C": "Azure complète les vecteurs avec des zéros",
            "D": "Rien, la dimension est indicative",
        },
        "correct": "B",
        "explication": "Dimension du champ = dimension de l'embedding, sans tolérance. C'est le Bug v1.",
    },
    {
        "question": "Le champ `content` est déclaré searchable=False. Symptôme ?",
        "options": {
            "A": "L'ingestion plante immédiatement",
            "B": "La recherche vectorielle pure échoue",
            "C": (
                "L'ingestion réussit, mais la recherche HYBRIDE renvoie peu/pas de résultats "
                "(le volet BM25 sur content est muet) — bug silencieux"
            ),
            "D": "Le service refuse de démarrer",
        },
        "correct": "C",
        "explication": (
            "searchable=False → BM25 n'indexe pas content → le volet mots-clés de l'hybride est "
            "neutralisé. Aucune erreur à l'ingestion : le bug n'apparaît qu'à la requête (Bug v3)."
        ),
    },
    {
        "question": "Pourquoi un service Basic PARTAGÉ plutôt que Free pour une classe ?",
        "options": {
            "A": "Le Free ne supporte pas les vecteurs",
            "B": (
                "Le Free est limité à 1 service par souscription : 15 élèves sur une souscription "
                "→ un seul create réussit. Basic partagé = 1 service, N index (un par élève)"
            ),
            "C": "Le Basic est gratuit",
            "D": "Le Free n'autorise pas la CLI",
        },
        "correct": "B",
        "explication": (
            "Free = 1 service/souscription (+ 50 Mo, 3 index). En classe : 1 service Basic partagé "
            "par le formateur, chaque élève crée SON index (index_name = trigramme)."
        ),
    },
    {
        "question": "Pourquoi lancer azure_teardown.sh en fin de séance ?",
        "options": {
            "A": "Pour vider le cache local",
            "B": (
                "Parce qu'un tier Dedicated (Free/Basic/…) est facturé à l'HEURE dès la création "
                "(pas à l'usage) → on supprime le groupe de ressources pour éviter les frais"
            ),
            "C": "Pour des raisons de sécurité réseau uniquement",
            "D": "Ce n'est pas nécessaire",
        },
        "correct": "B",
        "explication": (
            "Dedicated = facturation horaire dès la création. `az group delete` supprime service "
            "+ index. Garde-fou coût indispensable."
        ),
    },
]

SCORE_BONUS = 4
SCORE_SPRINT = 3


def run_quiz() -> None:
    print("\n" + "=" * 60)
    print("CHECKPOINT FINAL — Atelier 09 : Azure AI Search")
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
    for num, correct, expl in details:
        print(f"\n[{num}] {'OK' if correct else 'RATÉ'} — {expl}")

    print("\n" + "=" * 60)
    if score >= SCORE_BONUS:
        print(f"=> BONUS ({score}/5) — semantic_hybrid (semantic ranker), integrated vectorization.")
    elif score < SCORE_SPRINT:
        print(f"=> SPRINT ({score}/5) — reprends control/data plane, dimension, hybrid.")
    else:
        print(f"=> ENTRE LES DEUX ({score}/5) — relis le concept raté puis Bonus.")
    print("=" * 60)


if __name__ == "__main__":
    run_quiz()
