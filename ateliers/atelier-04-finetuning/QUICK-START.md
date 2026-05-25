# ⚡ Atelier 04 — Quick-Start (1 page)

> **Objectif** : fine-tuner Mistral-7B avec LoRA sur 500 paires Q/R conciergerie. Loss ≤ 1.5 après 3 epochs.

## 🚦 Pré-vol (10 min)
1. Ouvrir Google Colab avec **GPU T4 sélectionné** (Runtime → Change runtime type → T4 GPU).
2. Vérifier le quota : `!nvidia-smi` → tu dois voir Tesla T4, 15 Go VRAM.

## 🍳 Recette de cuisine — 6 étapes

| # | Étape | Fichier | Vulgarisation |
|---|---|---|---|
| **1** | **Construire le dataset** (À CODER `generate()`) | `scripts/generate_qa_dataset.py` | _format Alpaca_ = `{"instruction": "...", "input": "...", "output": "..."}` 1 ligne par ex (JSONL). C'est le format que HuggingFace `datasets` mange nativement. |
| **2** | **Augmenter le dataset** (À CODER `paraphrase_question`) | `scripts/augment_qa_dataset.py` | _data augmentation sans LLM_ = règles linguistiques + RNG seeded → reproductible. Vise 500 paires depuis 150. |
| **3** | **Charger Mistral en 4-bit** (À CODER cellule 11) | `notebooks/03_finetuning_lora.ipynb` | _QLoRA 4-bit_ = on quantise les poids en 4 bits (fp4 ou nf4) → 14 Go → 4 Go VRAM. Calculs en FP16, double quantization pour gagner ~0.4 bits/param. |
| **4** | **Configurer LoRA** (À CODER cellule 13) | idem notebook | _LoRA r=8_ = on ajoute des PETITES matrices entraînables (rang 8) sur Q et V de l'attention. <1 % des params sont entraînables. Analogie : « post-its sur quelques pages du livre, sans réimprimer le livre ». |
| **5** | **Lancer SFTTrainer** (À CODER cellule 15) | idem notebook | _SFTTrainer (TRL)_ = trainer spécialisé Supervised Fine-Tuning. 3 epochs, batch=4, gradient_accumulation=4 (→ batch effectif 16), lr=2e-4, scheduler cosine. ~15 min sur T4. |
| **6** | **Évaluer base vs FT** | cellules 18-19 du notebook | 🎯 cible : ROUGE-L FT > ROUGE-L base ; loss train ≤ 1.5 ; adapter < 50 Mo. |

## 🧠 Analogie LoRA
Le LLM est une **encyclopédie de 14 Go**. Plutôt que de la **réécrire entièrement** (full fine-tuning, coûteux), on **colle des notes adhésives** sur quelques pages (matrices Q et V de chaque couche). À l'usage, on lit le livre + on consulte les notes. Les notes pèsent < 50 Mo et sont rapides à entraîner.

## 🛟 Bloqué > 15 min ?
1. Indices **léger / fort** dans les commentaires de chaque cellule.
2. Verbalise : « pourquoi `lora_alpha = 2 × r` est-il une bonne valeur par défaut ? »
3. ```bash
   git diff student/04-finetuning atelier/04-finetuning -- notebooks/03_finetuning_lora.ipynb
   ```

## ✅ Validation
```bash
python scripts/generate_qa_dataset.py       # produit data/qa_dataset/concierge_qa.jsonl
python scripts/augment_qa_dataset.py        # produit augmented_concierge_qa.jsonl ~500 paires
# puis : ouvrir le notebook sur Colab, run all cells
python ateliers/atelier-04-finetuning/checkpoints/check_1.py
```
