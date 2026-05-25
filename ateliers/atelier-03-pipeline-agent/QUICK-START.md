# ⚡ Atelier 03 — Quick-Start (1 page)

> **Objectif** : un agent ReAct qui combine RAG + appel d'outil dans une conversation, et `bugs/test_v1.py` vert.

## 🚦 Pré-vol (5 min)
```bash
bash scripts/check_atelier_ready.sh 03   # vérifie env + index FAISS + Chroma
```

## 🍳 Recette de cuisine — 6 étapes

| # | Étape | Fichier | Vulgarisation |
|---|---|---|---|
| **1** | **Hybrid retrieval** (À CODER) | `homebutler/rag/retriever.py` → `get_ensemble_retriever` | _ensemble_ = combiner plusieurs retrievers avec des **poids**. FAISS (sémantique pur) 60 % + Chroma (filtrabilité métadonnées) 40 %. |
| **2** | **Récupérer un prompt ReAct** | `homebutler/agent/react_agent.py` → bloc try/except `hub.pull` | _hub_ = registre de prompts publics LangChain. `hwchase17/react-chat` = template ReAct officiel avec support `chat_history`. Fallback local si hub indispo. |
| **3** | **Construire l'agent** (À CODER) | `homebutler/agent/react_agent.py` → `create_react_agent` | _create_react_agent_ = fabrique un Runnable qui suit la boucle Thought → Action → Observation. Reçoit (llm, tools, prompt). |
| **4** | **Wrapper AgentExecutor** (À CODER) | `homebutler/agent/react_agent.py` → `AgentExecutor(...)` | _AgentExecutor_ = moteur d'exécution qui boucle l'agent. Params clés : `max_iterations=8` (anti-boucle), `handle_parsing_errors=True`, `return_intermediate_steps=debug`. |
| **5** | **Brancher la mémoire de session** (déjà fourni) | `get_session_agent(session_id)` | _ConversationBufferWindowMemory_ k=6 = garde 6 derniers tours. Reset si l'API redémarre. |
| **6** | **Tester** | `pytest ateliers/atelier-03-pipeline-agent/bugs/test_v1.py -v` | 🎯 cible : test vert ; agent respecte la limite d'itérations. |

## 🧠 Analogie ReAct
Un **détective** :
1. **Thought** (réfléchit) : « pour répondre à cette question, j'ai besoin de chercher dans le bail »
2. **Action** (agit) : appelle l'outil `search_home_docs("bail clause animaux")`
3. **Observation** (regarde) : lit le chunk retourné
4. (boucle si nécessaire)
5. **Final Answer** : synthèse

## 🛟 Bloqué > 15 min ?
1. Indice **léger** puis **fort** dans la docstring.
2. Verbalise : « qu'est-ce que prend `EnsembleRetriever` en argument ? »
3. ```bash
   git diff student/03-pipeline-agent atelier/03-pipeline-agent -- <fichier>
   ```

## ✅ Validation
```bash
pytest ateliers/atelier-03-pipeline-agent/                      # tronc commun
python ateliers/atelier-03-pipeline-agent/checkpoints/check_1.py
```
