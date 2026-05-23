"""
Bug v1 -- Description d'outil bacle.

Le test verifie que search_docs_tool possede une description suffisamment
informative pour que le LLM sache QUAND et COMMENT l'utiliser.

Critere : la description doit contenir au moins 3 elements d'information :
  1. Le domaine couvert (ex: bail, notices, equipements...)
  2. Quand l'utiliser (ex: "pour toute question sur...")
  3. Le format de l'input attendu

Lance apres avoir applique v1.patch pour voir l'echec.
Lance apres correction pour voir le succes.
"""

import pytest


def get_tool_description() -> str:
    """Recharge les tools depuis le module (evite le cache)."""
    import importlib
    import homebutler.agent.tools as tools_module
    importlib.reload(tools_module)
    return tools_module.search_docs_tool.description


class TestToolDescription:
    def test_description_mentions_domain(self):
        """La description doit mentionner le domaine couvert (documents, notices, bail...)."""
        desc = get_tool_description()
        domain_keywords = ["document", "notice", "bail", "equipement", "logement",
                           "documents", "notices", "équipement", "équipements"]
        has_domain = any(kw.lower() in desc.lower() for kw in domain_keywords)
        assert has_domain, (
            f"Description trop vague : '{desc}'\n"
            "La description doit mentionner le domaine couvert "
            "(ex: 'notices d\\'equipements', 'bail', 'documents du logement')."
        )

    def test_description_mentions_when_to_use(self):
        """La description doit indiquer quand utiliser l'outil."""
        desc = get_tool_description()
        usage_keywords = ["utilise", "utilisez", "pour", "when", "question", "quand"]
        has_usage = any(kw.lower() in desc.lower() for kw in usage_keywords)
        assert has_usage, (
            f"Description incomplete : '{desc}'\n"
            "La description doit indiquer quand utiliser l'outil "
            "(ex: 'Utilise cet outil pour toute question sur...')."
        )

    def test_description_length_sufficient(self):
        """La description doit etre assez longue pour etre informative (>= 80 chars)."""
        desc = get_tool_description()
        assert len(desc) >= 80, (
            f"Description trop courte ({len(desc)} chars) : '{desc}'\n"
            "Une description de moins de 80 caracteres est generalement trop vague "
            "pour que le LLM sache comment utiliser l'outil."
        )

    def test_description_mentions_input_format(self):
        """La description doit mentionner le format de l'input attendu."""
        desc = get_tool_description()
        input_keywords = ["input", "question", "mots-cles", "mots clés", "requete", "requête"]
        has_input = any(kw.lower() in desc.lower() for kw in input_keywords)
        assert has_input, (
            f"Description incomplete : '{desc}'\n"
            "La description doit mentionner le format de l'input attendu "
            "(ex: 'Input : question ou mots-cles en francais')."
        )
