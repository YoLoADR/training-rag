# Azure AI Search — CLI vs Portail (data Azure 2026)

> Le cœur conceptuel de l'atelier. À garder ouvert pendant le TP.

## Les deux plans d'API (LA clé)

Azure AI Search a **deux plans distincts** :

| Plan | Quoi | Outil |
|------|------|-------|
| **Control plane** | le SERVICE : créer/scaler/supprimer, clés, réseau | **CLI `az search`**, ARM/Bicep/Terraform |
| **Data plane** | le CONTENU : index, champs vectoriels, ingestion, requêtes | **SDK Python** `azure-search-documents` / REST |

> ⚠️ Le module `az search` ne touche QUE le service. **Il n'existe AUCUNE commande `az search`
> pour créer un index ou ingérer des documents.** Tout le RAG est en SDK/REST — donc 100%
> scriptable depuis le terminal, sans jamais ouvrir le portail.

## Tableau de synthèse CLI/SDK vs Portail

| Tâche | CLI / SDK | Portail obligatoire ? | Dans cet atelier |
|---|---|---|---|
| Groupe + service + clés | ✅ `az group create`, `az search service create`, `az search admin-key` | Non | **CLI** (`azure_provision.sh`, formateur) |
| Choisir le tier (free/basic/…) | ✅ `--sku` | Non | CLI ; **basic** partagé en classe |
| **Créer l'index vectoriel** | ✅ **SDK `SearchIndexClient`** (PAS `az search`) | Non | **SDK** (`build_index_schema` + `create_index`) |
| Ingérer les documents (push) | ✅ `AzureSearch.add_documents` / `SearchClient.upload_documents` | Non | SDK (`ingest_documents`) |
| Vectorisation intégrée (skillset+indexer+vectorizer) | ✅ REST/SDK (`api-version=2026-04-01` GA) | Non | hors scope (démo facultative) |
| Assistant « Import and vectorize data » | ❌ (no-code) | **Oui (portail)** | démo visuelle facultative |
| Configurer le semantic ranker | ✅ `SemanticConfiguration` (SDK, tier Basic+) | Non | bonus (`semantic_hybrid`) |
| Requêter vector/hybrid/semantic | ✅ SDK + **LangChain `AzureSearch`** | Non | SDK (`azure_search`) |
| Monitorer (latence, QPS, throttling) | ⚠️ Azure Monitor scriptable, mais lisible surtout au portail | Non strict | **Portail** (démo monitoring) |

## Le seul élément portail-only : le wizard « Import and vectorize data »

C'est un assistant no-code (portail) qui crée d'un coup data source + index + indexer + skillset.
Pratique pour prototyper, mais **non reproductible / non versionnable** → en atelier on fait
l'équivalent en SDK (reproductible, dans git). Tout ce que le wizard fait est faisable en REST/SDK.

## Coûts & garde-fous

- **Free tier** = 0 € mais **1 seul service par souscription**, 50 Mo, 3 index → on lui préfère
  **un service Basic partagé** en classe (1 service, N index, un par élève).
- Tier **Dedicated** (Free/Basic/S…) facturé à l'**heure dès la création** (pas à l'usage) →
  **toujours** `azure_teardown.sh` en fin de séance.
- Embeddings : ici **fastembed local 384d** → 0 coût token (pas d'Azure OpenAI).

## Monitoring (démo portail)

Portail Azure → ton service Search → **Overview** : Search latency, Queries per second,
Throttled queries. Utile pour montrer ce que le portail apporte VISUELLEMENT que le SDK ne
montre pas en un coup d'œil (mais Azure Monitor reste scriptable si besoin).

## Sources (learn.microsoft.com, 2026)
- Azure CLI Scripts (`az search`) : https://learn.microsoft.com/azure/search/search-manage-azure-cli
- Service tiers / limites : https://learn.microsoft.com/azure/search/search-sku-tier
- Integrated vectorization (REST) : https://learn.microsoft.com/azure/search/search-how-to-integrated-vectorization
- Import & vectorize wizard (portail) : https://learn.microsoft.com/azure/search/search-import-data-portal
- LangChain AzureSearch : https://python.langchain.com (intégration azure_ai_search / community)
