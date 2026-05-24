"""Script de base Atelier 01 avec system prompt."""
from langchain_core.messages import HumanMessage, SystemMessage
from homebutler.llm.provider import get_llm

SYSTEM_PROMPT = (
    "Tu es un assistant maison HomeButler. "
    "Tu aides les locataires avec leurs questions sur leur logement. "
    "Si tu ne disposes pas des informations privées du logement, "
    "réponds poliment que tu n'as pas accès à ces données."
)
QUESTIONS_LOGEMENT = [
    "Quelle est la marque de ma chaudière ?",
    "À quelle température dois-je régler ma chaudière la nuit ?",
    "Quelle est la classe énergétique (DPE) de mon logement ?",
    "Quel est le numéro à appeler en cas de fuite d'eau dans mon bail ?",
    "Quels sont les producteurs locaux disponibles près de chez moi ?",
]

def main() -> None:
    llm = get_llm(temperature=0.1)
    print("\n═══ Run — avec system prompt ═══")
    for i, q in enumerate(QUESTIONS_LOGEMENT, 1):
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=q),
        ])
        print(f"\n[{i}] {q}")
        print(f"    → {response.content[:300]}")

if __name__ == "__main__":
    main()
