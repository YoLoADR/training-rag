"""
Test Bug v3 At.09 — champ `content` non searchable → 0 résultat en hybride

Logique :
- La recherche hybride utilise BM25 sur le champ texte `content`. Si `content` n'est pas
  `searchable=True`, BM25 ne peut pas l'indexer → l'index se construit, l'upload réussit, mais
  les requêtes hybrides renvoient 0 résultat (le volet mots-clés est muet).
- Test HORS-LIGNE : on construit le schéma et on vérifie que `content` est searchable.
- Bug actif : content.searchable=False → test ECHOUE.
- Corrigé : content.searchable=True → test PASSE.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))


def test_content_field_searchable():
    from homebutler.rag.vectorstore_azure import build_index_schema
    idx = build_index_schema("homebutler-test")
    content = next(f for f in idx.fields if f.name == "content")
    print(f"\ncontent.searchable = {content.searchable} (attendu True)")
    assert content.searchable is True, (
        "Le champ `content` n'est pas searchable → BM25 ne l'indexe pas → la recherche hybride "
        "renvoie 0 résultat (malgré un upload réussi).\n"
        "Indice : SearchField(name='content', ..., searchable=True)."
    )
