# Atelier 09 — Azure AI Search (module avancé — parcours industrialisation)

> **Chapitre formation** : RAG avec Azure AI Search
> **Branche** : `atelier/09-azure-search`
> **Durée** : ~3h30 (demi-journée) — module optionnel, après AT02
> **Pré-requis** : AT02 (RAG/FAISS) + **compte Azure** + Azure CLI (`az`) installé

## Objectif pédagogique

Passer du vector store LOCAL (FAISS) à un vector store MANAGÉ en cloud (Azure AI Search), en
comprenant LA distinction structurante :
- **Control plane** (CLI `az search`) = le SERVICE (créer, scaler, clés).
- **Data plane** (SDK Python `azure-search-documents` / LangChain) = le CONTENU (index, vecteurs,
  ingestion, requêtes). **Aucune commande `az search` pour le contenu.**

C'est ce qui rend l'atelier réalisable 100% au terminal (cf. `CLI-VS-PORTAIL.md`).

## Pré-requis techniques

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_atelier09.txt && pip install -e .
python scripts/generate_documents.py
# Azure : compte + CLI
az login                                  # device code (interactif) — la veille de préférence
bash ateliers/atelier-09-azure-search/azure_provision.sh   # crée le service, écrit .env
```

## Décisions clés (issues de l'audit)

- **Quota Free = 1 service par souscription** → en classe, **1 service Basic PARTAGÉ** créé par le
  formateur, chaque élève crée **SON index** (`AZURE_SEARCH_INDEX=<trigramme>`). Pas de blocage quota.
- **Embeddings fastembed local 384d** (réutilisés d'AT02) → **0 dépendance Azure OpenAI, 0 coût token**.
- **Schéma créé À LA MAIN** (SDK `SearchIndexClient`) — c'est la leçon data-plane ET ça rend le
  Bug v1 (dimension) réel (sinon LangChain inférerait 384 et masquerait le bug).
- Schéma aligné sur les champs LangChain (`id/content/content_vector/metadata`) → `add_documents` marche.
- **Teardown obligatoire** : tier Dedicated facturé à l'heure dès la création → `azure_teardown.sh` en fin.

## Lancer

```bash
python ateliers/atelier-09-azure-search/solution.py    # crée index + ingère + requête 3 modes vs FAISS
bash ateliers/atelier-09-azure-search/azure_teardown.sh
```

## Ce que l'élève code (`homebutler/rag/vectorstore_azure.py`)

- `build_index_schema()` — schéma vectoriel (dim 384, content searchable, profil HNSW)
- `get_azure_store()` — `AzureSearch(... embedding_function=fastembed, search_type="hybrid")`
- `azure_search()` — requête en 3 modes

`create_index` / `ingest_documents` / `get_search_index_client` sont fournis (thin wrappers).

## Bug Hunt (cible vectorstore_azure.py, tests HORS-LIGNE)

| Patch | Bug | Symptôme | Fix |
|---|---|---|---|
| v1 | `AZURE_VECTOR_DIM=1536` ≠ embedding 384 | upload rejeté par Azure | 384 |
| v2 | `get_azure_store` défaut "similarity" | recall dégradé (pas de BM25) | "hybrid" |
| v3 | `content` searchable=False | hybride renvoie 0 résultat (silencieux) | searchable=True |

> Les 3 tests sont **déterministes et hors-ligne** (construction du schéma + analyse statique) :
> `pytest ateliers/atelier-09-azure-search/bugs/ -v` → 3 passed, **sans service Azure**.

## Note de vérification

Le run end-to-end (create_index/ingest/query) nécessite un **service Azure réel** → c'est le
formateur qui l'exécute après `azure_provision.sh`. Tout le reste (imports, schéma, bug tests)
est vérifiable sans Azure.

→ **Fin du parcours avancé** (07 mesurer · 08 améliorer · 09 industrialiser).
