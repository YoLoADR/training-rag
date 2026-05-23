"""
Checkpoint final -- Atelier 03 Pipeline Agent ReAct
ReAct / Tools / Memoire / max_iterations

5 questions QCM auto-corrigees.
Score >= 80% (4/5) -> Bonus
Score < 60% (< 3/5) -> Sprint

Lance : python ateliers/atelier-03-pipeline-agent/checkpoints/check_final.py
"""


QUESTIONS = [
    {
        "id": 1,
        "question": (
            "Dans la boucle ReAct, quelle est l'ordre correct des etapes ?"
        ),
        "choices": {
            "A": "Action -> Thought -> Observation -> Final Answer",
            "B": "Thought -> Action -> Observation -> (boucle) -> Final Answer",
            "C": "Observation -> Thought -> Action -> Final Answer",
            "D": "Action -> Observation -> Thought -> Final Answer",
        },
        "answer": "B",
        "explanation": (
            "ReAct = Reason + Act. La boucle : "
            "Thought (raisonnement) -> Action (appel d'outil) -> "
            "Observation (resultat de l'outil) -> retour au Thought, "
            "jusqu'a ce que le LLM decide qu'il a assez d'information pour Final Answer."
        ),
    },
    {
        "id": 2,
        "question": (
            "Tu constates que l'agent n'utilise jamais `search_home_docs` "
            "meme pour des questions sur les equipements de la maison. "
            "Quelle est la cause la plus probable ?"
        ),
        "choices": {
            "A": "L'index FAISS n'est pas construit",
            "B": "La description du tool est trop vague pour que le LLM comprenne quand l'utiliser",
            "C": "Il faut augmenter max_iterations",
            "D": "La fonction Python de l'outil a un bug",
        },
        "answer": "B",
        "explanation": (
            "80% des cas ou un agent ignore un outil viennent d'une description insuffisante. "
            "Le LLM lit la description pour decider d'appeler l'outil ou non. "
            "Une description vague ('cherche des documents') ne lui permet pas de savoir "
            "quand c'est pertinent vs un autre outil."
        ),
    },
    {
        "id": 3,
        "question": "Que se passe-t-il si on omet `max_iterations` dans `AgentExecutor` ?",
        "choices": {
            "A": "L'agent s'arrete automatiquement apres 1 outil appele",
            "B": "LangChain refuse de creer l'AgentExecutor et leve une erreur",
            "C": "L'agent utilise la valeur par defaut de LangChain et peut potentiellement boucler si le LLM hallucine",
            "D": "L'agent devient synchrone et bloque le thread principal",
        },
        "answer": "C",
        "explanation": (
            "LangChain a une valeur par defaut pour max_iterations (15 en v0.3). "
            "Mais en cas d'hallucination des observations ou de format LLM incorrect, "
            "l'agent peut depasser cette limite ou boucler. "
            "Toujours specifier max_iterations explicitement (recommande : 8) "
            "pour le plafonnement et le controle du cout."
        ),
    },
    {
        "id": 4,
        "question": (
            "`ConversationBufferWindowMemory(k=6)` : "
            "que conserve exactement ce composant ?"
        ),
        "choices": {
            "A": "Les 6 derniers documents recuperes par le retriever",
            "B": "Les 6 dernieres paires user/agent (12 messages : 6 human + 6 AI)",
            "C": "Un resume des 6 derniers echanges compresse par un LLM",
            "D": "Les 6 derniers outils appeles avec leurs observations",
        },
        "answer": "B",
        "explanation": (
            "ConversationBufferWindowMemory(k=6) garde les 6 derniers TOURS de conversation, "
            "soit 6 messages human + 6 messages AI = 12 messages au maximum dans l'historique. "
            "k=0 signifie pas de memoire. k=20 garde 20 tours mais augmente le cout en tokens."
        ),
    },
    {
        "id": 5,
        "question": (
            "Tu testes l'agent avec `memory_k=0` puis `memory_k=6`. "
            "Au tour 3, tu demandes 'Et la chaudiere que j'ai mentionnee tout a l'heure ?'. "
            "Que se passe-t-il ?"
        ),
        "choices": {
            "A": "Avec k=0 et k=6 : l'agent retrouve l'info car elle est dans le RAG",
            "B": "Avec k=0 : l'agent ne retrouve pas l'info (elle n'est plus dans le contexte). Avec k=6 : il retrouve",
            "C": "Avec k=0 et k=6 : l'agent ne retrouve pas (la memoire ne stocke que les outils appeles)",
            "D": "Avec k=6 : l'agent retrouve uniquement si l'info vient d'un outil RAG, pas d'un input utilisateur",
        },
        "answer": "B",
        "explanation": (
            "k=0 signifie aucune memoire : chaque question est traitee independamment. "
            "Si tu as mentionne 'chaudiere Viessmann' au tour 1, cette info est perdue au tour 3 avec k=0. "
            "Avec k=6, les 6 derniers tours sont dans le contexte, donc l'agent retrouve l'info. "
            "Important : la memoire stocke tout (inputs utilisateur ET observations d'outils)."
        ),
    },
]


def run_quiz():
    print("=" * 65)
    print("Checkpoint Final -- ReAct / Tools / Memoire / max_iterations")
    print("=" * 65)
    print("5 questions QCM. Score >= 4/5 -> Bonus | Score < 3/5 -> Sprint\n")

    score = 0

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

    print("=" * 65)
    print(f"Score final : {score}/{len(QUESTIONS)}")

    if score >= 4:
        print("\nExcellent ! -> BONUS (parcours avance, 60-70 min)")
        print("Va a la section 'BONUS' du GUIDE-ELEVE.md")
    elif score >= 3:
        print("\nCorrect. Prends 5 min, relis les explications des questions ratees.")
        print("Tu peux partir en Bonus en etant prudent sur tes points faibles.")
    else:
        print("\n-> SPRINT recommande (30 min de rattrapage)")
        print("Va a la section 'SPRINT' du GUIDE-ELEVE.md")
        print("Concepts a retravailler : ReAct, descriptions d'outils, memoire.")

    print("=" * 65)
    return score


if __name__ == "__main__":
    run_quiz()
