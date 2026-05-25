# ⚡ Atelier 06 — Quick-Start (1 page)

> **Objectif** : produire un tableau Markdown comparatif chiffré (RAG fixed/recursive/ensemble) + grille décision TCO pour 3 cas d'usage.

## 🚦 Pré-vol (5 min)
```bash
bash scripts/check_atelier_ready.sh 06
export ENABLE_COMPARE_ROUTES=true              # IMPORTANT : active /rag/evaluate et /chat/compare
uvicorn api.main:app --port 8000 &
sleep 3 && curl http://localhost:8000/         # vérifie que l'API répond
```

## 🍳 Recette de cuisine — 6 étapes

| # | Étape | Fichier / commande | Vulgarisation |
|---|---|---|---|
| **1** | **Charger 20 paires Q/R** (déjà fourni) | `evaluate_pipeline.py` → `load_qa()` | Dataset HomeButler `concierge_qa.jsonl`, format Alpaca. |
| **2** | **Évaluer 3 stratégies de chunking** (À CODER `evaluate_strategies`) | `POST /rag/evaluate` x3 | _stratégies_ : fixed (coupe brutalement) / recursive (séparateurs naturels) / ensemble (FAISS + Chroma pondéré). On compare Recall@1/@3/@5. |
| **3** | **Comparer 3 modes sur 5 questions** (À CODER `compare_modes`) | `POST /chat` 5x3 | _modes_ : llm_only (hallucine), rag_only (factuel), agent (orchestre outils). On capture la latence à chaque appel. |
| **4** | **Latence moyenne par mode** (déjà fourni) | `show_latency_summary()` | _statistics.mean_ + _median_. llm_only ≈ 1-2 s, rag_only ≈ 3-5 s, agent ≈ 8-15 s (ReAct boucle). |
| **5** | **Tableau récapitulatif** (À CODER `show_summary`) | print Markdown | 🎯 cibles RAFT 2024 (Zhang et al.) : RAG ensemble ~0.87, RAG fixed ~0.72, LLM seul ~0.15, Hybride 94 % factuel. |
| **6** | **Grille décision TCO** | `grille_decision.md` | Pour 3 cas (RH, support tech, juridique) : recommander RAG / FT / Hybride avec justif chiffrée (coût €, qualité, latence). |

## 🧠 Lexique décision
- **TCO** (Total Cost of Ownership) = coût total (build + run + maintenance). FT coûte cher à l'entraînement mais peu à l'inférence ; RAG l'inverse.
- **Faithfulness** = la réponse est-elle ancrée dans les sources retournées ? Cible RAG > 0.85.
- **Answer relevancy** = la réponse répond-elle à la question (pas hors-sujet) ? Cible > 0.80.
- **RAFT** = Retrieval-Augmented Fine-Tuning : on fine-tune sur des paires Q/R où le prompt contient l'oracle + des distracteurs. Le modèle apprend à IGNORER le bruit.

## 🛟 Bloqué > 15 min ?
1. Indices **léger / fort** dans chaque docstring TODO.
2. Verbalise : « pourquoi évaluer SUR L'API HTTP plutôt qu'en appelant directement les fonctions Python ? »
3. ```bash
   git diff student/06-finetune-vs-rag atelier/06-finetune-vs-rag \
     -- ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py
   ```

## ✅ Validation
```bash
python ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py
python ateliers/atelier-06-finetune-vs-rag/checkpoints/check_1.py
```
