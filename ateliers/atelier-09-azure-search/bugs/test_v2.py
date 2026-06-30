"""
Test Bug v2 At.09 — search_type "similarity" au lieu de "hybrid"

Logique :
- "hybrid" combine BM25 (mots-clés) + recherche vectorielle (sens), fusionnés par RRF. Sur des
  questions au vocabulaire divergent des documents, c'est nettement meilleur que le vecteur seul.
- Le bug met le défaut de get_azure_store à "similarity" (vecteur pur) → recall dégradé.
- Test d'analyse statique (hors-ligne, déterministe) : le défaut doit être "hybrid".
- Bug actif : défaut "similarity" → test ECHOUE.
- Corrigé : défaut "hybrid" → test PASSE.
"""

import inspect
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))


def test_get_azure_store_defaut_hybrid():
    from homebutler.rag import vectorstore_azure
    src = inspect.getsource(vectorstore_azure.get_azure_store)
    print(f"\nSignature get_azure_store :\n{src.splitlines()[0]}")
    assert 'search_type: str = "hybrid"' in src, (
        "Le défaut de get_azure_store n'est pas 'hybrid'.\n"
        "La recherche hybride (BM25 + vecteurs, fusion RRF) rattrape le vocabulaire divergent "
        "que le vecteur seul ('similarity') rate.\n"
        "Indice : search_type: str = \"hybrid\"."
    )
