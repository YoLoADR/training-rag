"""
Azure AI Search — vector store MANAGÉ en cloud (Atelier 09).

Le concept central de l'atelier : control plane vs data plane.
  • CONTROL PLANE = le SERVICE (créer/scaler/clés) → CLI `az search` (cf. azure_provision.sh).
  • DATA PLANE    = le CONTENU (index, vecteurs, ingestion, requêtes) → SDK Python ici.
    Il n'existe AUCUNE commande `az search` pour le contenu : tout passe par le SDK/REST.

On crée le SCHÉMA d'index À LA MAIN (au lieu de laisser LangChain l'inférer) : c'est la vraie
leçon data-plane (champs, type vectoriel, dimension) et ça force la cohérence
dimension-schéma ↔ dimension-embedding (cf. Bug v1).

Embeddings : on RÉUTILISE fastembed (384 dims) d'AT02 → zéro dépendance Azure OpenAI, zéro
coût token. Le schéma fixe donc vector_search_dimensions=384.
"""

from homebutler import config
from homebutler.rag.vectorstore_faiss import get_embeddings

# Dimension de l'embedding fastembed paraphrase-multilingual-MiniLM-L12-v2.
# DOIT être égale à la dimension du champ vectoriel du schéma (sinon upload rejeté).
AZURE_VECTOR_DIM = 384

_DIFF = ("Solution : git diff student/09-azure-search atelier/09-azure-search "
         "-- homebutler/rag/vectorstore_azure.py")


def build_index_schema(index_name: str, dim: int = AZURE_VECTOR_DIM):
    """DATA PLANE — construit le schéma de l'index vectoriel (objet, hors-ligne).

    Champs alignés sur LangChain AzureSearch : id / content / content_vector / metadata.
    `content` DOIT être searchable=True (BM25 hybride) ; `content_vector` porte la dimension
    qui doit matcher l'embedding (384).

    --- Indice léger ---
    `SearchIndex(name=..., fields=[...], vector_search=VectorSearch(...))`.
    Importe les modèles depuis azure.search.documents.indexes.models.

    --- Indice fort ---
    fields = [
      SimpleField("id", String, key=True),
      SearchField("content", String, searchable=True),
      SearchField("content_vector", Collection(Single), searchable=True,
                  vector_search_dimensions=dim, vector_search_profile_name="hnsw-profile"),
      SearchableField("metadata", String),
    ]
    vector_search = VectorSearch(algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
        profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw")])
    return SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
    """
    raise NotImplementedError("Atelier 09 § Étape 1 — schéma d'index.\n" + _DIFF)


def get_search_index_client():
    """CONTROL/DATA PLANE — client de gestion des index (création de schéma)."""
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    return SearchIndexClient(
        endpoint=config.AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(config.AZURE_SEARCH_KEY),
    )


def create_index(index_name: str | None = None) -> None:
    """Crée (ou met à jour) l'index sur le service Azure à partir du schéma manuel."""
    index_name = index_name or config.AZURE_SEARCH_INDEX
    client = get_search_index_client()
    client.create_or_update_index(build_index_schema(index_name))


def get_azure_store(index_name: str | None = None, search_type: str = "hybrid"):
    """DATA PLANE — vector store LangChain branché sur l'index Azure existant.

    search_type ∈ {"similarity", "hybrid", "semantic_hybrid"}. "hybrid" est le bon défaut.

    --- Indice léger ---
    `from langchain_community.vectorstores.azuresearch import AzureSearch`.
    Passe l'embedding fastembed via embedding_function.

    --- Indice fort ---
    return AzureSearch(azure_search_endpoint=config.AZURE_SEARCH_ENDPOINT,
                       azure_search_key=config.AZURE_SEARCH_KEY,
                       index_name=index_name or config.AZURE_SEARCH_INDEX,
                       embedding_function=get_embeddings().embed_query,
                       search_type=search_type)
    """
    raise NotImplementedError("Atelier 09 § Étape 2 — vector store Azure.\n" + _DIFF)


def ingest_documents(documents, index_name: str | None = None) -> int:
    """Pousse des Documents LangChain dans l'index Azure (push API). Retourne le nombre."""
    store = get_azure_store(index_name)
    store.add_documents(documents=documents)
    return len(documents)


def azure_search(query: str, index_name: str | None = None, k: int = 4,
                 search_type: str = "hybrid") -> list:
    """Requête l'index Azure et retourne des Documents LangChain.

    --- Indice fort ---
    return get_azure_store(index_name, search_type=search_type).similarity_search(
        query, k=k, search_type=search_type)
    """
    raise NotImplementedError("Atelier 09 § Étape 2 — requête Azure.\n" + _DIFF)
