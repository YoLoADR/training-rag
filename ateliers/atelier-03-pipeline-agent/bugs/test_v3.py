"""
Bug v3 -- Agent sans parametre de limite de boucle.

Le test verifie que la configuration de l'AgentExecutor inclut
un parametre de limite raisonnable (<= 15).

Sans cette limite, LangChain peut boucler indefiniment. Le risque :
  - Boucle infinie si le modele hallucine des observations
  - Cout API explose (centaines d'appels LLM)
  - Timeout cote utilisateur

Ce test inspecte le code source de react_agent.py pour detecter la configuration.
Lance apres avoir applique v3.patch pour voir l'echec.
Lance apres correction pour voir le succes.
"""

import re
import pytest
from pathlib import Path


def get_react_agent_source() -> str:
    """Retourne le code source complet de react_agent.py."""
    path = Path(__file__).resolve().parent.parent.parent.parent / "homebutler" / "agent" / "react_agent.py"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


class TestMaxIterations:
    def test_max_iterations_present_in_source(self):
        """max_iterations doit etre present dans get_agent_executor."""
        source = get_react_agent_source()
        assert "max_iterations" in source, (
            "max_iterations absent de la configuration AgentExecutor.\n"
            "Sans ce parametre, l'agent peut boucler indefiniment.\n"
            "Ajoute : max_iterations=8  dans AgentExecutor(...)."
        )

    def test_max_iterations_value_reasonable(self):
        """max_iterations doit etre une valeur raisonnable (entre 2 et 15)."""
        source = get_react_agent_source()
        matches = re.findall(r'max_iterations\s*=\s*(\d+)', source)
        if not matches:
            pytest.fail(
                "max_iterations est present mais sa valeur n'est pas lisible statiquement.\n"
                "Utilise une valeur litterale : max_iterations=8"
            )
        value = int(matches[0])
        assert 2 <= value <= 15, (
            f"max_iterations={value} hors plage raisonnable [2-15].\n"
            "- Trop petit (< 2) : l'agent n'a pas le temps de raisonner.\n"
            "- Trop grand (> 15) : risque de boucle et de cout excessif.\n"
            "Recommande : max_iterations=8"
        )

    def test_handle_parsing_errors_present(self):
        """handle_parsing_errors=True doit etre present (evite les crashs sur format LLM)."""
        source = get_react_agent_source()
        assert "handle_parsing_errors" in source, (
            "handle_parsing_errors absent.\n"
            "Sans ce parametre, un format de reponse LLM inattendu fait planter l'agent.\n"
            "Ajoute : handle_parsing_errors=True  dans AgentExecutor(...)."
        )
