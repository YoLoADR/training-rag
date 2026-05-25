# 🚀 Démarrer un atelier — Guide élève

> Tu viens d'arriver sur la formation **HomeButler AI — RAFT**. Ce fichier te
> dit en 8 étapes comment basculer sur un atelier, où trouver les supports,
> et comment récupérer la solution si tu bloques.

---

## Vue d'ensemble — 6 ateliers progressifs

| AT | Thème | Branche élève | Concepts blankés |
|----|-------|---------------|------------------|
| 01 | LLM Baseline | `student/01-llm-baseline` | `get_llm()`, `get_llm_cached()`, 4 templates de prompts |
| 02 | RAG Simple FAISS | `student/02-rag-simple` | 3 stratégies de chunking, `get_embeddings`, `build/load_faiss_index` |
| 03 | Pipeline Agent ReAct | `student/03-pipeline-agent` | `get_agent_executor` (boucle ReAct), `get_ensemble_retriever` |
| 04 | Fine-tuning LoRA/QLoRA | `student/04-finetuning` | 3 cellules notebook (QLoRA, LoraConfig, SFTTrainer), 2 scripts dataset |
| 05 | Déploiement FastAPI | `student/05-deploiement` | `_call_rag_only`, `_call_agent`, endpoint `/rag/retrieve` |
| 06 | RAG vs FT vs RAFT | `student/06-finetune-vs-rag` | `evaluate_strategies`, `compare_modes`, `show_summary` |

Pour chaque atelier, les branches `atelier/XX-…` contiennent la **version corrigée** (à utiliser uniquement pour `git diff` en cas de blocage).

---

## Procédure de démarrage (8 étapes)

### 1. Cloner le repo et créer un venv

```bash
git clone <repo-url>
cd training-rag
python -m venv .venv && source .venv/bin/activate
```

### 2. Basculer sur l'atelier voulu

```bash
git checkout student/01-llm-baseline      # ou 02, 03, 04, 05, 06
```

### 3. Installer les dépendances

```bash
pip install -e .
# ou pour un atelier précis :
pip install -r requirements_atelier02.txt
```

### 4. Vérifier l'environnement

```bash
bash scripts/check_atelier_ready.sh 01    # remplace 01 par ton atelier
# Vérifie : clés API (.env), modèles téléchargés, deps installées, données seed
```

### 5. Lire les supports — 1-page d'abord, complet ensuite

```bash
cat ateliers/atelier-01-llm-baseline/QUICK-START.md     # 1 page — recette 6 étapes
cat ateliers/atelier-01-llm-baseline/GUIDE-ELEVE.md     # complet — mission, carnet de bord, exercices
```

> 💡 **Slides de présentation** : si ton formateur les a partagés, ouvre `slides/atelier-XX-student.md` (dans le repo `pre-training-rag`) pour voir la version corrigée commentée bloc par bloc — utile pour comprendre AVANT de coder.

### 6. Repérer les fichiers blankés

Dans la section « 🎯 Atelier XX en un coup d'œil » du `GUIDE-ELEVE.md`,
la sous-section **🛠️ « À toi de coder »** liste les fichiers à compléter,
avec leur fonction et le type de blanking (corps entier `NotImplementedError`
ou paramètre ciblé `# TODO`).

Ouvre ces fichiers : chaque fonction blankée a une docstring avec **2 niveaux
d'indices** :
- **Indice léger** — « quel objet chercher »
- **Indice fort** — « quels arguments / quels appels »

### 7. Coder, tester, checkpoint

```bash
# Code dans les fichiers marqués 🛠️
# Test rapide :
pytest ateliers/atelier-XX-*/

# Checkpoint (QCM + verbalisation) :
python ateliers/atelier-XX-*/checkpoints/check_1.py

# Métriques cibles selon l'atelier (voir QUICK-START.md "Validation")
```

### 8. Bloqué > 15 min ? Récupérer la solution

```bash
# En DERNIER recours, après avoir lu les 2 niveaux d'indices et tenté :
git diff student/01-llm-baseline atelier/01-llm-baseline -- homebutler/llm/provider.py
```

> 💡 **Avant de regarder le diff** : passe par le checkpoint `check_1.py`. Il te demandera de **verbaliser** ta compréhension avant de te débloquer. Si tu ne peux pas verbaliser, tu n'as pas encore compris — pas la peine de copier la solution, tu vas la copier sans rien apprendre.

---

## Sécurité anti-vibe-coding (Claude Code / Cursor)

Chaque dossier d'atelier contient un `.claude/CLAUDE.md` qui **refuse**
explicitement de donner le code complet d'un `NotImplementedError`. Si tu
utilises Claude Code ou Cursor, ne le désactive pas — il te posera des
questions socratiques que tu DOIS verbaliser avant de progresser. C'est
ce qui transforme le « j'ai un code qui marche » en « je sais POURQUOI ça
marche ».

---

## Ordre d'exécution Bug Hunt (cohabitation avec les blanks)

Chaque atelier a un système Bug Hunt existant (`bugs/v*.patch` + `bugs/test_v*.py`).
**Ordre obligatoire** :

1. **Tronc commun** (~1h40) — remplir les blanks en suivant les indices.
   `pytest ateliers/atelier-XX-*/` doit passer vert.
2. **Sprint Bug Hunt** (~30 min) — appliquer `bugs/v1.patch`, diagnostiquer
   l'échec de `bugs/test_v1.py`, répondre au QCM `v1_explanation.md`. Idem v2, v3.

Le `solution.py` du dossier d'atelier IMPORTE depuis `homebutler/`. Tant que
tu n'as pas rempli les blanks de `homebutler/`, `python solution.py` plante
sur `NotImplementedError` — c'est intentionnel (anti-fraude `cat solution.py`).

---

## Lien avec le repo formateur

Les supports formateur (slides, guide formateur détaillé avec déroulé minute
par minute, FAQ) vivent dans le repo `pre-training-rag/` (séparé). En tant
qu'élève tu n'as pas besoin d'y aller — tout ce qu'il te faut est ici.

---

## Aide

- Problème de setup → `bash scripts/check_atelier_ready.sh XX` (très bavard)
- Question sur un concept → relis le `GUIDE-ELEVE.md` section « Carnet de bord » de l'atelier en cours
- Bug que tu ne comprends pas → demande au formateur (ou via le canal Slack/Discord de la formation)

Bonne formation ! 🚀
