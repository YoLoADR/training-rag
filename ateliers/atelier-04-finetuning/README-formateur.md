# Atelier 04 — Fine-tuning LoRA/QLoRA (J2 après-midi)

> **Chapitre formation** : Fine-tuning HuggingFace
> **Branche** : `atelier/04-finetuning`
> **Durée** : ~3 heures (demi-journée)

## Objectif pédagogique

Fine-tuner un LLM open-source (Mistral-7B) sur le **dataset Q/R conciergerie**
pour adopter le ton "HomeButler" :
- Préparer/explorer le dataset (Alpaca format, split 80/10/10)
- Comprendre LoRA / QLoRA (vs Full Fine-Tuning)
- Éviter les 5 pièges classiques du FT (Slide 9)
- Évaluer le modèle FT (perplexité, F1, similarité sémantique)

## Parcours selon votre matériel

### A) Avec GPU T4 (Google Colab gratuit) — parcours complet

1. Ouvrir `notebooks/03_finetuning_lora.ipynb` dans Colab
2. Runtime → Change runtime type → T4 GPU
3. Exécuter toutes les cellules (~20 min)
4. Exporter le modèle en GGUF + créer le Modelfile Ollama

### B) Sans GPU (Mac / CPU local) — parcours adapté

1. `python ateliers/atelier-04-finetuning/prepare_dataset.py` → générer le dataset + stats
2. `python ateliers/atelier-04-finetuning/explore_dataset.py` → distribution catégories
3. Modifier 5-10 paires manuellement pour comprendre la qualité requise
4. Discussion : *"Que change le fine-tuning dans les réponses ?"*

### C) Mode pair-sharing (recommandé en formation)

- 1 personne avec GPU Colab exécute le FT
- Les autres préparent le dataset + discutent les résultats ensemble

## Pré-requis

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_atelier04.txt
pip install -e .
cp .env.example .env  # ANTHROPIC_API_KEY si besoin
```

> Les packages FT (`transformers`, `peft`, `trl`, `bitsandbytes`) sont
> installés **dans Colab uniquement** — le notebook commence par leur `!pip install`.

## Checklist "5 pièges du Fine-Tuning" (Slide 9 Chapitre 4)

- [ ] **Catastrophic forgetting** — inclure 20-30 % de données générales
  dans le dataset pour préserver les capacités hors-domaine
- [ ] **Overfitting** — surveiller train_loss qui baisse pendant que val_loss monte
- [ ] **Mauvais base model** — Mistral-7B est OK FR, Llama-3 est meilleur EN
- [ ] **Learning rate trop élevé** — essayer 1e-4, 2e-4, 5e-4 ; jamais > 1e-3
- [ ] **Pas de split validation** — split 80/10/10 obligatoire pour détecter l'overfitting

## Questions de réflexion

1. **Pourquoi 99 % des praticiens utilisent LoRA/QLoRA et pas Full FT ?**
   _(coût VRAM : Full FT Mistral-7B = 140 GB ; QLoRA = ~12 GB → T4 gratuit suffit)_

2. **Qu'est-ce que le catastrophic forgetting ?**
   _(le modèle "oublie" ce qu'il savait hors du dataset FT → mitigation : mélanger 20-30 % de données générales dans le mix d'entraînement)_

3. **Le FT peut-il remplacer le RAG pour les infos factuelles ?**
   _(non : le FT fige les connaissances au moment du training. Pour des données qui changent (DPE, météo, stock producteurs), RAG est indispensable. Le FT est meilleur pour le STYLE/TON.)_

## Note — Distillation (Slide 10 Chapitre 4)

Hors-scope TP, à connaître :
> La distillation transfère les capacités d'un gros modèle (teacher, ex GPT-4)
> vers un petit modèle (student, ex Mistral-7B) en générant un dataset de
> paires question/réponse via le teacher, puis en fine-tunant le student.

## Critère de succès

- [ ] `prepare_dataset.py` affiche 150+ paires, format Alpaca, split 80/10/10
- [ ] `explore_dataset.py` montre la distribution équilibrée des catégories
- [ ] (Si Colab) modèle FT exporté en GGUF + chargé dans Ollama → ton plus chaleureux

→ **Atelier suivant** : déployer l'API + Streamlit + Ollama avec sécurité.
