# Ateliers progressifs — Formation RAFT

Ce dossier contient les **6 ateliers fil rouge** alignés sur les 6 chapitres
de la formation RAFT (3 jours). Chaque atelier construit incrémentalement
le projet final **HomeButler AI** (assistant conciergerie pour logement).

## Comment démarrer un atelier

Chaque atelier correspond à une **branche git dédiée** contenant le projet
à l'état exact de ce chapitre (zéro débordement).

```bash
# 1. Se placer sur la branche de l'atelier
git checkout atelier/02-rag-simple    # ou 01, 03, 04, 05, 06

# 2. Créer l'environnement Python dédié (recommandé : 1 venv par atelier)
python -m venv .venv && source .venv/bin/activate

# 3. Installer les dépendances spécifiques de l'atelier
pip install -r requirements_atelier02.txt

# 4. Installer le package homebutler en mode editable
#    (OBLIGATOIRE — sans ça, les imports ne marchent pas)
pip install -e .

# 5. Configurer les secrets
cp .env.example .env
# Éditer .env → ajouter au minimum ANTHROPIC_API_KEY

# 6. Vérifier que le package est importable
python -c "import homebutler; print('Package HomeButler OK')"

# 7. Lancer l'exercice de l'atelier
python ateliers/atelier-02-rag-simple/exercice.py
```

## Comment démarrer — point d'entrée élève

**Le point d'entrée élève est `GUIDE-ELEVE.md`**, pas `README-formateur.md` (réservé aux formateurs).

Avant le premier atelier, faire l'**Atelier 00 Pré-vol** (`atelier-00-prevol/GUIDE-ELEVE.md`) pour préparer l'environnement une fois pour toutes.

## Structure d'un atelier

```
ateliers/atelier-0X-nom/
├── GUIDE-ELEVE.md            ← 📖 Point d'entrée élève — mission + indices + Bug Hunt
├── README-formateur.md       ← instructions formateur (contexte, débrief)
├── exercice.py               ← squelette à compléter (TODOs)
├── .claude/
│   ├── CLAUDE.md             ← scope strict pour Claude Code / Cursor
│   └── settings.json         ← hook UserPromptSubmit (anti-scope-leak)
├── .cursorrules              ← équivalent scope strict pour Cursor
├── bugs/
│   ├── v1.patch              ← bug à appliquer (git apply)
│   ├── test_v1.py            ← test qui ÉCHOUE avec le bug, PASSE une fois réparé
│   └── v1_explanation.md     ← QCM vrai/faux sur la cause racine
└── checkpoints/
    ├── check_1.py            ← QCM auto-corrigé intermédiaire
    └── check_final.py        ← QCM auto-corrigé final (décide Sprint vs Bonus)
```

La `solution.py` est disponible sur la branche `solution/at0X` (non checkoutée par défaut).

Certains ateliers ont des fichiers supplémentaires :
- `evaluate_rag.py` (02) — métriques Recall@k, faithfulness
- `gradio_demo.py` (03) — interface chat (Bonus)
- `prepare_dataset.py` / `explore_dataset.py` (04) — dataset FT
- `test_securite.sh` / `checklist.md` (05) — sécurité, déploiement
- `evaluate_pipeline.py` / `grille_decision.md` (06) — benchmark comparatif
- `evaluate_pipeline.py` / `grille_decision.md` (06) — comparaison RAG vs FT

## Mapping formation → ateliers

| Branche                          | Jour       | Chapitre PDF                       | Objectif TP                                                          |
|----------------------------------|------------|------------------------------------|----------------------------------------------------------------------|
| `atelier/01-llm-baseline`        | J1 matin   | Introduction LLM + concepts RAG    | LLM seul → observer hallucinations, comparer 2 modèles               |
| `atelier/02-rag-simple`          | J1 a.-m.   | Création d'un RAG simple           | Chatbot RAG FAISS, 3 stratégies chunking, métriques RAGAs            |
| `atelier/03-pipeline-agent`      | J2 matin   | Pipeline RAG + Agent ReAct         | Agent LangChain 4 outils, trace ReAct, EnsembleRetriever             |
| `atelier/04-finetuning`          | J2 a.-m.   | Fine-tuning HuggingFace            | LoRA/QLoRA Colab, dataset Alpaca, 5 pièges FT, évaluation PPL+F1     |
| `atelier/05-deploiement`         | J3 matin   | Déploiement + supervision          | FastAPI + Streamlit + Langfuse + Ollama, sécurité                    |
| `atelier/06-finetune-vs-rag`     | J3 a.-m.   | Fine-tuning vs RAG                 | Recall@k 3 modes, RAFT, benchmarks, grille de décision               |

## Vérifier le scope d'une branche

Pour s'assurer qu'une branche ne contient pas de code d'un atelier suivant :

```bash
bash scripts/verify_branch_scope.sh
```

## Conventions de commentaires pédagogiques dans le code

- **Concept RAG** (ateliers 01-03) — bloc encadré `═══ CONCEPT RAG : … ═══`
- **Concept Fine-Tuning** (atelier 04, cellules notebook) — `# ─── FT CONCEPT : … ───`
- **Sécurité / production** (atelier 05) — `# SÉCURITÉ : …`

Les solutions importent toujours depuis `homebutler/` (pas de duplication
de code) et ajoutent les commentaires pédagogiques autour des appels.

## Démarrer depuis zéro (élève J1 matin)

```bash
git clone <repo>
cd pre-training-rag
git checkout atelier/01-llm-baseline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_atelier01.txt && pip install -e .
cp .env.example .env
# (éditer .env)
python ateliers/atelier-01-llm-baseline/exercice.py
```
