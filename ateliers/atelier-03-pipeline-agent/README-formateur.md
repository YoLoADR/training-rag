# Atelier 03 — Pipeline RAG + Agent ReAct (J2 matin)

> **Chapitre formation** : Pipeline RAG + Agent ReAct
> **Branche** : `atelier/03-pipeline-agent`
> **Durée** : ~3 heures (demi-journée)

## Objectif pédagogique

Passer d'un RAG mono-source à un **agent multi-outils** capable d'orchestrer
plusieurs sources d'information dynamiquement.

1. Ajouter **ChromaDB** à côté de FAISS (filtres métadonnées)
2. Combiner les deux via un **EnsembleRetriever** (poids 0.6/0.4)
3. Construire 4 **outils LangChain** (RAG, énergie, marketplace, météo)
4. Assembler un agent **ReAct** (Thought → Action → Observation → ...)
5. Observer la trace ReAct sur une question multi-outils

## Pré-requis

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_atelier03.txt
pip install -e .
cp .env.example .env
# Éditer .env → ANTHROPIC_API_KEY

# Données nécessaires (PDFs + CSV énergie + JSON producteurs)
python scripts/generate_documents.py
python scripts/generate_energy_data.py
python scripts/generate_producers.py
python scripts/preload_models.py

# Construire les deux index vectoriels (une seule fois)
python -c "from homebutler.rag.ingestion import ingest_all_documents; \
           from homebutler.rag.vectorstore_faiss import build_faiss_index; \
           build_faiss_index(ingest_all_documents(), force_rebuild=True)"
python -c "from homebutler.rag.ingestion import ingest_all_documents; \
           from homebutler.rag.vectorstore_chroma import build_chroma_db; \
           build_chroma_db(ingest_all_documents())"
```

## Lancer l'exercice

```bash
python ateliers/atelier-03-pipeline-agent/exercice.py
# ou la version Gradio :
python ateliers/atelier-03-pipeline-agent/gradio_demo.py
```

## Questions de réflexion

1. **Que se passe-t-il si l'agent boucle indéfiniment (max_iterations atteint) ?**
   _(indice : le AgentExecutor renvoie une réponse partielle + warning ; à monitorer en prod via la trace ReAct)_

2. **Pourquoi mélanger FAISS (0.6) et ChromaDB (0.4) plutôt qu'un seul ?**
   _(indice : FAISS = recherche dense par sens ; ChromaDB = filtres + complément
   sparse — l'ensemble améliore le recall sur certaines requêtes)_

3. **Question multi-outils du fil rouge** :
   > "Il va faire -5°C demain, comment je prépare ma maison et que puis-je commander à un producteur local ?"
   Combien d'outils sont appelés ? Lesquels ? Dans quel ordre ?
   _(attendu : 3+ outils — get_weather_forecast, search_home_docs, find_local_products)_

## Concepts clés

- **EnsembleRetriever** = fusion de plusieurs retrievers avec poids
- **AgentExecutor** = boucle while qui pilote l'agent jusqu'à `Final Answer`
- **ConversationBufferWindowMemory** = mémoire glissante (k=6 derniers tours)
- **ReAct loop** = pattern Thought→Action→Observation jusqu'à la réponse finale

## Critère de succès

- [ ] Question multi-outils → 3+ outils différents appelés
- [ ] `return_intermediate_steps=True` expose la trace ReAct
- [ ] Le retriever ensemble retourne des chunks des 2 backends

→ **Atelier suivant** : fine-tuner un modèle pour adapter son style.
