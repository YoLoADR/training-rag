# ⚡ Atelier 05 — Quick-Start (1 page)

> **Objectif** : exposer le chatbot HomeButler via FastAPI (3 modes : llm_only, rag_only, agent) + endpoint pédagogique `/rag/retrieve`. Latence < 5 s.

## 🚦 Pré-vol (5 min)
```bash
bash scripts/check_atelier_ready.sh 05
# index FAISS + Chroma OK, agent ReAct importable, .env complet.
```

## 🍳 Recette de cuisine — 6 étapes

| # | Étape | Fichier | Vulgarisation |
|---|---|---|---|
| **1** | **Lire main.py** (déjà fourni) | `api/main.py` | _middleware_ = filtre HTTP qui s'exécute AVANT chaque requête. Ici : 19 patterns regex (FR+EN) qui bloquent les tentatives d'injection (« ignore les instructions », « jailbreak »…). |
| **2** | **Coder `_call_rag_only`** (À CODER) | `api/routers/chat.py` | _LCEL pipe_ = `chain = RAG_QA_TEMPLATE \| llm` — composition LangChain. `await loop.run_in_executor(None, chain.invoke, payload)` car FastAPI est async mais `.invoke()` est sync. |
| **3** | **Coder `_call_agent`** (À CODER) | `api/routers/chat.py` | _intermediate_steps_ = trace `[(AgentAction, observation_str), …]` exposée si `debug=True`. Permet au client de voir le Thought/Action/Observation. |
| **4** | **Coder `/rag/retrieve`** (À CODER) | `api/routers/rag.py` | Endpoint pédagogique de transparence : retourne les chunks RAW (rank, source, page, excerpt). Permet de comparer visuellement l'effet du chunking sans passer par le LLM. |
| **5** | **Démarrer l'API** | `uvicorn api.main:app --port 8000 --reload` | _reload_ = redémarre automatiquement quand un fichier change (dev). _slowapi_ limite à 30 req/min sur `/chat`. |
| **6** | **Tester** | `curl` ou Swagger UI http://localhost:8000/docs | 🎯 cible : réponse < 5 s ; `/rag/retrieve` renvoie 3-5 chunks ; tentative d'injection bloquée (400). |

## 🛟 Bloqué > 15 min ?
1. Indices **léger / fort** dans la docstring de chaque fonction blanke.
2. Verbalise : « pourquoi `await loop.run_in_executor` et pas un simple `chain.invoke()` ? »
3. ```bash
   git diff student/05-deploiement atelier/05-deploiement -- api/routers/<fichier>
   ```

## ✅ Validation
```bash
uvicorn api.main:app --port 8000 &
curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' \
  -d '{"message":"Quelle est ma chaudière?","mode":"rag_only"}'
curl -X POST http://localhost:8000/rag/retrieve -H 'Content-Type: application/json' \
  -d '{"query":"chaudière","k":3}'
python ateliers/atelier-05-deploiement/checkpoints/check_1.py
```
