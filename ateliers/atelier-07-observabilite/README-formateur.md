# Atelier 07 — Observabilité & Évaluation (module avancé — parcours industrialisation)

> **Chapitre formation** : Évaluation & observabilité de RAG
> **Branche** : `atelier/07-observabilite`
> **Durée** : ~3h30 (demi-journée) — module optionnel, après AT05/AT06
> **Pré-requis** : AT02/03 (RAG), AT05 (Langfuse câblé), AT06 (dataset + bases d'éval)

## Objectif pédagogique

Rendre le pipeline RAG MESURABLE en continu (passer de « ça marche » à « voici la preuve
chiffrée et tracée ») :
1. **Tracer** chaque appel avec Langfuse (handler en callback)
2. **Noter** chaque réponse via un LLM-as-judge déterministe → score poussé dans la trace
3. **Évaluer** en batch avec RAGAS (faithfulness, answer_relevancy, context_precision/recall)

Délimitation avec AT05 : AT05 = « voir les traces » (ops/debug). AT07 = « scorer la qualité »
(évaluation systématique attachée aux traces).

## Pré-requis techniques

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_atelier07.txt
pip install -e .
python scripts/generate_documents.py        # corpus (si absent)
python scripts/generate_qa_dataset.py        # dataset Q/R (reference = champ output)
python scripts/preload_models.py             # fastembed
# .env : ANTHROPIC_API_KEY (ou LLM_PROVIDER=ollama) + LANGFUSE_* (Cloud)
```

## Lancer

```bash
python ateliers/atelier-07-observabilite/evaluate_observability.py
```

## Décisions clés (issues de l'audit)

- **Langfuse Cloud par défaut** (déjà configuré AT05). Le **self-host Docker** est un BONUS :
  `docker compose -f ateliers/atelier-07-observabilite/docker-compose.langfuse.yml up -d`
  (Langfuse v2 = 2 conteneurs, léger ; dashboard http://localhost:3000).
- **SDK Langfuse v2** (`langfuse==2.57.1`) : import `from langfuse.callback import CallbackHandler`.
  PAS `langfuse.langchain` (= v3).
- **RAGAS 0.2.x** : schéma `user_input / response / retrieved_contexts / reference`.
  Le juge et les embeddings sont injectés explicitement (get_llm + fastembed) → jamais OpenAI.
- **Garde-fou rate-limit** : `N_EVAL=6` questions en Core (RAGAS = dizaines d'appels LLM).
  Pour une classe, conseiller `LLM_PROVIDER=ollama` pour la phase éval. 20 questions en Bonus.
- **reference vient du champ `output`** du dataset Alpaca (mapping input→user_input, output→reference).

## Ce que l'élève code

`ateliers/atelier-07-observabilite/evaluate_observability.py` (TODO inline, style AT06) :
- charger le dataset (input→question, output→reference)
- câbler le handler Langfuse en callback du RAG chain
- pour chaque question : récupérer contextes, répondre (tracé), noter via llm_as_judge, score_trace
- build_eval_dataset + run_ragas_eval → tableau de métriques + flush_traces

`homebutler/eval/` est FOURNI (lecture seule).

## Bug Hunt (cible homebutler/eval/, tests sans LLM)

| Patch | Bug | Symptôme | Fix |
|---|---|---|---|
| v1 | import `langfuse.langchain` (v3) | ImportError du handler → 0 trace | `from langfuse.callback import CallbackHandler` |
| v2 | build_eval_dataset omet `reference` | context_recall/precision = NaN | transmettre reference |
| v3 | juge `temperature=1.0` | scores non reproductibles | temperature=0 |

> Vérif formateur : `pytest ateliers/atelier-07-observabilite/bugs/ -v` → 3 passed sur le corrigé.
> Les tests sont déterministes (analyse statique + construction de dataset), pas besoin de clé LLM ni de Langfuse live.

## Note de vérification

Le run NUMÉRIQUE de RAGAS (faithfulness, etc.) nécessite un LLM joignable (clé Anthropic ou
Ollama) — c'est le formateur qui l'exécute avec sa clé. Tout le reste (imports, dataset,
handler, bug tests) est vérifiable sans clé.

→ **Atelier suivant possible** : 08 (optimisation pipeline) ou 09 (Azure).
