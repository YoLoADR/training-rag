# GUIDE FORMATEUR — Atelier 07 : Observabilité & Évaluation (~3h30)

> Guide destiné au formateur. L'élève n'y a pas accès.
> **Module avancé optionnel** (parcours industrialisation) — après AT05/AT06.

---

## 1. Ce que l'élève doit comprendre à la fin

- La différence **observabilité (tracing)** vs **évaluation** : QUE s'est-il passé (latence,
  tokens, coût) vs est-ce BON (faithfulness, pertinence).
- Quelles métriques RAGAS exigent une **référence** (context_recall/precision) et lesquelles
  non (faithfulness, answer_relevancy) — et POURQUOI.
- Pourquoi un **LLM-as-judge** doit être déterministe (`temperature=0`).
- Comment **attacher un score** à une trace (suivi continu de la qualité).

Délimitation AT05 → AT07 : AT05 introduit Langfuse pour VOIR les traces (ops). AT07 ajoute la
discipline d'ÉVALUATION (RAGAS + judge) attachée aux traces. On MESURE le RAG, on ne le modifie pas.

**Hors scope** : reranking (AT08), Azure (AT09). Le hook bloque ces mots-clés.

---

## 1.bis Carte des blancs — navigation rapide formateur

> `git checkout student/07-observabilite` puis ouvre `ateliers/atelier-07-observabilite/evaluate_observability.py`.
> Les TODO sont DANS ce fichier (style AT06). La lib `homebutler/eval/` est FOURNIE corrigée.

### `evaluate_observability.py` — ce que l'élève câble

| Zone | Ce que l'élève écrit | Pourquoi |
|---|---|---|
| handler + callbacks | `handler = get_langfuse_handler()` ; `rag_chain.invoke(q, config={"callbacks":[handler]})` | Tracer chaque appel |
| judge + score | `score = llm_as_judge(q, answer, contexts)` ; `score_trace(handler.get_trace_id(), "llm_judge", score)` | Noter la qualité, l'attacher à la trace |
| samples | `{user_input:q, response:answer, retrieved_contexts:contexts, reference:output}` | reference = champ output du dataset (sinon NaN) |
| RAGAS | `build_eval_dataset(samples)` → `run_ragas_eval(...)` | Rapport de métriques |
| flush | `flush_traces(handler)` | Envoi async → flush en fin |

### Vérifier l'état en 30 s
```bash
git checkout student/07-observabilite
grep -n "TODO\|NotImplementedError" ateliers/atelier-07-observabilite/evaluate_observability.py
```

---

## 2. Setup formateur — avant l'atelier

```bash
git checkout atelier/07-observabilite
source .venv/bin/activate
pip install -r requirements_atelier07.txt && pip install -e .
python scripts/generate_documents.py
python scripts/generate_qa_dataset.py        # crée data/qa_dataset/concierge_qa.jsonl
python scripts/preload_models.py
# .env : ANTHROPIC_API_KEY (ou LLM_PROVIDER=ollama) + LANGFUSE_* (Cloud)
```

### Test de fumée
```bash
# Bug tests : déterministes, PAS besoin de clé LLM ni de Langfuse live
pytest ateliers/atelier-07-observabilite/bugs/ -v     # 3 passed
# Run complet (nécessite un LLM joignable pour RAGAS + judge) :
python ateliers/atelier-07-observabilite/evaluate_observability.py
```

> ⚠️ Le run NUMÉRIQUE RAGAS exige un LLM (clé Anthropic ou Ollama). Sans clé, le script
> charge le dataset, retrouve les contextes, construit la chaîne, puis échoue à l'appel LLM —
> c'est attendu. Les bug tests, eux, tournent sans clé.

### Langfuse : Cloud (défaut) ou self-host (bonus)
- Cloud : réutiliser le projet AT05 (clés dans `.env`). Le plus simple en salle.
- Self-host : `docker compose -f ateliers/atelier-07-observabilite/docker-compose.langfuse.yml up -d`
  → http://localhost:3000, créer projet, copier les clés, `LANGFUSE_HOST=http://localhost:3000`.

---

## 3. Déroulé détaillé

| Bloc | Durée | Contenu |
|---|---|---|
| Slides | 30 min | observabilité vs éval, RAGAS, judge déterministe |
| Démo live | 20 min | run + traces Langfuse + rapport RAGAS |
| Passage de relais | 5 min | commandes student/07 |
| Core élève | 1h40 | câbler tracing + judge + RAGAS |
| Bug Hunt | 20 min | 3 bugs (lib eval/) |
| Mesure + Checkpoint | 15 min | tableau + check_final |
| Sprint OU Bonus | 30-70 min | selon score |

### Démo live (T+30)
```bash
git checkout atelier/07-observabilite
python ateliers/atelier-07-observabilite/evaluate_observability.py
```
- Montre `homebutler/eval/tracing.py` → l'import v2 `from langfuse.callback import CallbackHandler`.
- Lance le script ; ouvre Langfuse → pointe une trace : latence, tokens, coût, ET le score `llm_judge`.
- Pointe le rapport RAGAS ; insiste sur `context_recall` qui n'est PAS NaN car `reference` est fournie.
- Verbalise : « AT05 nous montrait les traces. Ici on y ATTACHE un jugement de qualité. »

### Passage de relais (T+50)
```bash
git checkout student/07-observabilite
grep -n "TODO" ateliers/atelier-07-observabilite/evaluate_observability.py
```
Annonce : **« 1h40. Critère : traces avec score + RAGAS sans NaN. 6 questions en Core (rate-limit). »**

---

## 4. Bug Hunt — concret

> Reset : `git checkout -- homebutler/eval/<fichier>`. Tests déterministes (sans LLM/Langfuse live).

- **v1 (tracing.py)** : import `langfuse.langchain` (v3) au lieu de `langfuse.callback` (v2).
  `test_v1` (analyse statique) échoue. Question : « ça marche sans clés, ça casse avec — pourquoi ? »
  (handler créé seulement si clés présentes → ImportError en prod uniquement).
- **v2 (ragas_eval.py)** : `build_eval_dataset` omet `reference`. `test_v2` (construit un dataset,
  vérifie reference) échoue. Question : « quelles métriques deviennent NaN et pourquoi ? »
- **v3 (judge.py)** : `temperature=1.0`. `test_v3` (statique) échoue. Question : « pourquoi un
  juge doit-il être déterministe ? »

Après chaque bug, faire lire `bugs/vN_explanation.md`.

---

## 5. Checkpoints
- `check_1.py` — 3 QCM (observabilité vs éval, NaN/reference, juge déterministe). Seuil 2/3.
- `check_final.py` — 5 questions à réponse libre (mots-clés). ≥80% prêt, <60% Sprint.

---

## 6. Questions fréquentes

**"context_recall est NaN"** → `reference` manquante ou mal mappée (output→reference). C'est le Bug v2.
**"RAGAS me réclame une clé OpenAI"** → tu n'as pas injecté le LLM/embeddings. `run_ragas_eval`
passe `llm=get_llm(...)` + `embeddings=fastembed` explicitement. Ne jamais laisser RAGAS par défaut.
**"429 rate limit"** → RAGAS = dizaines d'appels. Réduire N_EVAL, ou `LLM_PROVIDER=ollama`.
**"Traces invisibles"** → API/handler non flush (flush_traces en fin), ou .env non rechargé, ou
host avec slash final. Cf. AT05 FAQ.
**"Pourquoi langfuse v2 et pas v3 ?"** → AT05 en dépend (pin 2.57.1). v3 change l'intégration LangChain.

---

## 7. Signaux d'alerte (élève bloqué)
- **Confond tracing et éval** → analogie boîte noire (trace) vs jury (éval).
- **Oublie reference** → context_recall NaN ; rappeler le mapping output→reference.
- **Veut modifier le RAG pour améliorer les scores** → STOP : ici on MESURE. L'amélioration = AT08.
- **Met temperature>0 au judge** → rappeler la reproductibilité.

---

## 8. Transition

À la fin d'AT07, l'élève sait MESURER (tracer + scorer) la qualité en continu. Suites :
- **AT08** : maintenant qu'on sait mesurer, AMÉLIORONS le retrieval (reranking) et prouvons le gain.
- **AT09** : passer l'index local à un vector store managé en cloud (Azure AI Search).
