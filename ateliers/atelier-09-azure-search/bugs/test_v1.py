"""
Test Bug v1 At.09 — dimension du schéma (1536) ≠ dimension de l'embedding (384)

Logique :
- On utilise fastembed (paraphrase-multilingual-MiniLM-L12-v2) → vecteurs de 384 dims.
- Le champ vectoriel du schéma DOIT déclarer vector_search_dimensions=384. Le bug le met à
  1536 (valeur copiée d'un exemple Azure OpenAI text-embedding-ada-002) → à l'ingestion réelle,
  Azure REJETTE l'upload (longueur du vecteur ≠ dimension du champ).
- Test HORS-LIGNE (pas de service Azure requis) : on construit le schéma et on vérifie la dim.
- Bug actif : dims=1536 → test ECHOUE.
- Corrigé : dims=384 → test PASSE.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))


def test_dimension_schema_egale_embedding():
    from homebutler.rag.vectorstore_azure import build_index_schema
    idx = build_index_schema("homebutler-test")
    vector_field = next(f for f in idx.fields if f.name == "content_vector")
    print(f"\nvector_search_dimensions = {vector_field.vector_search_dimensions} (attendu 384)")
    assert vector_field.vector_search_dimensions == 384, (
        f"Dimension du schéma = {vector_field.vector_search_dimensions}, mais l'embedding "
        "fastembed produit des vecteurs de 384.\n"
        "À l'ingestion, Azure rejette l'upload si dim_schema ≠ dim_embedding.\n"
        "Indice : AZURE_VECTOR_DIM doit valoir 384 (1536 = dimension d'un embedding OpenAI)."
    )
