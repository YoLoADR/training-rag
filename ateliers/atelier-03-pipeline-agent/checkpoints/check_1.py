"""
Checkpoint 1 -- Atelier 03 Pipeline Agent ReAct
EnsembleRetriever / ChromaDB / Hybrid Search

3 questions QCM auto-corrigees.
Lance : python ateliers/atelier-03-pipeline-agent/checkpoints/check_1.py
"""


QUESTIONS = [
    {
        "id": 1,
        "question": "Qu'est-ce qu'un EnsembleRetriever ?",
        "choices": {
            "A": "Un retriever qui utilise plusieurs modeles de langage en parallele",
            "B": "Un retriever qui combine les resultats de plusieurs retrievers (ex: FAISS + Chroma) avec des poids",
            "C": "Un retriever qui effectue plusieurs requetes sur le meme index FAISS",
            "D": "Un retriever qui fusionne plusieurs bases de donnees SQL",
        },
        "answer": "B",
        "explanation": (
            "L'EnsembleRetriever de LangChain combine les resultats de plusieurs retrievers differents "
            "(ici FAISS pour la recherche dense et ChromaDB pour la recherche avec filtres). "
            "Il utilise Reciprocal Rank Fusion pour fusionner les resultats selon les poids configures."
        ),
    },
    {
        "id": 2,
        "question": (
            "Tu configures `ensemble_weights=[0.8, 0.2]`. "
            "Que signifie ce reglage ?"
        ),
        "choices": {
            "A": "80% des documents viennent de FAISS et 20% de ChromaDB (en nombre brut)",
            "B": "La recherche FAISS est ponderee 4x plus que ChromaDB dans le score de fusion",
            "C": "L'index FAISS est 80% plus grand que l'index ChromaDB",
            "D": "80% des requetes vont vers FAISS, 20% vers ChromaDB",
        },
        "answer": "B",
        "explanation": (
            "Les poids [0.8, 0.2] influencent le score de fusion (Reciprocal Rank Fusion). "
            "Un score de 0.8 pour FAISS signifie que ses resultats ont un poids 4x superieur "
            "a ceux de ChromaDB dans le classement final. "
            "Ce n'est pas un partitionnement du nombre de documents retournes."
        ),
    },
    {
        "id": 3,
        "question": "Pourquoi ChromaDB est-il utile en complement de FAISS pour HomeButler ?",
        "choices": {
            "A": "ChromaDB est plus rapide que FAISS pour les recherches vectorielles",
            "B": "ChromaDB permet de filtrer par metadonnees (type de document, piece, etc.) en plus de la recherche semantique",
            "C": "ChromaDB peut stocker des documents texte brut sans embeddings",
            "D": "ChromaDB est open-source contrairement a FAISS",
        },
        "answer": "B",
        "explanation": (
            "L'avantage de ChromaDB est le filtrage par metadonnees. "
            "Par exemple, on peut chercher 'notice chaudiere' uniquement dans les documents "
            "de type 'equipement' ou uniquement pour la piece 'chaufferie'. "
            "FAISS fait uniquement de la recherche vectorielle dense sans filtrage natif."
        ),
    },
]


def run_quiz():
    print("=" * 60)
    print("Checkpoint 1 -- EnsembleRetriever / ChromaDB / Hybrid Search")
    print("=" * 60)
    print("3 questions QCM. Reponds par la lettre (A/B/C/D).\n")

    score = 0
    results = []

    for q in QUESTIONS:
        print(f"Question {q['id']} : {q['question']}")
        for letter, text in q["choices"].items():
            print(f"  {letter}) {text}")

        while True:
            answer = input("\nTa reponse : ").strip().upper()
            if answer in q["choices"]:
                break
            print("  Reponds par A, B, C ou D.")

        correct = answer == q["answer"]
        if correct:
            score += 1
            print("  CORRECT")
        else:
            print(f"  INCORRECT. La bonne reponse etait : {q['answer']}")
        print(f"  Explication : {q['explanation']}\n")
        results.append({"id": q["id"], "correct": correct})

    print("=" * 60)
    print(f"Score : {score}/{len(QUESTIONS)}")

    if score == len(QUESTIONS):
        print("Parfait ! Tu peux passer a l'Etape 2.")
    elif score >= 2:
        print("Bon. Relis l'explication de la question ratee, puis continue.")
    else:
        print("Relis la section 'EnsembleRetriever' du Carnet de bord avant de continuer.")
        print("Sans validation de ce checkpoint, on ne passe pas a l'etape suivante.")

    print("=" * 60)
    return score


if __name__ == "__main__":
    run_quiz()
