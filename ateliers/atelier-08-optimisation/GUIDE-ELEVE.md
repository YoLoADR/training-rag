# Atelier 08 — Optimisation du pipeline RAG (demi-journée, ~3h30)

> Ici tu ne suis pas un step-by-step. Tu reçois une mission, des contraintes, des indices ;
> tu construis. Si tu cherches le tuto, ouvre `homebutler/rag/reranking.py` — mais alors
> tu n'apprends pas.
>
> **Module avancé — parcours industrialisation.** Pré-requis : AT02 (FAISS) + AT03 (retriever).

---

## 🚦 Pré-vol (avant de commencer) — 20 min

- [ ] `bash scripts/check_atelier_ready.sh 08` retourne OK
- [ ] Les PDFs sont présents dans `data/documents/` (sinon : `python scripts/generate_documents.py`)
- [ ] L'index FAISS existe (sinon il sera construit au 1er run de `exercice.py`)
- [ ] Le reranker flashrank est téléchargé :
  ```bash
  python -c "from flashrank import Ranker; Ranker(model_name='ms-marco-MiniLM-L-12-v2')"
  ```
  (~34 Mo ONNX, CPU — cache local, une seule fois)
- [ ] `ANTHROPIC_API_KEY` présente dans `.env` OU `LLM_PROVIDER=ollama` (utile pour multi-query/HyDE ; le reranking n'a PAS besoin de LLM)
- [ ] J'ai lu la section "Périmètre" ci-dessous

---

## 🎯 La mission

Le CTO HomeButler te demande : **"Notre RAG trouve souvent la bonne notice, mais le bon
passage n'est pas toujours en tête — surtout quand l'utilisateur parle avec ses mots à lui.
Améliore la PRÉCISION du retrieval, et prouve-le avec des chiffres."**

**Livrable** : une démo CLI (`python exercice.py`) qui :
1. Mesure la baseline (FAISS seul) : Recall@1/@3/@5 + MRR
2. Ajoute un reranking cross-encoder (flashrank) en entonnoir base_k=20 → top_n=5
3. Affiche le GAIN (ΔRecall@1, ΔMRR) sur des questions en langage naturel

**Critères de succès auto-vérifiables** :
- Le reranking améliore **Recall@1** d'au moins +20 points sur le jeu de questions naturelles
- Le reranking améliore **MRR** (ordre de tête) de façon visible (≈ +0.2)
- Les 3 bugs du Bug Hunt réparés (3× `pytest` vert)
- `bash scripts/verify_branch_scope.sh` passe

**Budget temps** : 1h40 Core (+30 min Sprint OU 60-70 min Bonus)

---

## 🚧 Périmètre de cet atelier

- ✅ **Dans le scope** : reranking cross-encoder (flashrank), bi vs cross-encoder, entonnoir `base_k`/`top_n`, `ContextualCompressionRetriever`, multi-query, HyDE, métriques Recall@1/@3/@5 et MRR
- ❌ **Hors scope** (autres ateliers) : observabilité Langfuse/RAGAS (AT07), Azure AI Search (AT09), fine-tuning, déploiement API
- 🛡️ **Garde-fou activé** : `.claude/CLAUDE.md` local + hook `UserPromptSubmit`
  (demander "ajoute Langfuse" ou "passe sur Azure" déclenchera un refus automatique — c'est intentionnel)
- ⛔ **Ne modifie PAS** `homebutler/rag/retriever.py` (code AT03 réutilisé tel quel). Tu codes dans `homebutler/rag/reranking.py`.

---

## 🛠️ vs 🎮 — Choisis ta piste

| Critère | 🛠️ Piste Build | 🎮 Piste Vibe |
|---|---|---|
| **Outil** | Code à la main ; Claude Code en mode `plan` ou fermé | Délégation OK à Claude/Cursor |
| **Liberté** | Tu décides tout | Tu valides ce que l'IA produit |
| **Obligation Build** | Lire `homebutler/rag/retriever.py` (ce que tu réutilises) avant de coder | — |
| **Obligation Vibe** | (a) Expliquer l'entonnoir `base_k ≫ top_n` en 3 phrases | (b) Prédire l'effet de `base_k=top_n` avant de lancer le Bug Hunt v1 |
| **Bug Hunt** | Tu trouves le bug toi-même (observe avant de lire le patch) | Tu prédis l'effet du bug avant de regarder le test |

> **Piste Vibe — obligation contractuelle** : avant de valider une étape générée par l'IA,
> tu dois savoir répondre : "Pourquoi le cross-encoder est-il plus précis mais plus lent que
> le bi-encodeur ? Pourquoi ne l'applique-t-on qu'à `base_k` candidats ?"

---

## 🧠 Carnet de bord (concepts à mobiliser)

> Lis ce lexique avant de coder. Il sera testé dans les checkpoints.

### Bi-encodeur (embeddings)
Encode la question et chaque chunk **séparément** en vecteurs, puis compare par similarité
(cosinus). Rapide et scalable : on pré-calcule les vecteurs des chunks une fois pour toutes,
la recherche est en O(log n) via FAISS.

**Analogie** : juger deux personnes compatibles en lisant leurs deux CV séparément, sans
jamais les faire se rencontrer. Rapide, mais on rate les subtilités de l'interaction.

**Dans le projet** : `get_faiss_retriever()` (AT02/AT03) = bi-encodeur.

### Cross-encoder (reranker)
Lit la **paire** (question, chunk) **ensemble** et sort un score de pertinence. Bien plus
précis (il voit l'interaction des mots) mais lent : un forward pass par paire. On ne peut
donc PAS l'appliquer à tout le corpus — seulement à un petit pool de candidats.

**Analogie** : faire passer un **entretien** à chaque candidat (question + CV ensemble).
Précis, mais on ne peut le faire qu'avec une shortlist.

**Dans le projet** : `FlashrankRerank` (modèle ms-marco-MiniLM-L-12-v2, ONNX, CPU).

### L'entonnoir (base_k ≫ top_n)
On récupère LARGE avec le bi-encodeur (`base_k=20` candidats), puis le cross-encoder
reclasse et ne garde que les meilleurs (`top_n=5`).

**Analogie** : présélection sur CV (20 candidats), puis entretiens pour garder les 5
meilleurs. Si tu présélectionnes seulement 5 et en gardes 5, l'entretien ne sert plus
à filtrer — juste à les remettre dans un autre ordre.

**Règle** : `base_k` ≈ 4 à 10 × `top_n`.

### ContextualCompressionRetriever
Le wrapper LangChain qui combine les 2 étages : `base_retriever` (étage 1) + `base_compressor`
(étage 2 = le reranker). `retriever.invoke(q)` renvoie directement les `top_n` rerankés.

### MultiQueryRetriever
Le LLM reformule la question en N variantes (en UN seul appel), on récupère pour chacune,
puis on prend l'UNION des documents. Augmente le **rappel** quand le vocabulaire de
l'utilisateur diverge de celui des documents.

**Point clé** : la diversité vient du **PROMPT** (on demande N reformulations), PAS de la
température. On garde `temperature=0` pour la reproductibilité.

### HyDE (Hypothetical Document Embeddings)
On demande au LLM de générer une **réponse hypothétique** à la question, puis on embedde ce
paragraphe (au lieu de la question) pour la recherche. Le paragraphe ressemble davantage aux
chunks cibles → meilleur rappel sur questions vagues.

### Recall@k et MRR
- **Recall@k** : sur N questions, combien ont le bon document dans les k premiers.
- **MRR** (Mean Reciprocal Rank) : moyenne de 1/rang du premier bon document. 1.0 = toujours
  en tête, 0.5 = en moyenne au 2e rang.

**Pourquoi MRR ici ?** Le reranking remonte le bon chunk vers le **sommet**. Sur un petit
corpus, Recall@5 sature (le bon doc est presque toujours dans le top-5) — c'est **Recall@1
et MRR** qui révèlent le gain.

---

## 🎯 TRONC COMMUN (1h40)

### Étape 1 — Coder le reranking et mesurer la baseline (35 min)

**Objectif** : implémenter `get_reranked_retriever()` et mesurer la baseline FAISS.

**Indices (Build)** :
- Fichier à compléter : `homebutler/rag/reranking.py` → `get_reranked_retriever(base_k, top_n)`
- Briques :
  ```python
  from langchain.retrievers import ContextualCompressionRetriever
  from langchain_community.document_compressors import FlashrankRerank
  base_retriever = get_faiss_retriever(k=base_k, fetch_k=max(base_k, 20))
  compressor = FlashrankRerank(model="ms-marco-MiniLM-L-12-v2", top_n=top_n)
  return ContextualCompressionRetriever(base_compressor=compressor, base_retriever=base_retriever)
  ```
- Puis dans `exercice.py` : TODO 1 (import) + lance la baseline fournie

**Garde-fou (Vibe)** :
- Consigne : "Implémente get_reranked_retriever dans reranking.py. Réutilise get_faiss_retriever, ne modifie PAS retriever.py. Pas de Langfuse, pas d'Azure."
- Après génération : explique pourquoi `base_k=20` et `top_n=5` (et pas 5/5)

**Observation attendue (baseline)** :
```
── BASELINE FAISS k=5
   Recall@1 = 40%   Recall@3 = 90%   Recall@5 = 90%   MRR = 0.617
```

✋ **Checkpoint 1** — `python ateliers/atelier-08-optimisation/checkpoints/check_1.py`
→ Score ≥ 2/3 : continue · Score < 2/3 : relis le Carnet (bi/cross-encoder, entonnoir)

---

### 🔬 Mini-lab — Faire varier base_k (15 min)

**Variable** : `base_k` (taille du pool de candidats) avec `top_n=5` fixe.
**Plage** : `base_k ∈ {5, 10, 20, 40}`

**Protocole** : pour chaque `base_k`, mesure Recall@1 et MRR du retriever reranké.

| base_k | Recall@1 | MRR | latence/req |
|---|---|---|---|
| 5 (== top_n) | ? | ? | ? |
| 10 | ? | ? | ? |
| 20 | ? | ? | ? |
| 40 | ? | ? | ? |

**Questions à te poser** :
- À partir de quel `base_k` le gain plafonne-t-il ?
- Que vaut le reranking quand `base_k == top_n` (=5) ? Pourquoi ?
- Le gain en MRR justifie-t-il la latence supplémentaire à `base_k=40` ?

---

### Étape 2 — Mesurer le gain et brancher le multi-query (30 min)

**Objectif** : comparer baseline vs reranké, puis tester le multi-query.

**Indices (Build)** :
- `exercice.py` TODO 2-3 : construire `get_reranked_retriever(base_k=20, top_n=5)`, le scorer, afficher ΔRecall@1 / ΔMRR
- `get_multiquery_retriever(k=4)` : `MultiQueryRetriever.from_llm(retriever=..., llm=get_llm(temperature=0), prompt=MULTIQUERY_PROMPT)`

**Observation attendue (gain)** :
```
── FAISS+flashrank
   Recall@1 = 70%   Recall@3 = 100%   Recall@5 = 100%   MRR = 0.833
GAIN : ΔRecall@1 = +30%   ΔMRR = +0.217
```

> Si tu n'as pas de clé LLM, le reranking se mesure quand même (il n'utilise pas de LLM).
> Seuls multi-query et HyDE nécessitent un LLM joignable.

---

### 🐛 Casse-moi ça — Bug Hunt (20 min)

**3 bugs à débusquer.** Applique le patch, observe, répare, valide avec pytest.

**Bug v1 — base_k == top_n (l'entonnoir est cassé)**
```bash
git apply ateliers/atelier-08-optimisation/bugs/v1.patch
pytest ateliers/atelier-08-optimisation/bugs/test_v1.py -v   # doit ECHOUER
# Observe : le pool de candidats == la sortie → le reranker ne filtre plus
# Répare : RERANK_BASE_K doit rester ≫ RERANK_TOP_N
git checkout -- homebutler/rag/reranking.py
pytest ateliers/atelier-08-optimisation/bugs/test_v1.py -v   # doit PASSER
```
Lis `bugs/v1_explanation.md`.

**Bug v2 — multi-query qui ne demande qu'une reformulation**
```bash
git apply ateliers/atelier-08-optimisation/bugs/v2.patch
pytest ateliers/atelier-08-optimisation/bugs/test_v2.py -v
# Observe : plus de diversité de requêtes — la diversité vient du PROMPT
git checkout -- homebutler/rag/reranking.py
pytest ateliers/atelier-08-optimisation/bugs/test_v2.py -v
```
Lis `bugs/v2_explanation.md`.

**Bug v3 — top_n non transmis au reranker**
```bash
git apply ateliers/atelier-08-optimisation/bugs/v3.patch
pytest ateliers/atelier-08-optimisation/bugs/test_v3.py -v
# Observe : la sortie a 3 docs (défaut flashrank) au lieu de 5
git checkout -- homebutler/rag/reranking.py
pytest ateliers/atelier-08-optimisation/bugs/test_v3.py -v
```
Lis `bugs/v3_explanation.md`.

> **Règle anti-cheat** : tu peux demander à l'IA d'expliquer le comportement observé, pas
> "trouve le bug dans le patch". La déduction depuis le symptôme EST l'apprentissage.

---

### 📊 Mesure-toi (15 min)

Lance la solution complète et remplis le tableau :

```bash
python ateliers/atelier-08-optimisation/solution.py
```

| Métrique | Baseline | + Reranking | Cible |
|---|---|---|---|
| **Recall@1** | ___% | ___% | reranké ≥ baseline +20 pts |
| **Recall@3** | ___% | ___% | — |
| **Recall@5** | ___% | ___% | — |
| **MRR** | ___ | ___ | reranké > baseline (≈ +0.2) |

**Interprétation** :
- Si ΔRecall@1 ≈ 0 → vérifie que `base_k ≫ top_n` (entonnoir) ET que les questions sont en langage naturel
- Si la sortie n'a pas 5 docs → vérifie `top_n` passé à FlashrankRerank
- Recall@5 ne bouge presque pas → **normal** : il sature ; regarde Recall@1 et MRR

**Baseline de référence** : Recall@1 40%→70%, MRR 0.617→0.833 sur les questions naturelles HomeButler.

✋ **Checkpoint final Core** — `python ateliers/atelier-08-optimisation/checkpoints/check_final.py`
→ ≥ 4/5 : Bonus 🏆 · < 3/5 : Sprint ⚡ · entre les deux : relis le concept raté puis Bonus

---

## ⚡ SPRINT (chemin alternatif, 30 min)

> Tu es ici parce que le checkpoint < 60%, ou que tu as pris du retard.

**Sprint 1 — L'entonnoir (15 min)**
Ouvre `homebutler/rag/reranking.py`. Explique par écrit : que se passe-t-il si `base_k=5`
et `top_n=5` ? Et si `base_k=20`, `top_n=5` ? Lance les deux et compare Recall@1.

**Sprint 2 — Bi vs cross-encoder (15 min)**
Sur la question "mon linge ressort trempé", affiche les 5 chunks de la baseline FAISS puis
les 5 chunks rerankés. Le bon chunk (lave-linge) monte-t-il dans le classement ?

---

## 🏆 BONUS (parcours alternatif, 60-70 min)

> Score ≥ 80%. Tous les défis restent dans le scope AT08 — pas de Langfuse, pas d'Azure.

### Défi Bonus 1 — Tuning base_k / top_n (coût vs précision)
**POURQUOI ?** L'entonnoir a un coût : le cross-encoder score `base_k` paires par requête.
**Question** : pour `base_k ∈ {10, 20, 40, 80}` et `top_n=5`, trace Recall@1, MRR et latence/req.
Où est le meilleur compromis pour HomeButler ?
**Pistes** : le gain plafonne-t-il ? La latence devient-elle gênante ? Existe-t-il un `base_k`
au-delà duquel on ajoute du bruit (mauvais chunks repêchés) ?

### Défi Bonus 2 — Chaîner multi-query → reranking
**POURQUOI ?** Multi-query augmente le rappel, reranking la précision. Les chaîner cumule.
**Question** : construis un retriever qui (1) fait du multi-query pour ratisser large, puis
(2) reranke l'union à top_n=5. Compare Recall@1/MRR à reranking-seul sur les questions naturelles.
**Pistes** : sur quelles questions le multi-query apporte-t-il des chunks que le reranking seul
ratait ? Le coût (appels LLM + cross-encoder) en vaut-il la peine ?

---

## 🎓 Wrap-up (10 min)

**Checklist de fin** :
- [ ] `python solution.py` affiche ΔRecall@1 ≥ +20 pts et ΔMRR > 0
- [ ] Les 3 bugs réparés et testés (3× `pytest` vert)
- [ ] `bash scripts/verify_branch_scope.sh` passe
- [ ] Checkpoint final ≥ 60%

**Quiz oral chronométré (5 min, 10 questions)** — sans relire :
1. Différence bi-encodeur / cross-encoder ?
2. Pourquoi ne pas appliquer le cross-encoder à tout le corpus ?
3. Qu'est-ce que l'entonnoir `base_k ≫ top_n` ?
4. Que se passe-t-il si `base_k == top_n` ?
5. Pourquoi mesurer Recall@1 et MRR plutôt que Recall@5 ici ?
6. D'où vient la diversité du multi-query ?
7. Multi-query améliore le rappel ou la précision ?
8. Qu'est-ce que HyDE ?
9. Pourquoi les questions en langage naturel révèlent-elles le gain du reranking ?
10. Quel modèle de reranking utilise-t-on et sur quel matériel tourne-t-il ?

→ ≥ 8/10 : tu maîtrises l'optimisation du pipeline. 5-7 : relis le Carnet. < 5 : refais le Sprint.

**Ce que je retiens en 3 lignes** :
```
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________
```

---

## 🔗 Pour aller plus loin (hors TP, lecture)

**Pont avec ton projet** : en production, le reranking est le meilleur rapport qualité/effort
pour améliorer un RAG existant — pas besoin de réindexer, on ajoute juste un étage. Le coût
est une latence cross-encoder maîtrisée par l'entonnoir.

**Avertissements** :
- flashrank télécharge son modèle au 1er run (réseau requis une fois)
- Le reranking n'aide pas si le bon chunk n'est PAS dans les `base_k` candidats : soigne
  d'abord le chunking et le retrieval (AT02) avant d'ajouter un reranker

**Lectures complémentaires** :
- Reimers & Gurevych, Sentence-BERT / cross-encoders : https://arxiv.org/abs/1908.10084
- Gao et al. 2022, HyDE — Precise Zero-Shot Dense Retrieval : https://arxiv.org/abs/2212.10496
- LangChain docs — ContextualCompressionRetriever, FlashrankRerank, MultiQueryRetriever
