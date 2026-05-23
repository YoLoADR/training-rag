# Atelier 01 — LLM Baseline (J1 matin)

> **Chapitre formation** : Introduction LLM + concepts RAG
> **Branche** : `atelier/01-llm-baseline`
> **Durée** : ~3 heures (demi-journée)

## Objectif pédagogique

Observer le comportement d'un LLM **sans contexte externe** :
- Constater les hallucinations sur des questions spécifiques (logement)
- Comprendre la knowledge cutoff (le modèle ne connaît pas votre logement)
- Mesurer l'impact de la température sur le déterminisme
- Comparer l'API hébergée (Claude) à un modèle local (Ollama)

## Pré-requis

```bash
# 1. Venv et dépendances
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_atelier01.txt
pip install -e .

# 2. Configuration
cp .env.example .env
# Éditer .env → ajouter ANTHROPIC_API_KEY=sk-ant-...

# 3. Vérification
python -c "import homebutler; print('Package OK')"
```

## Lancer l'exercice

```bash
python ateliers/atelier-01-llm-baseline/exercice.py
```

## Questions de réflexion (alignées Slide 3 Chapitre 1)

1. **Pourquoi un LLM prédit le prochain token plutôt que de "comprendre" ?**
   _(indice : penser à comment il a été entraîné — next-token prediction sur des trillions de tokens du web)_

2. **Quel type de question échoue TOUJOURS sans retrieval ?**
   _(indice : tout ce qui dépend d'un contexte privé ou postérieur à la date d'entraînement)_

3. **La température contrôle quoi exactement ?**
   _(indice : c'est un paramètre de sampling au moment de choisir le prochain token)_

## Contexte fil rouge — HomeButler AI

Le projet final est un **assistant conciergerie pour logement** qui répond
à des questions comme :
- "Quelle est la marque de ma chaudière ?"
- "À quelle température régler la chaudière la nuit ?"
- "Mon DPE est de quelle classe ?"

À ce stade, l'assistant n'a **aucune connaissance** de votre logement.
Il invente donc des réponses plausibles mais fausses → **c'est le problème
que le RAG résoudra à l'atelier 02**.

## Note Colab — comparaison 3 modèles

La comparaison Llama / Mistral / Qwen est dans `notebooks/01_llm_baseline.ipynb`,
compatible Google Colab uniquement (GPU T4 gratuit requis).
L'exercice Python en local utilise un seul modèle (Claude ou Ollama).

## Critère de succès

À la fin de cet atelier vous devez avoir constaté :
- [ ] Le LLM invente une réponse plausible sur "marque de la chaudière"
- [ ] Avec `temperature=0`, deux runs successifs donnent la même réponse
- [ ] Avec `temperature=0.9`, deux runs successifs divergent
- [ ] Le LLM ne sait pas que vous habitez à telle adresse (knowledge cutoff)

→ **Atelier suivant** : on injecte une base documentaire (PDFs du logement) via RAG.
