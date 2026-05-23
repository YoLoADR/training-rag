"""
Bug v2 -- Trop d'outils dans la liste.

Le test verifie que le nombre d'outils dans ALL_TOOLS reste dans une plage
raisonnable (1 a 7) pour eviter la confusion du LLM.

Au-dela de 7 outils, le LLM a du mal a choisir et peut :
  - Appeler le mauvais outil
  - Produire des hallucinations sur les noms d'outils
  - Augmenter le nombre de steps sans ameliorer la reponse

Lance apres avoir applique v2.patch pour voir l'echec.
Lance apres correction (retirer les outils fictifs) pour voir le succes.
"""

import pytest


def get_all_tools():
    """Recharge les tools depuis le module."""
    import importlib
    import homebutler.agent.tools as tools_module
    importlib.reload(tools_module)
    return tools_module.ALL_TOOLS


class TestToolCount:
    def test_tool_count_in_range(self):
        """Le nombre d'outils doit etre entre 1 et 7."""
        tools = get_all_tools()
        n = len(tools)
        assert 1 <= n <= 7, (
            f"Nombre d'outils : {n} (hors plage 1-7)\n"
            "Au-dela de 7 outils, le LLM devient confus et choisit mal.\n"
            "Si tu as plus de 7 cas d'usage, utilise plusieurs agents specialises."
        )

    def test_core_tools_present(self):
        """Les 4 outils metier doivent etre presents."""
        tools = get_all_tools()
        tool_names = {t.name for t in tools}
        core_tools = {
            "search_home_docs",
            "analyze_energy_consumption",
            "find_local_products",
            "get_weather_forecast",
        }
        missing = core_tools - tool_names
        assert not missing, (
            f"Outils metier manquants : {missing}\n"
            "Ces 4 outils sont indispensables au fonctionnement de l'agent HomeButler."
        )

    def test_no_duplicate_tool_names(self):
        """Aucun outil ne doit avoir le meme nom."""
        tools = get_all_tools()
        names = [t.name for t in tools]
        duplicates = [n for n in names if names.count(n) > 1]
        assert not duplicates, (
            f"Noms d'outils dupliques : {set(duplicates)}\n"
            "Des doublons provoquent des comportements impredictibles dans l'agent."
        )
