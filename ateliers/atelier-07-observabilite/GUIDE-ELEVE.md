# Atelier 07 — Observabilité & Évaluation (demi-journée, ~3h30)

> Ici tu ne suis pas un step-by-step. Tu reçois une mission, des contraintes, des indices ;
> tu câbles. La bibliothèque `homebutler/eval/` est fournie — tu l'ORCHESTRES dans
> `evaluate_observability.py`.
>
> **Module avancé — parcours industrialisation.** Pré-requis : AT02/03 (RAG), AT05 (Langfuse), AT06 (dataset).

---

## 🚦 Pré-vol (avant de commencer) — 20 min

- [ ] `bash scripts/check_atelier_ready.sh 07` retourne OK
- [ ] Corpus + dataset présents : `python scripts/generate_documents.py` et `python scripts/generate_qa_dataset.py`
- [ ] Index FAISS construit (sinon reconstruit au 1er run)
- [ ] LLM joignable : `ANTHROPIC_API_KEY` dans `.env` OU `LLM_PROVIDER=ollama` (RAGAS + judge font des appels LLM)
- [ ] Traces : `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` dans `.env`
  - Par défaut : **Langfuse Cloud** (https://cloud.langfuse.com — déjà utilisé en AT05)
  - Bonus self-host : `docker compose -f ateliers/atelier-07-observabilite/docker-compose.langfuse.yml up -d` puis `LANGFUSE_HOST=http://localhost:3000`
- [ ] J'ai lu la section "Périmètre"

> Sans clés Langfuse, le tracing devient un no-op silencieux : RAGAS et le judge fonctionnent quand même.

---

## 🎯 La mission

Le CTO HomeButler te demande : **"Notre assistant répond. Mais en production, je veux SAVOIR :
combien ça coûte, combien de temps ça prend, et surtout — est-ce que les réponses sont BONNES ?
Rends-moi ça mesurable et tracé."**

**Livrable** : `python evaluate_observability.py` qui :
1. Trace chaque appel RAG dans Langfuse (prompt, latence, tokens, coût)
2. Note chaque réponse via un LLM-as-judge (score poussé dans la trace)
3. Produit un rapport RAGAS (faithfulness, answer_relevancy, context_precision, context_recall)

**Critères de succès auto-vérifiables** :
- Les traces apparaissent dans Langfuse avec un score `llm_judge` attaché
- Le rapport RAGAS s'affiche avec `faithfulness` AU-DESSUS du seuil que TU mesures (≈ 0.85 sur le corpus)
- `context_recall` n'est PAS NaN (donc `reference` bien fournie)
- Les 3 bugs du Bug Hunt réparés (3× `pytest` vert)

**Budget temps** : 1h40 Core (+30 min Sprint OU 60-70 min Bonus). Dataset réduit à 6 questions en Core (rate-limit).

---

## 🚧 Périmètre de cet atelier

- ✅ **Dans le scope** : Langfuse (tracing + scoring), RAGAS (4 métriques), LLM-as-judge déterministe, métriques qualité/coût/latence
- ❌ **Hors scope** (autres ateliers) : reranking/multi-query (AT08), Azure (AT09), fine-tuning. **Modifier le RAG lui-même** : ici on le MESURE, on ne le change pas.
- 🛡️ **Garde-fou activé** : `.claude/CLAUDE.md` local + hook `UserPromptSubmit`

---

## 🛠️ vs 🎮 — Choisis ta piste

| Critère | 🛠️ Piste Build | 🎮 Piste Vibe |
|---|---|---|
| **Outil** | Code à la main ; Claude Code en `plan` | Délégation OK |
| **Obligation Build** | Lire `homebutler/eval/` (la lib que tu câbles) avant de coder | — |
| **Obligation Vibe** | (a) Expliquer pourquoi `context_recall` a besoin de `reference` | (b) Prédire l'effet de `temperature=1.0` sur le judge avant le Bug Hunt v3 |
| **Bug Hunt** | Tu trouves le bug toi-même | Tu prédis l'effet du bug avant de lire le test |

> **Obligation Vibe** : avant de valider une étape, sache répondre : "Quelle est la différence entre TRACER et ÉVALUER ?"

---

## 🧠 Carnet de bord (concepts à mobiliser)

### Observabilité (tracing)
Enregistrer ce qui se passe à chaque appel : prompt envoyé, réponse, modèle, latence, tokens, coût, étapes intermédiaires.

**Analogie** : la boîte noire d'un avion. Quand quelque chose cloche en prod, tu rejoues la trace. Sans elle, tu débugues à l'aveugle.

**Dans le projet** : `get_langfuse_handler()` (homebutler/eval/tracing.py) → passé en `callbacks=[handler]` à la chaîne. SDK v2 : `from langfuse.callback import CallbackHandler`.

### Évaluation
Mesurer la QUALITÉ des réponses selon des métriques, pas seulement « ça a tourné ».

**Analogie** : l'observabilité dit « le plat est sorti de cuisine en 8 min » ; l'évaluation dit « le plat est-il bon ? ».

### RAGAS — les 4 métriques
- **faithfulness** : la réponse est-elle ANCRÉE dans les contextes (ne pas inventer) ? [pas besoin de référence]
- **answer_relevancy** : la réponse RÉPOND-elle à la question ? [pas besoin de référence]
- **context_precision** : les contextes récupérés sont-ils pertinents ? [EXIGE `reference`]
- **context_recall** : les contextes couvrent-ils la réponse de référence ? [EXIGE `reference`]

**Schéma RAGAS 0.2.x** : chaque échantillon = `{user_input, response, retrieved_contexts, reference}`.

> ⚠️ Sans `reference`, `context_recall` et `context_precision` renvoient **NaN** (c'est le Bug v2).

### reference (ground truth)
La bonne réponse annotée. Dans notre dataset Alpaca (`concierge_qa.jsonl`), c'est le champ `output`. Mapping : `input` → `user_input`, `output` → `reference`.

### LLM-as-judge
Un LLM note la qualité d'une réponse (1-5). DOIT être déterministe (`temperature=0`) sinon les scores fluctuent → évaluation non reproductible.

**Analogie** : un jury qui donnerait une note différente à chaque visionnage de la même copie serait inutilisable.

### score attaché à une trace
On pousse le score du judge DANS la trace Langfuse (`score_trace(trace_id, name, value)`) → on filtre/suit la qualité par requête dans le dashboard.

---

## 🎯 TRONC COMMUN (1h40)

### Étape 1 — Tracer le RAG avec Langfuse (30 min)

**Objectif** : câbler le handler Langfuse et voir les traces apparaître.

**Indices (Build)** — dans `evaluate_observability.py` :
- `handler = get_langfuse_handler()` (None si pas de clés)
- `rag_chain.invoke(q, config={"callbacks": [handler]})` → l'appel est tracé
- `flush_traces(handler)` en fin (l'envoi est asynchrone)

**Observation attendue** : après le run, ouvrir Langfuse → projet → Traces : une trace par question, avec latence + tokens.

✋ **Checkpoint 1** — `python ateliers/atelier-07-observabilite/checkpoints/check_1.py` (≥ 2/3)

---

### 🔬 Mini-lab — Mesurer l'overhead du tracing (15 min)

**Variable** : tracing activé vs désactivé.
**Protocole** : mesure la latence moyenne sur 5 questions AVEC handler, puis SANS (commente `LANGFUSE_PUBLIC_KEY`). Compare.

**Questions** : l'overhead est-il significatif ? (typiquement 50-150 ms, envoi async). Acceptable en prod ?

---

### Étape 2 — Noter (judge) + évaluer (RAGAS) (35 min)

**Objectif** : attacher un score LLM-judge aux traces et produire le rapport RAGAS.

**Indices (Build)** :
- `score = llm_as_judge(q, answer, contexts)` puis `score_trace(handler.get_trace_id(), "llm_judge", score)`
- Construire les échantillons `{user_input, response, retrieved_contexts, reference}` (reference = output du dataset !)
- `dataset = build_eval_dataset(samples)` ; `metrics = run_ragas_eval(dataset)`

**Observation attendue** :
```
faithfulness            : 0.8xx
answer_relevancy        : 0.8xx
context_precision       : 0.xxx
context_recall          : 0.xxx   ← PAS NaN
```

> Garde-fou rate-limit : reste à 6 questions en Core. Si 429, passe `LLM_PROVIDER=ollama`.

---

### 🐛 Casse-moi ça — Bug Hunt (20 min)

Les bugs sont dans `homebutler/eval/` (la lib fournie). Reset : `git checkout -- homebutler/eval/<fichier>`.

**Bug v1 — mauvais import du CallbackHandler (v3 au lieu de v2)**
```bash
git apply ateliers/atelier-07-observabilite/bugs/v1.patch
pytest ateliers/atelier-07-observabilite/bugs/test_v1.py -v   # ECHOUE
git checkout -- homebutler/eval/tracing.py
pytest ateliers/atelier-07-observabilite/bugs/test_v1.py -v   # PASSE
```
Lis `bugs/v1_explanation.md`.

**Bug v2 — `reference` absent → context_recall NaN**
```bash
git apply ateliers/atelier-07-observabilite/bugs/v2.patch
pytest ateliers/atelier-07-observabilite/bugs/test_v2.py -v
git checkout -- homebutler/eval/ragas_eval.py
pytest ateliers/atelier-07-observabilite/bugs/test_v2.py -v
```
Lis `bugs/v2_explanation.md`.

**Bug v3 — judge non déterministe (temperature=1.0)**
```bash
git apply ateliers/atelier-07-observabilite/bugs/v3.patch
pytest ateliers/atelier-07-observabilite/bugs/test_v3.py -v
git checkout -- homebutler/eval/judge.py
pytest ateliers/atelier-07-observabilite/bugs/test_v3.py -v
```
Lis `bugs/v3_explanation.md`.

> **Règle anti-cheat** : demande à l'IA d'expliquer le symptôme, pas « trouve le bug dans le patch ».

---

### 📊 Mesure-toi (15 min)

| Métrique | Valeur observée | Cible |
|---|---|---|
| **faithfulness** | ___ | ≥ 0.85 (à confirmer sur ton corpus) |
| **answer_relevancy** | ___ | élevé |
| **context_precision** | ___ | — |
| **context_recall** | ___ | PAS NaN |
| **latence p50** (Langfuse) | ___ s | — |
| **score llm_judge moyen** | ___ | — |

**Interprétation** :
- context_recall NaN → `reference` manquante (vérifie le mapping output→reference)
- faithfulness faible → le LLM invente au-delà du contexte (revois le prompt RAG)
- scores judge qui varient entre 2 runs → juge non déterministe (temperature)

✋ **Checkpoint final** — `python ateliers/atelier-07-observabilite/checkpoints/check_final.py` (≥ 80% prêt, < 60% Sprint)

---

## ⚡ SPRINT (chemin alternatif, 30 min)

**Sprint 1 — Tracing (15 min)** : fais apparaître 3 traces dans Langfuse. Explique par écrit ce que contient une trace (latence, tokens, coût).
**Sprint 2 — RAGAS reference (15 min)** : explique pourquoi `context_recall` exige `reference` et d'où vient `reference` dans notre dataset.

---

## 🏆 BONUS (60-70 min)

### Défi Bonus 1 — RAGAS sur 20 questions + dérive
**POURQUOI ?** 6 questions = échantillon ; 20 = tendance. **Question** : lance RAGAS sur 20 questions (attention rate-limit → Ollama). Compare les métriques à celles de 6 questions. La faithfulness est-elle stable ?

### Défi Bonus 2 — Self-host Langfuse + PII scrubbing
**POURQUOI ?** Souveraineté des données + RGPD. **Question** : lance Langfuse en local (docker-compose fourni), reconfigure `.env`, et ajoute une fonction qui masque les données personnelles (emails, adresses) AVANT de les envoyer dans les traces. Vérifie qu'aucune PII n'apparaît dans le dashboard.

---

## 🎓 Wrap-up (10 min)

**Checklist** :
- [ ] Traces visibles dans Langfuse avec score `llm_judge`
- [ ] Rapport RAGAS sans NaN sur context_recall
- [ ] 3 bugs réparés (3× pytest vert)
- [ ] Checkpoint final ≥ 60%

**Quiz oral (5 min, 10 questions)** :
1. Différence observabilité / évaluation ?
2. Quel import pour le CallbackHandler Langfuse v2 ?
3. Pourquoi flush les traces en fin de script ?
4. Quelles métriques RAGAS exigent `reference` ?
5. D'où vient `reference` dans notre dataset ?
6. Que mesure faithfulness ?
7. Que mesure context_recall ?
8. Pourquoi le judge doit-il être à temperature=0 ?
9. Que signifie un context_recall = NaN ?
10. Cite 3 usages de Langfuse en production.

→ ≥ 8/10 : tu maîtrises l'observabilité/éval. 5-7 : relis le Carnet. < 5 : refais le Sprint.

**Ce que je retiens en 3 lignes** :
```
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________
```

---

## 🔗 Pour aller plus loin (hors TP, lecture)

**Pont avec ton projet** : en production, ce qui n'est pas mesuré dérive en silence. Tracer + scorer en continu transforme « on croit que c'est bon » en « on sait, chiffres à l'appui ».

**Avertissements** :
- Langfuse SDK v2 (`langfuse.callback`) ≠ v3 (`langfuse.langchain`) — ne pas mélanger
- RAGAS appelle un LLM par métrique et par question → coûteux : commence petit (6 Q), passe en Ollama pour les gros runs
- RAGAS sans LLM/embeddings explicites tente d'utiliser OpenAI par défaut → toujours injecter get_llm + fastembed

**Lectures complémentaires** :
- RAGAS (Es et al. 2024, EACL) : https://arxiv.org/abs/2309.15217
- Docs Langfuse : https://langfuse.com/docs · self-host : https://langfuse.com/self-hosting
