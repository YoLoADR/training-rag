# Atelier 08 — Optimisation du pipeline RAG (module avancé — parcours industrialisation)

> **Chapitre formation** : Techniques avancées de RAG / optimisation itérative du pipeline
> **Branche** : `atelier/08-optimisation`
> **Durée** : ~3h30 (demi-journée) — module optionnel, jouable après AT03
> **Pré-requis** : AT02 (FAISS) et AT03 (retriever) acquis

## Objectif pédagogique

Reprendre le retrieval d'AT02/AT03 (qui laisse parfois le bon chunk au rang 6-8) et
en améliorer la **précision** avec 3 techniques 100% locales (CPU, sans GPU) :
1. **Reranking cross-encoder** (flashrank) — entonnoir `base_k` ≫ `top_n`
2. **Multi-query** — le LLM reformule, on prend l'union (rappel)
3. **HyDE** — embed une réponse hypothétique (bonus)

Puis **mesurer** le gain (Recall@1, MRR) face à la baseline FAISS.

## Pré-requis techniques

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_atelier08.txt
pip install -e .
python scripts/generate_documents.py      # corpus (si absent)
python scripts/preload_models.py          # fastembed + reranker flashrank (~34 Mo)
```

## Lancer

```bash
python ateliers/atelier-08-optimisation/exercice.py    # squelette (élève)
python ateliers/atelier-08-optimisation/solution.py    # corrigé (formateur)
```

## Résultats de référence (figés par run réel, corpus HomeButler)

Questions en langage NATUREL/indirect (vocabulaire usager ≠ documents) :

| Métrique | Baseline FAISS | + Reranking | Gain |
|---|---|---|---|
| Recall@1 | 40% | 70% | **+30 pts** |
| Recall@3 | 90% | 100% | +10 pts |
| Recall@5 | 90% | 100% | +10 pts |
| MRR | 0.617 | 0.833 | **+0.22** |

> Point clé à verbaliser : sur des questions "mot pour mot" du document, la baseline
> est déjà parfaite — le gain du reranking ne se voit QUE sur du vocabulaire divergent,
> et surtout sur Recall@1/MRR (l'ordre de tête), pas sur Recall@5 (qui sature).

## Ce que l'élève code

`homebutler/rag/reranking.py` (3 fonctions) :
- `get_reranked_retriever(base_k, top_n)` — ContextualCompressionRetriever + FlashrankRerank
- `get_multiquery_retriever(k)` — MultiQueryRetriever.from_llm + MULTIQUERY_PROMPT
- `get_hyde_chain()` — chaîne LCEL (bonus)

Puis complète `exercice.py` (TODO 2-4) pour comparer baseline vs reranked.

## Bug Hunt

| Patch | Bug | Symptôme | Fix |
|---|---|---|---|
| v1 | `RERANK_BASE_K=5` (== top_n) | entonnoir cassé, reranker ne filtre plus | base_k=20 |
| v2 | prompt multi-query → 1 reformulation | plus de diversité de requêtes | redemander 3 |
| v3 | `FlashrankRerank()` sans top_n | sortie = 3 (défaut) au lieu de 5 | passer top_n=top_n |

## Contexte fil rouge

AT02 finissait sur : *"On pourrait améliorer la précision en ajoutant un re-ranker
(cross-encoder) après le retriever. Hors-scope de cet atelier mais à mentionner."*
AT08 réalise exactement cette promesse.

→ **Atelier suivant possible** : 07 (observabilité/éval) pour mesurer en continu, 09 (Azure).
