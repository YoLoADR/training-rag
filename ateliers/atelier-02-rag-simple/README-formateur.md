# Atelier 02 — RAG Simple FAISS (J1 après-midi)

> **Chapitre formation** : Création d'un RAG simple
> **Branche** : `atelier/02-rag-simple`
> **Durée** : ~3 heures (demi-journée)

## Objectif pédagogique

Résoudre le problème d'hallucination de l'atelier 01 en construisant un
**pipeline RAG complet** :
1. Charger les PDFs du logement (notice chaudière, bail, DPE, ...)
2. Découper en chunks avec 3 stratégies différentes
3. Vectoriser et indexer dans FAISS
4. Retrouver les chunks pertinents et les injecter dans le prompt
5. Mesurer le Recall@k sur 5 questions étalons

## Pré-requis

```bash
# 1. Venv + dépendances
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_atelier02.txt
pip install -e .

# 2. Variables d'environnement
cp .env.example .env
# Éditer .env → ANTHROPIC_API_KEY + DOCUMENTS_DIR/FAISS_PATH (déjà par défaut)

# 3. Générer les PDFs fictifs du logement
python scripts/generate_documents.py

# 4. Pré-télécharger le modèle d'embeddings (~300 MB, une seule fois)
python scripts/preload_models.py
```

## Lancer l'exercice

```bash
python ateliers/atelier-02-rag-simple/exercice.py
```

## Questions de réflexion

1. **Pourquoi le chunking impacte ~80 % de la qualité d'un RAG ?**
   _(indice : si le bon contexte n'est pas dans un chunk, le LLM ne pourra
   pas y accéder même avec le meilleur retriever)_

2. **Recall@5 = 80 % signifie quoi concrètement ?**
   _(indice : sur 100 questions, 80 ont au moins un chunk pertinent dans
   le top 5 ; 20 questions sont structurellement irrésolubles par le RAG)_

3. **Pourquoi FAISS est plus rapide qu'une boucle `for doc in documents:
   calculer_distance(doc, question)` ?**
   _(indice : structure d'index ANN — Approximate Nearest Neighbors)_

## Contexte fil rouge

La question test : "**Quelle est la marque de ma chaudière ?**"
- Atelier 01 → le LLM invente "Viessmann" / "Atlantic" au hasard
- Atelier 02 → le LLM répond **"Viessmann Vitodens 100-W"** en citant
  `notice_chaudiere.pdf` comme source.

## Fichiers fournis

```
ateliers/atelier-02-rag-simple/
├── README.md           ← ce fichier
├── exercice.py         ← 6 TODOs à compléter
├── solution.py         ← version corrigée + commentaires RAG
└── evaluate_rag.py     ← métriques RAGAs (optionnel)
```

## Critère de succès

- [ ] `python solution.py` répond "Viessmann Vitodens 100-W" + cite la source
- [ ] Recall@5 ≥ 80 % sur les 5 questions étalons
- [ ] Vous savez expliquer la différence entre les 3 stratégies de chunking

→ **Atelier suivant** : ajouter ChromaDB + un agent ReAct multi-outils.
