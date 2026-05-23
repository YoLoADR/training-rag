"""
Bug v3 -- Agent sans max_iterations.

Le test verifie que la configuration de l'AgentExecutor inclut
un max_iterations raisonnable (<= 15).

Sans max_iterations, LangChain utilise sa valeur par defaut (15 en LangChain >=0.2)
ou peut boucler indefiniment sur certaines versions. Le risque :
  - Boucle infinie si le modele hallucine des observations
  - Cout API explose (centaines d'appels LLM)
  - Timeout cote utilisateur

Ce test inspecte le code de build_agent_executor pour detecter la configuration.
Lance apres avoir applique v3.patch pour voir l'echec.
Lance apres correction pour voir le succes.
"""

import ast
import inspect
import pytest
from pathlib import Path


def get_agent_executor_source() -> str:
    """Retourne le code source de build_agent_executor."""
    try:
        from homebutler.agent import react_agent
        import importlib
        importlib.reload(react_agent)
        return inspect.getsource(react_agent.build_agent_executor)
    except (ImportError, AttributeError):
        # Lecture directe du fichier si l'import echoue
        path = Path(__file__).resolve().parent.parent.parent.parent / "homebutler" / "agent" / "react_agent.py"
        if path.exists():
            return path.read_text()
        return ""


class TestMaxIterations:
    def test_max_iterations_present_in_source(self):
        """max_iterations doit etre present dans build_agent_executor."""
        source = get_agent_executor_source()
        assert "max_iterations" in source, (
            "max_iterations absent de la configuration AgentExecutor.\n"
            "Sans ce parametre, l'agent peut boucler indefiniment.\n"
            "Ajoute : max_iterations=8  dans AgentExecutor(...)."
        )

    def test_max_iterations_value_reasonable(self):
        """max_iterations doit etre une valeur raisonnable (entre 2 et 15)."""
        source = get_agent_executor_source()
        # Chercher un pattern 'max_iterations=<nombre>'
        import re
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
        source = get_agent_executor_source()
        assert "handle_parsing_errors" in source, (
            "handle_parsing_errors absent.\n"
            "Sans ce parametre, un format de reponse LLM inattendu fait planter l'agent.\n"
            "Ajoute : handle_parsing_errors=True  dans AgentExecutor(...)."
        )
