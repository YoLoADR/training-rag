# Atelier 00 — Pré-vol (30-60 min — à faire la veille !)

> Ne commence aucun atelier sans avoir complété ce Pré-vol.
> Un setup raté = 30 minutes perdues demain matin, et ça démarre mal.
> Ce guide se fait en une fois, la veille ou quelques heures avant la formation.

---

## Objectif

Préparer ton environnement une fois pour toutes, télécharger les modèles lourds
(qui pèsent plusieurs centaines de MB), générer les données de la formation, et
vérifier tous tes accès avant de commencer les ateliers.

**Résultat attendu :** `bash scripts/check_atelier_ready.sh 01` retourne `Atelier 01 : PRÊT`

---

## Checklist complète

### Étape 1 — Clone et venv (10 min)

**Cloner le repo :**

```bash
git clone <URL_DU_REPO> pre-training-rag
cd pre-training-rag
```

**Créer et activer le venv pour chaque atelier :**

Chaque atelier a son propre environnement pour éviter les conflits de versions.
Tu peux les créer tous maintenant ou un par un avant chaque atelier.

```bash
# Création (fais-le pour les ateliers que tu vas faire)
python3 -m venv .venv_atelier01
python3 -m venv .venv_atelier02
python3 -m venv .venv_atelier03
python3 -m venv .venv_atelier04
python3 -m venv .venv_atelier05
python3 -m venv .venv_atelier06
```

**Installer les dépendances :**

```bash
# Pour l'atelier du jour (exemple avec At.01)
source .venv_atelier01/bin/activate
pip install -r requirements_atelier01.txt

# Pour les autres ateliers (en fond si tu veux tout installer d'un coup)
source .venv_atelier02/bin/activate && pip install -r requirements_atelier02.txt
source .venv_atelier03/bin/activate && pip install -r requirements_atelier03.txt
source .venv_atelier04/bin/activate && pip install -r requirements_atelier04.txt
source .venv_atelier05/bin/activate && pip install -r requirements_atelier05.txt
source .venv_atelier06/bin/activate && pip install -r requirements_atelier06.txt
```

**Verification :**
- [ ] `python --version` affiche Python 3.10 ou 3.11
- [ ] `which python` pointe vers `.venv_atelierXX/bin/python`

---

### Étape 2 — Clés API (5 min)

**Copier le fichier de configuration :**

```bash
cp .env.example .env
```

**Ouvrir `.env` et renseigner :**

```dotenv
# Obligatoire pour tous les ateliers (01, 02, 03, 05, 06)
ANTHROPIC_API_KEY=sk-ant-...

# Obligatoire pour At.05 — Langfuse (observabilité LLM)
# Crée un compte gratuit sur https://cloud.langfuse.com (< 2 min)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...

# Optionnel — si tu utilises Ollama en local (alternative à Anthropic)
# LLM_PROVIDER=ollama
# OLLAMA_MODEL=llama3.2

# Évite les warnings ChromaDB dans At.03
ANONYMIZED_TELEMETRY=false

# Scope At.05 : routes de comparaison désactivées par défaut (activées en At.06)
ENABLE_COMPARE_ROUTES=false
```

**Où obtenir ANTHROPIC_API_KEY :**
1. Va sur https://console.anthropic.com
2. Menu "API Keys" → "Create Key"
3. Copie la clé (commence par `sk-ant-`)

**Où obtenir les clés Langfuse (At.05) :**
1. Va sur https://cloud.langfuse.com
2. "Sign up" → compte gratuit, pas de CB requise
3. "Create project" → "Settings" → "API Keys"
4. Copie les deux clés (Public Key et Secret Key)

**Verification :**
- [ ] `.env` contient `ANTHROPIC_API_KEY=sk-ant-...` (pas vide, pas "votre_clé_ici")
- [ ] Test rapide : `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OK' if os.getenv('ANTHROPIC_API_KEY') else 'MANQUANT')"`

---

### Étape 3 — Pré-téléchargement des modèles (15-20 min, peut tourner en fond)

Certains modèles pèsent 100-500 MB. Télécharge-les maintenant pour éviter
d'attendre pendant les ateliers.

**Modèle d'embeddings pour At.02 et At.03 (~120 MB) :**

```bash
source .venv_atelier02/bin/activate
python -c "
from fastembed import TextEmbedding
print('Téléchargement du modèle d\\'embeddings...')
list(TextEmbedding('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'))
print('OK — modèle en cache')
"
```

> Note : le message `mean pooling instead of CLS embedding` est **normal** — ignore-le.
> Ne passe pas en version 0.5.1 pour corriger ce warning, c'est un faux positif.

**FAISS sur Mac ARM (si erreur) :**
```bash
pip install "faiss-cpu>=1.13.2" --upgrade
```

**Pour At.04 — Google Colab :**
- Vérifie que tu as un compte Google actif sur https://colab.research.google.com
- Connecte-toi et crée un notebook test pour vérifier l'accès au GPU T4
- Le notebook du TP sera fourni à l'ouverture de l'atelier 04

---

### Étape 4 — Génération des données (5 min)

Les PDFs et données de la formation HomeButler sont générés par des scripts.
Lance-les dans le venv de base (ou At.01) :

```bash
source .venv_atelier01/bin/activate

# Génère les notices PDF des propriétés HomeButler
python scripts/generate_documents.py

# Génère les données de consommation énergétique
python scripts/generate_energy_data.py

# Génère la liste des producteurs locaux
python scripts/generate_producers.py
```

**Verification :**
- [ ] `ls data/documents/*.pdf | wc -l` affiche un nombre > 0
- [ ] `ls data/` affiche `documents/` et d'autres dossiers de données

**Pré-construction de l'index FAISS pour At.02 (optionnel — peut attendre At.02) :**

```bash
source .venv_atelier02/bin/activate
python -c "
from homebutler.rag.vectorstore_faiss import build_faiss_index
print('Construction index FAISS...')
build_faiss_index()
print('Index ready')
"
```

---

### Étape 5 — Vérification des ports (2 min)

Les ateliers utilisent ces ports :
- **8000** — API FastAPI (At.05, At.06)
- **8501** — Streamlit (At.05, At.06)
- **3300** — Langfuse local (At.05, optionnel)

Vérifie qu'ils sont libres :

```bash
lsof -ti :8000 :8501 :3300
```

Si cette commande retourne des lignes, ces ports sont occupés.
Note les PID et arrête les processus concernés avec `kill <PID>` ou `kill -9 <PID>`.

**Verification :**
- [ ] `lsof -ti :8000 :8501 :3300` retourne rien (ports libres)

---

### Étape 6 — Test final (2 min)

Lance le script de vérification pour l'atelier 01 :

```bash
source .venv_atelier01/bin/activate
bash scripts/check_atelier_ready.sh 01
```

Si tout est vert :
```
============================================
  Atelier 01 : PRÊT
============================================
```

Si des ❌ apparaissent, corrige-les avant de continuer.

---

## Notes importantes — problèmes connus

### fastembed : warning "mean pooling"
```
Embeddings are computed using mean pooling instead of CLS embedding.
```
C'est **normal** et **attendu**. Le modèle fonctionne correctement. Ne pin pas la version
à 0.5.1 pour corriger ce warning — ça crée des incompatibilités avec les requirements.

### FAISS sur Mac ARM (Apple Silicon M1/M2/M3)
Si tu vois `ImportError: libfaiss.so: cannot open shared object file` :
```bash
pip install "faiss-cpu>=1.13.2" --upgrade
```

### Langfuse : version requise
Les requirements d'At.05 pinnent `langfuse<4.0.0`. Il y a des breaking changes majeurs
entre Langfuse v3 et v4. Ne pas upgrader manuellement.

Vérifie ta version :
```bash
pip show langfuse | grep Version
```
Si tu vois `Version: 4.x.x`, downgrade :
```bash
pip install "langfuse<4.0.0"
```

### Rate limits Anthropic (si > 10 stagiaires en même temps)
Des erreurs HTTP 429 peuvent apparaître lors d'usages intensifs en groupe.
Solution : alterner avec Ollama en ajoutant `LLM_PROVIDER=ollama` dans `.env`.
Ollama doit être installé : https://ollama.com

### ChromaDB telemetry warnings (At.03)
Le message `Anonymized telemetry enabled` peut apparaître. Pour le désactiver :
Ajoute `ANONYMIZED_TELEMETRY=false` dans ton `.env`. C'est déjà inclus dans
le template `.env.example`.

---

## Checklist de validation finale

- [ ] `git clone` OK et `cd pre-training-rag` OK
- [ ] venv créé et activé pour At.01 (et les suivants si tu veux)
- [ ] `pip install -r requirements_atelier01.txt` sans erreur
- [ ] `.env` créé depuis `.env.example` avec ANTHROPIC_API_KEY renseignée
- [ ] Clés Langfuse renseignées (pour At.05)
- [ ] Modèle embeddings téléchargé (fastembed)
- [ ] PDFs générés (`data/documents/*.pdf`)
- [ ] Ports 8000, 8501, 3300 libres
- [ ] `bash scripts/check_atelier_ready.sh 01` retourne `PRÊT`

Tout est bon ? Tu es prêt pour la formation. A demain !
