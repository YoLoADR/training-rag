"""
Blank pédagogique du notebook AT04 — Fine-tuning LoRA.

Édite ATOMIQUEMENT (via nbformat) les 3 cellules pivotales du notebook
03_finetuning_lora.ipynb pour les remplacer par des TODO + indices.

Cellules ciblées :
  - Cell 11 : Chargement modèle Mistral-7B + BitsAndBytesConfig (QLoRA 4-bit).
  - Cell 13 : Configuration LoraConfig (r, alpha, target_modules).
  - Cell 15 : TrainingArguments + SFTTrainer.

Pourquoi un script ?
  Édition JSON manuelle d'un .ipynb = corruption garantie (UUID des cellules,
  outputs sérialisés, execution_count). nbformat lit / mute / écrit en
  préservant la structure.

Usage :
  python scripts/blank_notebook.py

Idempotent : peut être relancé, ne touche que les cellules visées.
Ce script vit UNIQUEMENT sur la branche student/04-finetuning (reproductibilité).
"""

import nbformat
from pathlib import Path

NOTEBOOK_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "03_finetuning_lora.ipynb"


CELL_11_BLANK = '''\
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL_NAME = 'mistralai/Mistral-7B-Instruct-v0.2'

# ═══════════════════════════════════════════════════════════════════════════
# 🎓 Atelier 04 § 4 — Tu dois construire la config QLoRA 4-bit et charger
#    le modèle de base Mistral-7B en quantization 4 bits.
#
# Solution finale : git diff student/04-finetuning atelier/04-finetuning \\
#                   -- notebooks/03_finetuning_lora.ipynb
# ═══════════════════════════════════════════════════════════════════════════
#
# --- Indice léger ---
# Tu dois créer un `BitsAndBytesConfig` qui :
#   - charge le modèle en 4 bits (load_in_4bit=True)
#   - fait les calculs en FP16 (bnb_4bit_compute_dtype)
#   - active la "double quantization" (gain ~0.4 bits/param)
#   - utilise le type 'nf4' (NormalFloat 4-bit, optimal pour les LLM)
#
# Puis charger le tokenizer (avec pad_token = eos_token car Mistral n'a pas
# de pad token natif) et le modèle via AutoModelForCausalLM.from_pretrained()
# en lui passant la quantization_config et device_map='auto'.
#
# Penser à : `model.config.use_cache = False` (incompatible avec
# le gradient checkpointing utilisé pendant l'entraînement).
#
# --- Indice fort ---
# bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_compute_dtype=torch.float16,
#     bnb_4bit_use_double_quant=True,
#     bnb_4bit_quant_type='nf4',
# )
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
# tokenizer.pad_token = tokenizer.eos_token
# tokenizer.padding_side = 'right'
# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_NAME,
#     quantization_config=bnb_config,
#     device_map='auto',
#     trust_remote_code=True,
# )
# model.config.use_cache = False

raise NotImplementedError(
    "Atelier 04 cellule 11 — chargement Mistral-7B en QLoRA 4-bit."
)
'''


CELL_13_BLANK = '''\
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Préparer le modèle pour l'entraînement en 4-bit (active gradient checkpointing)
model = prepare_model_for_kbit_training(model)

# ═══════════════════════════════════════════════════════════════════════════
# 🎓 Atelier 04 § 5 — Configure LoRA : choisis r, alpha, target_modules,
#    dropout, bias, task_type. Puis applique-le au modèle.
# ═══════════════════════════════════════════════════════════════════════════
#
# --- Indice léger ---
# LoRA = "Low-Rank Adaptation". On ajoute des PETITES matrices entraînables
# A et B autour des matrices figées du modèle. Le RANG r contrôle leur taille
# (donc le nombre de paramètres entraînables).
#
# Bonnes valeurs de départ pour Mistral-7B :
#   r = 8        (rang faible, suffit pour adapter le ton/style)
#   alpha = 16   (souvent 2 × r — règle de pouce LoRA paper)
#   target_modules = matrices Q et V de l'attention (la "où" on injecte LoRA)
#   dropout = 0.05  (régularisation)
#   bias = 'none'   (on n'entraîne pas les biais — économie de paramètres)
#   task_type = 'CAUSAL_LM'  (génération de texte autoregressive)
#
# Ensuite, `get_peft_model(model, lora_config)` remplace `model` par sa version
# adaptée LoRA, et tu peux appeler `model.print_trainable_parameters()` pour
# vérifier que < 1 % des params sont entraînables.
#
# --- Indice fort ---
# lora_config = LoraConfig(
#     r=8,
#     lora_alpha=16,
#     target_modules=['q_proj', 'v_proj'],
#     lora_dropout=0.05,
#     bias='none',
#     task_type='CAUSAL_LM',
# )
# model = get_peft_model(model, lora_config)
# model.print_trainable_parameters()

raise NotImplementedError(
    "Atelier 04 cellule 13 — LoraConfig + get_peft_model."
)
'''


CELL_15_BLANK = '''\
import mlflow
from trl import SFTTrainer
from transformers import TrainingArguments

# Configuration MLFlow (tracking local dans /content/mlruns) — DÉJÀ FOURNI
mlflow.set_tracking_uri('file:///content/mlruns')
mlflow.set_experiment('homebutler-finetuning')

# ═══════════════════════════════════════════════════════════════════════════
# 🎓 Atelier 04 § 6 — Configure TrainingArguments puis lance SFTTrainer
#    dans un bloc `with mlflow.start_run(...)` pour tracker l'expérience.
# ═══════════════════════════════════════════════════════════════════════════
#
# --- Indice léger ---
# Hyperparamètres CLÉS à choisir (cf. carnet de bord — "fine-tuning LoRA") :
#   - num_train_epochs   : 3 epochs suffisent en LoRA (sinon overfit)
#   - per_device_train_batch_size : 4 sur T4 (16 Go VRAM)
#   - gradient_accumulation_steps : 4  → batch effectif = 16
#   - learning_rate : 2e-4 (LoRA tolère un LR plus élevé que le full FT)
#   - warmup_steps : 50, lr_scheduler_type : 'cosine'
#   - fp16 = True (calculs en FP16 pour la vitesse sur T4)
#   - optim : 'paged_adamw_32bit' (optimiseur paginé, économise VRAM)
#
# Puis dans `with mlflow.start_run(run_name='mistral-homebutler-qlora'):`
#   1. mlflow.log_params({...})  ← TOUS les hyperparams au-dessus
#   2. trainer = SFTTrainer(model=model, train_dataset=..., eval_dataset=...,
#                            peft_config=lora_config, dataset_text_field='text',
#                            max_seq_length=512, tokenizer=tokenizer,
#                            args=training_args)
#   3. train_result = trainer.train()
#   4. mlflow.log_metrics({'final_train_loss': train_result.training_loss, ...})
#   5. trainer.save_model(OUTPUT_DIR)
#
# --- Indice fort ---
# Voir la version corrigée via :
#   git diff student/04-finetuning atelier/04-finetuning -- notebooks/03_finetuning_lora.ipynb

raise NotImplementedError(
    "Atelier 04 cellule 15 — TrainingArguments + SFTTrainer + MLFlow run."
)
'''


BLANKS = {
    11: CELL_11_BLANK,
    13: CELL_13_BLANK,
    15: CELL_15_BLANK,
}


def main() -> None:
    if not NOTEBOOK_PATH.exists():
        raise FileNotFoundError(f"Notebook introuvable : {NOTEBOOK_PATH}")

    nb = nbformat.read(str(NOTEBOOK_PATH), as_version=4)

    for idx, new_src in BLANKS.items():
        if idx >= len(nb.cells):
            raise IndexError(f"Cellule {idx} hors index (notebook a {len(nb.cells)} cellules)")
        cell = nb.cells[idx]
        if cell.cell_type != "code":
            raise ValueError(f"Cellule {idx} n'est pas une cellule de code (type={cell.cell_type})")
        cell["source"] = new_src
        cell["outputs"] = []
        cell["execution_count"] = None
        print(f"  ✓ Cellule {idx} blankée")

    nbformat.write(nb, str(NOTEBOOK_PATH))
    print(f"\nNotebook réécrit : {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
