# ⚡ Atelier 01 — Quick-Start (1 page)

> **Objectif** : démontrer qu'un LLM seul hallucine sur les données privées du logement (hallucination rate ≥ 80 % sur 5 questions privées).

## 🚦 Pré-vol (5 min)
```bash
bash scripts/check_atelier_ready.sh 01
echo $ANTHROPIC_API_KEY      # OU `ollama list` si LLM_PROVIDER=ollama
```

## 🍳 Recette de cuisine — 6 étapes

| # | Étape | Fichier | Vulgarisation |
|---|---|---|---|
| **1** | **Choisir le provider** | `.env` → `LLM_PROVIDER=anthropic` OU `ollama` | _provider_ = fournisseur du modèle (cloud payant vs local gratuit). On garde la même interface pour pouvoir switcher. |
| **2** | **Construire le LLM** (À CODER) | `homebutler/llm/provider.py` → `get_llm()` | _temperature_ = niveau d'aléatoire (0.0 = factuel, 1.0 = créatif). Pour conciergerie, vise **0.0–0.2**. _max_tokens_ = budget de la réponse (~1024 = ~750 mots). |
| **3** | **Écrire le system prompt** (À CODER) | `homebutler/llm/prompts.py` → `CONCIERGE_SYSTEM_PROMPT` | _system prompt_ = la « fiche de poste » du LLM (rôle, ton, domaines, règles). Indispensable pour cadrer la personnalité. |
| **4** | **Composer les 4 templates** (À CODER) | `homebutler/llm/prompts.py` → `RAG_QA`, `ENERGY_ANALYSIS`, `REACT_SYSTEM`, `BARE_LLM` | _ChatPromptTemplate_ = squelette de prompt avec variables `{question}`, `{context}`, etc. LangChain les substitue à l'appel. |
| **5** | **Lancer les 10 questions** | `python ateliers/atelier-01-llm-baseline/exercice.py` | 5 questions privées (LLM ne sait pas, doit halluciner ou refuser) + 5 questions générales (devrait savoir) |
| **6** | **Mesurer le taux d'hallucination** | output du script | 🎯 cible : ≥ 80 % d'hallucinations sur les 5 questions privées (preuve qu'il faut le RAG pour AT02) |

## 🛟 Bloqué > 15 min ?
1. Relis l'indice **léger** dans la docstring de la fonction.
2. Lis l'indice **fort** (juste en dessous).
3. Verbalise : « que prend `ChatAnthropic` comme arguments minimum ? »
4. En dernier recours :
   ```bash
   git diff student/01-llm-baseline atelier/01-llm-baseline -- homebutler/llm/<fichier>
   ```

## ✅ Validation
```bash
python ateliers/atelier-01-llm-baseline/exercice.py
python ateliers/atelier-01-llm-baseline/checkpoints/check_1.py
```
