# Atelier 09 — Azure AI Search (demi-journée, ~3h30)

> Ici tu ne suis pas un step-by-step. Tu reçois une mission, des contraintes, des indices ;
> tu construis. Tu codes dans `homebutler/rag/vectorstore_azure.py`.
>
> **Module avancé — parcours industrialisation.** Pré-requis : AT02 (FAISS) + **compte Azure** + `az` installé.

---

## 🚦 Pré-vol (avant de commencer) — 20 min

- [ ] `bash scripts/check_atelier_ready.sh 09` retourne OK
- [ ] Corpus présent : `python scripts/generate_documents.py`
- [ ] Azure CLI installé : `az version`
- [ ] Connecté : `az login` puis `az account show` (à faire la VEILLE de préférence)
- [ ] Service provisionné : `bash ateliers/atelier-09-azure-search/azure_provision.sh`
  - écrit `AZURE_SEARCH_ENDPOINT` / `AZURE_SEARCH_KEY` dans `.env`
  - **en classe** : le service est PARTAGÉ → mets ton trigramme dans `AZURE_SEARCH_INDEX` (ex. `AZURE_SEARCH_INDEX=abc-homebutler`)
- [ ] J'ai lu `CLI-VS-PORTAIL.md` et la section "Périmètre"

> ⚠️ **Coût** : un service Azure Search Dedicated est facturé à l'heure dès sa création.
> À la fin : `bash ateliers/atelier-09-azure-search/azure_teardown.sh`.

---

## 🎯 La mission

Le CTO HomeButler te demande : **"Notre index FAISS est sur le laptop du dev. En production, je
veux un moteur de recherche MANAGÉ, scalable, en cloud. Migre vers Azure AI Search — et montre-moi
ce qui se fait en CLI vs ce qui passe par du code."**

**Livrable** : `python solution.py` (puis ton `exercice.py`) qui :
1. Crée un index vectoriel sur Azure (schéma à la main, SDK)
2. Ingère le corpus HomeButler (push API, embeddings fastembed 384d)
3. Requête en `similarity` / `hybrid` et compare au FAISS local

**Critères de succès auto-vérifiables** :
- L'index est créé avec `vector_search_dimensions=384` (= dimension fastembed)
- Une requête `hybrid` cite les bonnes sources HomeButler
- Tu sais dire ce qui est **control plane (CLI)** vs **data plane (SDK)**
- Les 3 bugs du Bug Hunt réparés (3× `pytest` vert)
- Ressources libérées (`azure_teardown.sh`)

**Budget temps** : 1h40 Core (+30 min Sprint OU 60-70 min Bonus)

---

## 🚧 Périmètre de cet atelier

- ✅ **Dans le scope** : `az search` (service), SDK `azure-search-documents` (schéma/index), LangChain `AzureSearch`, search_type similarity/hybrid/semantic_hybrid, dimension vectorielle, champ searchable, coût/teardown
- ❌ **Hors scope** (autres ateliers) : observabilité Langfuse/RAGAS (AT07), reranking (AT08), fine-tuning, Azure OpenAI embeddings (on reste sur fastembed local)
- 🛡️ **Garde-fou activé** : `.claude/CLAUDE.md` local + hook `UserPromptSubmit`

---

## 🛠️ vs 🎮 — Choisis ta piste

| Critère | 🛠️ Piste Build | 🎮 Piste Vibe |
|---|---|---|
| **Outil** | Code à la main ; Claude Code en `plan` | Délégation OK |
| **Obligation Build** | Lire `CLI-VS-PORTAIL.md` avant de coder | — |
| **Obligation Vibe** | (a) Expliquer control plane vs data plane | (b) Prédire l'effet de dim 1536 vs 384 avant le Bug Hunt v1 |
| **Bug Hunt** | Tu trouves le bug toi-même | Tu prédis l'effet avant de lire le test |

> **Obligation Vibe** : sache répondre "Pourquoi `az search` ne peut PAS créer un index ?"

---

## 🧠 Carnet de bord (concepts à mobiliser)

### Control plane vs data plane (LE concept)
Azure AI Search a deux plans d'API. Le **control plane** gère le SERVICE (créer, scaler, clés) → CLI `az search`. Le **data plane** gère le CONTENU (index, vecteurs, ingestion, requêtes) → SDK Python / REST.

**Analogie** : `az search` construit le BÂTIMENT de la bibliothèque (murs, électricité). Le SDK range les LIVRES sur les étagères et répond aux lecteurs. On ne range pas des livres avec une grue de chantier.

> ⚠️ Il n'existe AUCUNE commande `az search` pour créer un index ou ingérer. Tout le RAG est en SDK/REST → 100% scriptable au terminal.

### Schéma d'index vectoriel
La définition des champs : `id` (clé), `content` (texte recherchable BM25), `content_vector` (le vecteur, dimension fixée), `metadata` (source/page en JSON). On le crée À LA MAIN (data plane) pour maîtriser ces champs.

### Dimension vectorielle
La taille du vecteur, dictée par le modèle d'embedding : **384** pour fastembed MiniLM, 1536 pour text-embedding-3-small/ada-002. Le champ `content_vector` DOIT déclarer la même dimension, sinon Azure rejette l'upload.

### Champ searchable
`searchable=True` sur un champ texte = indexé pour BM25 (recherche plein-texte). Indispensable sur `content` pour que la recherche HYBRIDE fonctionne.

### search_type : similarity / hybrid / semantic_hybrid
- **similarity** : vecteur pur (sens)
- **hybrid** : vecteur + BM25 (mots-clés), fusionnés par RRF → rattrape vocabulaire divergent et termes exacts
- **semantic_hybrid** : hybrid + semantic ranker (tier Basic+, semantic config) → l'équivalent managé du reranking d'AT08

### Embeddings locaux (fastembed)
On réutilise fastembed (384d) d'AT02 via `embedding_function`. Zéro Azure OpenAI, zéro coût token. Le contenu est vectorisé côté Python, puis poussé.

### Coût & teardown
Tier Dedicated facturé à l'heure dès la création (pas à l'usage). `az group delete` supprime service + index → garde-fou coût.

---

## 🎯 TRONC COMMUN (1h40)

### Étape 1 — Le schéma d'index (data plane) (30 min)

**Objectif** : coder `build_index_schema()` avec la bonne dimension et `content` searchable.

**Indices (Build)** — dans `homebutler/rag/vectorstore_azure.py` :
- Champs : `SimpleField(id, key=True)`, `SearchField(content, searchable=True)`, `SearchField(content_vector, vector_search_dimensions=384, vector_search_profile_name="hnsw-profile")`, `SearchableField(metadata)`
- `VectorSearch(algorithms=[HnswAlgorithmConfiguration(name="hnsw")], profiles=[VectorSearchProfile("hnsw-profile", "hnsw")])`

✋ **Checkpoint 1** — `python ateliers/atelier-09-azure-search/checkpoints/check_1.py` (≥ 2/3)

---

### 🔬 Mini-lab — Lire CLI-VS-PORTAIL.md (10 min)

Ouvre `CLI-VS-PORTAIL.md`. Pour chaque tâche du tableau, dis à voix haute : CLI, SDK, ou portail ?
**Question** : quelle est la SEULE tâche portail-only ? (réponse : le wizard « Import and vectorize data », et il est remplaçable par SDK).

---

### Étape 2 — Créer, ingérer, requêter (data plane) (30 min)

**Objectif** : `get_azure_store()` + `azure_search()`, puis ingérer et comparer 3 modes.

**Indices (Build)** :
- `get_azure_store` : `AzureSearch(azure_search_endpoint=..., azure_search_key=..., index_name=..., embedding_function=get_embeddings().embed_query, search_type="hybrid")`
- `azure_search` : `get_azure_store(index_name, search_type).similarity_search(query, k=k, search_type=search_type)`
- Dans `exercice.py` : `create_index()`, `ingest_documents(_load_chunks())`, boucle requêtes

**Observation attendue** : sur une question à vocabulaire divergent, `hybrid` cite la bonne source là où `similarity` peut rater.

---

### 🐛 Casse-moi ça — Bug Hunt (20 min)

Bugs dans `homebutler/rag/vectorstore_azure.py`. Reset : `git checkout -- homebutler/rag/vectorstore_azure.py`.
Les tests sont **hors-ligne** (pas besoin du service Azure).

**Bug v1 — dimension 1536 ≠ embedding 384**
```bash
git apply ateliers/atelier-09-azure-search/bugs/v1.patch
pytest ateliers/atelier-09-azure-search/bugs/test_v1.py -v   # ECHOUE
git checkout -- homebutler/rag/vectorstore_azure.py
pytest ateliers/atelier-09-azure-search/bugs/test_v1.py -v   # PASSE
```
Lis `bugs/v1_explanation.md`.

**Bug v2 — search_type "similarity" au lieu de "hybrid"**
```bash
git apply ateliers/atelier-09-azure-search/bugs/v2.patch
pytest ateliers/atelier-09-azure-search/bugs/test_v2.py -v
git checkout -- homebutler/rag/vectorstore_azure.py
pytest ateliers/atelier-09-azure-search/bugs/test_v2.py -v
```
Lis `bugs/v2_explanation.md`.

**Bug v3 — `content` non searchable → 0 résultat en hybride**
```bash
git apply ateliers/atelier-09-azure-search/bugs/v3.patch
pytest ateliers/atelier-09-azure-search/bugs/test_v3.py -v
git checkout -- homebutler/rag/vectorstore_azure.py
pytest ateliers/atelier-09-azure-search/bugs/test_v3.py -v
```
Lis `bugs/v3_explanation.md`.

> **Règle anti-cheat** : demande à l'IA d'expliquer le symptôme, pas « trouve le bug ».

---

### 📊 Mesure-toi (15 min)

| Question | similarity | hybrid | FAISS local |
|---|---|---|---|
| "Quelle est la marque de ma chaudière ?" | ✓/✗ | ✓/✗ | ✓/✗ |
| "Mon linge ressort trempé" | ✓/✗ | ✓/✗ | ✓/✗ |
| "Jusqu'à quelle heure faire du bruit ?" | ✓/✗ | ✓/✗ | ✓/✗ |

**Interprétation** : sur quelles questions `hybrid` bat-il `similarity` ? Azure (managé) vs FAISS (local) : quels compromis (coût, latence, ops, scalabilité) ?

✋ **Checkpoint final** — `python ateliers/atelier-09-azure-search/checkpoints/check_final.py` (≥ 4/5 Bonus, < 3/5 Sprint)

> 🧹 **Avant de partir** : `bash ateliers/atelier-09-azure-search/azure_teardown.sh`

---

## ⚡ SPRINT (chemin alternatif, 30 min)

**Sprint 1 — Control vs data plane (15 min)** : liste 3 tâches faites en `az search` et 3 faites en SDK. Pourquoi cette séparation ?
**Sprint 2 — Dimension (15 min)** : explique par écrit ce qui se passe si le schéma déclare 1536 et l'embedding fait 384. Comment vérifier la dimension de fastembed ?

---

## 🏆 BONUS (60-70 min)

### Défi Bonus 1 — semantic_hybrid (semantic ranker)
**POURQUOI ?** C'est l'équivalent managé du reranking d'AT08. **Question** : ajoute une semantic
configuration au schéma, active `search_type="semantic_hybrid"` (tier Basic+), compare à `hybrid`
sur les questions en langage naturel. Le semantic ranker améliore-t-il le classement de tête ?

### Défi Bonus 2 — FAISS vs Azure : grille de décision
**POURQUOI ?** Choisir local vs managé est une décision d'archi. **Question** : remplis une grille
(coût, latence, scalabilité, ops, souveraineté des données, lock-in) FAISS local vs Azure AI Search.
Pour HomeButler en early-stage, lequel recommandes-tu et pourquoi ?

---

## 🎓 Wrap-up (10 min)

**Checklist** :
- [ ] Index créé avec dim 384, `content` searchable
- [ ] Requête `hybrid` cite les bonnes sources
- [ ] 3 bugs réparés (3× pytest vert)
- [ ] Checkpoint final ≥ 60%
- [ ] **Ressources libérées (`azure_teardown.sh`)**

**Quiz oral (5 min, 10 questions)** :
1. Control plane vs data plane ?
2. Quelle tâche est portail-only ?
3. Pourquoi `az search` ne crée-t-il pas d'index ?
4. Quelle dimension vectorielle et pourquoi ?
5. Que se passe-t-il si dim_schema ≠ dim_embedding ?
6. Différence similarity / hybrid / semantic_hybrid ?
7. À quoi sert `searchable=True` sur `content` ?
8. Pourquoi un service Basic partagé en classe (vs Free) ?
9. Pourquoi le teardown en fin de séance ?
10. Pourquoi fastembed local plutôt qu'Azure OpenAI ici ?

→ ≥ 8/10 : tu maîtrises Azure AI Search. 5-7 : relis le Carnet. < 5 : refais le Sprint.

**Ce que je retiens en 3 lignes** :
```
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________
```

---

## 🔗 Pour aller plus loin (hors TP, lecture)

**Pont avec ton projet** : migrer un index local vers un service managé est un classique du passage
en prod. La clé est de comprendre QUI fait QUOI (service en CLI/IaC, contenu en SDK versionné).

**Avertissements** :
- Tier Dedicated facturé à l'heure dès la création → toujours teardown
- Free tier = 1 service/souscription → service partagé en classe
- Dimension schéma = dimension embedding, sans exception
- `searchable=False` ne plante pas à l'ingestion : bug silencieux à la requête

**Lectures** :
- Azure AI Search — vector search : https://learn.microsoft.com/azure/search/vector-search-overview
- `az search` (control plane) : https://learn.microsoft.com/azure/search/search-manage-azure-cli
- LangChain AzureSearch : https://python.langchain.com
