# GUIDE FORMATEUR — Atelier 09 : Azure AI Search (~3h30)

> Guide destiné au formateur. L'élève n'y a pas accès.
> **Module avancé optionnel** (parcours industrialisation) — nécessite un compte Azure.

---

## 1. Ce que l'élève doit comprendre à la fin

- **Control plane vs data plane** : `az search` gère le SERVICE ; le SDK gère le CONTENU
  (index, vecteurs, ingestion, requêtes). Aucune commande `az search` pour le contenu.
- La **dimension** du champ vectoriel = dimension de l'embedding (384 pour fastembed).
- `searchable=True` sur `content` est requis pour le volet BM25 de la recherche **hybride**.
- Les modes **similarity / hybrid / semantic_hybrid** et quand les utiliser.
- Le **coût** (facturation horaire Dedicated) → teardown obligatoire.

**Hors scope** : observabilité (AT07), reranking (AT08), Azure OpenAI embeddings. Le hook bloque ces mots-clés.

---

## 1.bis Carte des blancs — navigation rapide formateur

> `git checkout student/09-azure-search` puis ouvre `homebutler/rag/vectorstore_azure.py`.
> Les `raise NotImplementedError` sont dans CE fichier + les TODO dans `exercice.py`.

### `homebutler/rag/vectorstore_azure.py`

| Fonction | Ce que l'élève écrit | Pourquoi |
|---|---|---|
| `build_index_schema(name, dim=384)` | champs id/content(searchable)/content_vector(dim 384)/metadata + VectorSearch HNSW | data plane : le schéma. dim=384 = fastembed. content searchable = BM25 hybride |
| `get_azure_store(index, search_type="hybrid")` | `AzureSearch(endpoint, key, index, embedding_function=fastembed, search_type)` | brancher LangChain sur l'index ; défaut hybrid |
| `azure_search(q, index, k, search_type)` | `get_azure_store(...).similarity_search(q, k, search_type)` | requête |

Fournis (thin) : `get_search_index_client`, `create_index`, `ingest_documents`.

### Vérifier l'état
```bash
git checkout student/09-azure-search
grep -n "raise NotImplementedError" homebutler/rag/vectorstore_azure.py
```

---

## 2. Setup formateur — avant l'atelier

```bash
git checkout atelier/09-azure-search
source .venv/bin/activate
pip install -r requirements_atelier09.txt && pip install -e .
python scripts/generate_documents.py
# Azure (LA VEILLE) :
az login
bash ateliers/atelier-09-azure-search/azure_provision.sh    # crée le service, écrit .env
```

### Stratégie compte/quota (IMPORTANT)
- **Free tier = 1 service par souscription** → 15 élèves sur une souscription = un seul `create`
  réussit. **Solution retenue** : le formateur crée **1 service Basic PARTAGÉ**
  (`AZ_SEARCH_SKU=basic bash azure_provision.sh`), puis chaque élève crée **SON index** via
  `AZURE_SEARCH_INDEX=<trigramme>` dans son `.env`. 1 service, N index.
- Le PDF Ambient IT exige déjà « Maîtriser Azure » + un compte → à confirmer à l'inscription (Qualiopi).
- `az login` interactif (device code) : à faire **la veille**, pas en live ×15.

### Test de fumée
```bash
# Bug tests : HORS-LIGNE, déterministes, PAS besoin d'Azure
pytest ateliers/atelier-09-azure-search/bugs/ -v          # 3 passed
# Run complet (nécessite le service Azure provisionné) :
python ateliers/atelier-09-azure-search/solution.py
bash ateliers/atelier-09-azure-search/azure_teardown.sh
```

> ⚠️ Sans service Azure, `solution.py` s'arrête proprement sur « Service Azure non configuré ».
> Les bug tests et la construction de schéma tournent SANS Azure.

---

## 3. Déroulé détaillé

| Bloc | Durée | Contenu |
|---|---|---|
| Slides | 30 min | control/data plane, schéma, dimension, hybrid, coût |
| Démo live | 20 min | az search (service) + SDK (index/ingest/query) + portail (monitoring) |
| Passage de relais | 5 min | commandes student/09 + trigramme index |
| Core élève | 1h40 | schéma + store + requêtes |
| Bug Hunt | 20 min | 3 bugs (hors-ligne) |
| Mesure + Checkpoint | 15 min | tableau 3 modes + check_final |
| Sprint OU Bonus | 30-70 min | selon score |

### Démo live (T+30)
```bash
git checkout atelier/09-azure-search
# CONTROL PLANE (CLI) — montrer que az gère le SERVICE :
az search service show --name <svc> --resource-group rg-atelier-rag -o table
# DATA PLANE (SDK) — montrer que le contenu est en Python :
python ateliers/atelier-09-azure-search/solution.py
```
- Ouvre `CLI-VS-PORTAIL.md` → projette le tableau. Martèle : « az search ≠ RAG ».
- Montre `build_index_schema` → pointe `vector_search_dimensions=384` (= fastembed) et `content` searchable.
- Quand solution tourne, pointe une question où `hybrid` bat `similarity`.
- Ouvre le PORTAIL (Overview du service) → montre latence/QPS : ce que le portail apporte visuellement.

### Passage de relais (T+50)
```bash
git checkout student/09-azure-search
# chaque élève : AZURE_SEARCH_INDEX=<trigramme> dans .env
grep -n "raise NotImplementedError" homebutler/rag/vectorstore_azure.py
```
Annonce : **« 1h40. Service Basic PARTAGÉ, ton index = ton trigramme. Teardown en fin. »**

---

## 4. Bug Hunt — concret (hors-ligne)

> Reset : `git checkout -- homebutler/rag/vectorstore_azure.py`. Tests sans Azure.

- **v1 (dimension)** : `AZURE_VECTOR_DIM=1536`. `test_v1` construit le schéma, vérifie dims==384.
  Question : « d'où vient la dimension 384 ? » (de l'embedding fastembed).
- **v2 (search_type)** : défaut "similarity". `test_v2` (statique) vérifie le défaut "hybrid".
  Question : « que perd-on sans BM25 ? » (les correspondances de termes exacts).
- **v3 (searchable)** : `content` searchable=False. `test_v3` vérifie content.searchable.
  Question : « pourquoi aucune erreur à l'ingestion mais 0 résultat à la requête ? » (BM25 muet).

Après chaque bug, faire lire `bugs/vN_explanation.md`.

---

## 5. Checkpoints
- `check_1.py` — 3 QCM (control/data plane, dimension, hybrid). Seuil 2/3.
- `check_final.py` — 5 QCM. ≥4/5 Bonus, <3/5 Sprint.

---

## 6. Questions fréquentes

**"Quota exceeded à la création"** → Free = 1 service/souscription. Utiliser le service Basic
partagé + index par trigramme. Ne PAS créer un service par élève sur la même souscription Free.
**"az login ne marche pas en classe"** → device code interactif : à valider la veille.
**"add_documents échoue (champ manquant)"** → le schéma doit aligner id/content/content_vector/metadata
(noms LangChain). C'est le cas dans build_index_schema fourni.
**"hybrid renvoie 0 résultat"** → `content` non searchable (Bug v3) ou index vide (ingestion non faite).
**"Combien ça coûte ?"** → Dedicated facturé à l'heure dès la création. Quelques heures de Basic =
quelques dizaines de centimes à ~1 €, À CONDITION de teardown. Embeddings = fastembed local = 0 €.
**"Peut-on tout faire sans le portail ?"** → Oui sauf le wizard « Import and vectorize data »
(no-code, portail), remplacé par le SDK. Le monitoring est plus lisible au portail mais scriptable
via Azure Monitor.

---

## 7. Signaux d'alerte (élève bloqué)
- **Cherche à créer l'index via `az search`** → STOP : c'est du SDK (data plane). Analogie grue/livres.
- **Met dim 1536 "par habitude"** → rappeler que la dim vient de l'embedding (384).
- **hybrid vide** → vérifier ingestion faite + content searchable + bon index_name (trigramme).
- **Oublie le teardown** → coût ; rappeler systématiquement en fin.

---

## 8. Transition / clôture du parcours avancé

AT09 clôt le parcours « industrialisation » : 07 (mesurer) → 08 (améliorer) → 09 (cloud managé).
Phrase de clôture : « On sait maintenant mesurer la qualité, l'améliorer, et déployer le retrieval
sur un service managé. C'est la boucle complète d'un RAG de production. »

Ne pas oublier : faire lancer `azure_teardown.sh` à TOUS les élèves avant de partir (coût).
