# Atelier 04 — Fine-tuning LoRA/QLoRA (demi-journée, ~3h30)

> **Comment ce guide differe de l'ancien GUIDE-ELEVE.md** : ici tu ne suis pas un step-by-step.
> Tu recois une mission, des contraintes, des indices ; tu construis. Si tu cherches le tuto,
> ouvre `prepare_dataset.py` et lis les commentaires -- mais alors tu n'apprends pas.

---

## 🚦 Pré-vol (avant de commencer)

- [ ] `bash scripts/check_atelier_ready.sh 04` retourne OK
- [ ] Compte Google Colab verifie (acces GPU T4 gratuit disponible)
- [ ] Compte HuggingFace cree : https://huggingface.co/join (gratuit, 1 min)
- [ ] `python ateliers/atelier-04-finetuning/prepare_dataset.py` tourne sans erreur
- [ ] J'ai lu la section "Perimetre" ci-dessous

---

## La mission

Le PM HomeButler te demande :

> "Nos reponses sont correctes mais elles sonnent generiques. On veut que l'assistant parle
> 'Merenza' : chaleureux, en francais impeccable, avec un format de reponse strict
> (accueil personnalise, corps structure, signature). Le RAG ne peut pas faire ca --
> c'est un probleme de style, pas de connaissance. Prepare le dataset, explique-moi
> pourquoi le fine-tuning est la bonne solution ici, et lance le training sur Colab."

**Livrable** :
1. Dataset equilibre (>= 150 paires, distribution equilibree par categorie)
2. Notebook Colab lance et training observe jusqu'a la 1ere epoch
3. Rapport perplexite note dans ton carnet

**Criteres de succes auto-verificables** :
- [ ] `python ateliers/atelier-04-finetuning/explore_dataset.py` montre >= 3 catégories avec >= 10 paires chacune
- [ ] Fichiers `data/qa_dataset/concierge_qa_train.jsonl`, `_val.jsonl`, `_test.jsonl` presents et non vides
- [ ] val_loss < train_loss x 1.3 apres 3 epochs (pas d'overfitting visible)
- [ ] Tu peux expliquer en 2 phrases pourquoi le FT et pas le RAG pour ce probleme de style

**Budget temps** : 1h40 Core Mac (+30 min Sprint OU 60-70 min Bonus Colab)

---

## Périmètre de cet atelier

**Dans le scope :**
- LoRA (Low-Rank Adaptation) et QLoRA (quantized LoRA)
- Dataset au format Alpaca (instruction/input/output)
- Split dataset : 80% train / 10% validation / 10% test
- Metriques de training : perplexite, loss, val_loss
- Hyperparametres : `learning_rate`, `r` (LoRA rank), `epochs`, `batch_size`
- Problemes : overfitting (val_loss > train_loss), catastrophic forgetting
- Sur-échantillonnage pour dataset déséquilibré
- Google Colab T4 pour le training (notebook : `notebooks/03_finetuning_lora.ipynb`)
- Versionning dataset : HuggingFace Hub, git LFS
- `prepare_dataset.py`, `explore_dataset.py`

**Hors scope (ateliers suivants) :**
- API FastAPI, endpoints REST, deploiement
- Interface Streamlit
- RAFT (Retrieval-Augmented Fine-Tuning)
- Evaluation comparative RAG vs FT (reservee a At.06)

**Garde-fou active** : `.claude/CLAUDE.md` local + hook UserPromptSubmit

---

## Choisis ta piste

| | Piste Build | Piste Vibe |
|---|---|---|
| **Mode** | Code a la main, Claude/Cursor en mode `plan` ou ferme | Delegation OK |
| **Indices** | API, imports, fichiers a lire fournis dans ce guide | Prompt-guard actif |
| **Checkpoint** | Explique ce que tu as code | Explique en 3 phrases + modifie 1 parametre + predit l'impact |
| **Bug Hunt** | Instrumente, inspecte, raisonne | Formule une hypothese AVANT de regarder le patch |

**Declare ta piste ici (ecris-le dans ton carnet)** : Build / Vibe

---

## Carnet de bord -- Lexique obligatoire

> Ce tableau est a lire AVANT toute manipulation. Les sections suivantes y font reference.
> Le mini-quiz `check_1.py` te demandera 3 termes au hasard.

| Terme jargon | Ce que c'est (sans jargon) | Analogie quotidienne |
|---|---|---|
| **GPU** (Graphics Processing Unit) | Carte dédiée aux calculs massivement paralleles. Indispensable au training de gros modeles. | Une cuisine de restaurant avec 100 cuisiniers qui font la meme tache en parallele, vs. ta cuisine perso (CPU) avec 1 cuisinier polyvalent. |
| **RAM vs VRAM** | RAM = mémoire vive de ton ordi. VRAM = mémoire vive de la carte graphique (GPU). Un modele 7B "tient" en VRAM, pas en RAM. | RAM = ton frigo (large mais lent a acceder). VRAM = ton plan de travail (petit mais ultra-rapide pour cuisiner). |
| **Colab T4 (gratuit)** | Service Google qui te prête un GPU "T4" gratuitement quelques heures par jour, dans un notebook web. | Un coworking gratuit avec une cuisine pro (GPU T4) ; tu peux y aller 4h/jour. |
| **Quantization 4-bit** | Stocker les poids du modele sur 4 bits au lieu de 16 -- 4x moins de memoire. Cout : legere perte de precision. | Compresser une photo HD en JPG basse qualite : 4x plus leger, presque pas visible. |
| **Mistral-7B = ~12 GB VRAM en QLoRA** | Le modele Mistral a 7 milliards de parametres, compresse, tient sur 12 GB de memoire GPU. Le T4 a 15 GB, ca passe. | Une voiture de 7 places (Mistral-7B) qui rentre dans un garage de 12 m2 grace a un demontage astucieux (QLoRA). |
| **Learning rate (`lr`)** | "Pas d'apprentissage". A chaque exemple vu, le modele ajuste ses poids un peu. `lr` dit de combien. Trop grand -> ca part en vrille (loss = NaN). Trop petit -> n'apprend rien. | Regler la vitesse d'un cuisinier qui ajuste sa recette : trop vite il rate, trop lentement il ne progresse jamais. Sweet spot LoRA : 1e-4 a 5e-4. |
| **Epoch** | 1 epoch = le modele a vu tout le dataset une fois. 5 epochs = il l'a vu 5 fois. | Relire 5 fois ses fiches de revision avant un examen. |
| **Grid search** | Tester systématiquement plusieurs combinaisons de parametres (ex: 3 `lr` x 3 `epochs` = 9 essais). | Gouter 9 versions d'une sauce avec 3 doses de sel x 3 doses de sucre pour trouver la meilleure. |
| **Loss / val_loss** | Loss = écart moyen entre la prédiction du modele et la vraie reponse. On veut qu'il baisse. `val_loss` = pareil sur des questions jamais vues (set de validation). | Note d'un eleve qui s'entraine : `loss` = note aux exercices du cours ; `val_loss` = note au controle blanc. Si la note au controle est bien plus mauvaise -> il a appris par coeur, pas compris. |
| **Dataset déséquilibré** | Quand certaines catégories sont sur-représentées (ex: 66 questions "autres" vs 6 "marketplace"). Le modele apprend bien "autres" et rate "marketplace". | Un prof qui ne donne que des exercices de maths : son eleve sera nul en francais le jour de l'examen. |
| **Sur-échantillonner** | Dupliquer (ou créer des variantes) des exemples des catégories sous-représentées pour reeequilibrer. | Faire repasser 10 fois les exercices de francais a l'eleve pour compenser. |
| **Versionner le dataset** (git LFS / HF Hub) | git classique gere mal les gros fichiers binaires. git LFS = extension pour stocker les fichiers lourds a part. HF Hub = "GitHub des modeles" (HuggingFace). | Une bibliotheque qui a un depot special pour les encyclopedies (trop lourdes pour les etageres normales). |
| **W&B artifacts** | Weights & Biases = outil pro de suivi d'expériences ML. "Artifacts" = il garde une trace de chaque dataset, chaque modele entraine, avec leurs versions. | Un cahier de laboratoire qui photographie chaque eprouvette a chaque manip -- tu peux toujours retrouver "celle du mardi 14h". |
| **HF Hub (HuggingFace Hub)** | Plateforme publique ou les chercheurs publient leurs modeles. Tu peux telecharger Mistral, Llama, etc. en une ligne de code. | Steam / App Store, mais pour les modeles IA. |
| **Catastrophic forgetting** | Le modele, en apprenant ton domaine, oublie ce qu'il savait avant (anglais, code...). | Un cuisinier qui apprend a fond la patisserie et oublie comment faire un steak. Fix : melanger 20-30% d'exercices generaux dans la formation. |
| **Perplexite** | Mesure de "surprise" du modele face a la bonne reponse. Plus c'est bas, mieux c'est. | Note d'incomprehension. Si la bonne reponse "surprend" le modele -> il l'a mal apprise. |

### RAG vs Fine-tuning -- la confusion numéro 1 des debutants

| | RAG | Fine-tuning |
|---|---|---|
| **Apprend** | Des faits recuperables | Un style / format / ton |
| **Mise a jour** | Re-indexer (minutes) | Re-entrainer (heures-jours) |
| **Cout recurrent** | Embeddings + LLM par requete | Hosting du modele FT |
| **Quand utiliser** | Donnees factuelles qui changent | Voice / persona / format specifique |

**Regle d'or** : "Le FT apprend a parler, le RAG apprend a savoir."

**Pour cette mission** : le PM veut un ton "Merenza" -- c'est du style, pas des faits. RAG ne peut pas imposer un ton.
FT, oui.

### Architecture LoRA/QLoRA

```
Modele Mistral-7B (gele -- 7 milliards de parametres, on ne les touche pas)
        |
        +-- LoRA matrices (petites, ~1% des poids -- on entraine UNIQUEMENT ca)
        |   faiss_k=8 --> r=8 matrices de rang 8
        |
        v
Modele Mistral-7B + adaptateur LoRA = comportement "Merenza"
```

Full FT = refaire tous les fils electriques de la maison.
LoRA = poser des prises supplementaires.
QLoRA = poser des prises et utiliser des cables plus fins (4-bit).

**Format Alpaca** (ce que le trainer attend) :
```json
{
  "instruction": "Tu es HomeButler, assistant concierge chaleureux...",
  "input":       "Comment regler ma chaudiere ?",
  "output":      "Bonjour ! Avec plaisir... [ton Merenza]"
}
```

---

## TRONC COMMUN (1h40)

### Étape 1 — Explorer le dataset (20 min)

**Objectif** : comprendre la structure du dataset, detecter le déséquilibré entre catégories,
preparer le diagnostic avant de corriger.

**Manipulation** :
```bash
python ateliers/atelier-04-finetuning/prepare_dataset.py
python ateliers/atelier-04-finetuning/explore_dataset.py
```

**Ce que tu dois observer** :
- Distribution des catégories (`explore_dataset.py` affiche les barres)
- La catégorie "marketplace" est significativement sous-representee vs "autres"
  (cf. Carnet de bord, ligne *Dataset déséquilibré*)
- Longueur mediane des questions et reponses
- Nombre de paires dupliquees (attendu : ~45, delibere pour la robustesse)

**Indices Build** :
- Lis `prepare_dataset.py` : la fonction `categorize()` classe les paires par mots-cles
- La fonction `split_train_val_test()` effectue le split 80/10/10 avec `seed=42`
- Les fichiers de sortie sont dans `data/qa_dataset/`

**Question cle** : si tu lances le training avec ce dataset tel quel, sur quelles catégories
le modele sera-t-il mauvais ? Pourquoi ?

---

**Checkpoint 1** -- lance `python ateliers/atelier-04-finetuning/checkpoints/check_1.py`

*Sans validation du checkpoint -> on ne passe pas a l'etape suivante.*

---

### Mini-lab — Sur-échantillonnage (15 min)

**Variable a faire varier** : composition du dataset (taille et equilibre)

**Situation de depart** : dataset déséquilibré (~66 "autres" vs ~6 "marketplace")

**Manipulation** : dans `prepare_dataset.py`, apres le chargement des paires,
ajoute du code pour dupliquer les paires de la catégorie sous-representee jusqu'a
atteindre un ratio plus equilibre.

```python
# Indice : tu peux filtrer par catégorie avec la fonction categorize() existante
# puis utiliser random.choices() pour sur-echantillonner
```

Relance `explore_dataset.py` apres modification et compare les distributions.

**Metriques a observer (Mac)** :

| Metrique | Avant equilibrage | Apres equilibrage |
|---|---|---|
| Taille totale dataset | ? | ? |
| Ratio category_max / category_min | ? | ? |
| % paires dupliquees | ? | ? |
| Longueur mediane Q | ? | ? |

**Autres variables a explorer** :

| Parametre | Valeurs a tester | Metrique |
|---|---|---|
| `dataset size` | 100 / 150 / 500 paires | imbalance ratio |
| `split ratio` | 80/10/10 vs 70/15/15 | val set size |
| Categorie a equilibrer | marketplace / droits | distribution |

---

### Étape 2 — Comprendre le format et preparer Colab (25 min)

**Objectif** : verifier que le dataset est pret pour le training, comprendre les hyperparametres.

**Verification format** :
```bash
# Verifie qu'une paire est bien formee
python -c "
import json
from pathlib import Path
pairs = [json.loads(l) for l in open('data/qa_dataset/concierge_qa_train.jsonl')]
print('Nb paires train:', len(pairs))
print('Cles:', list(pairs[0].keys()))
print('Exemple instruction:', pairs[0]['instruction'][:80])
print('Exemple output (60 chars):', pairs[0]['output'][:60])
"
```

**Hyperparametres Colab a connaitre** :

| Parametre | Valeurs a tester | Effet | Reference lexique |
|---|---|---|---|
| `learning_rate` | 1e-5 / 2e-4 / 1e-3 | Stabilite du training | Ligne *Learning rate* |
| `r` (LoRA rank) | 4 / 8 / 64 | Memoire vs qualite | Analogie prises electriques |
| `epochs` | 3 / 5 / 10 | Overfitting | Ligne *Epoch* |
| `batch_size` | 4 / 8 | Vitesse vs memoire | Ligne *VRAM* |

**Signal overfitting** : si apres epoch N, `val_loss` > `train_loss x 1.3` -> stop training.
C'est le signal d'alarme a surveiller dans les logs Colab.

**Garde-fou Vibe** : avant de valider, explique en 2 phrases :
"Pourquoi utilise-t-on un val set separement du train set ?"
"Que se passe-t-il si on entraine avec `lr=1e-2` ?"

---

#### 🐛 Casse-moi ça — Bug Hunt (20 min)

Trois bugs a diagnostiquer. Applique-les un par un.

```bash
# Bug 1 -- dataset 100% "autres" (zero marketplace)
git apply ateliers/atelier-04-finetuning/bugs/v1.patch
pytest ateliers/atelier-04-finetuning/bugs/test_v1.py -v
# repare, puis :
git checkout -- .

# Bug 2 -- learning rate trop grand
git apply ateliers/atelier-04-finetuning/bugs/v2.patch
pytest ateliers/atelier-04-finetuning/bugs/test_v2.py -v
# repare, puis :
git checkout -- .

# Bug 3 -- absence de validation split
git apply ateliers/atelier-04-finetuning/bugs/v3.patch
pytest ateliers/atelier-04-finetuning/bugs/test_v3.py -v
# repare, puis :
git checkout -- .
```

**Reformulation non-tech des bugs** (reference Carnet de bord) :

- **Bug 1** : "Mon dataset ne contient que des questions sur les 'autres' -- zero question sur la marketplace.
  Le modele apprend parfaitement a repondre sur 'autres' et ne sait strictement rien sur 'marketplace'
  le jour du test. C'est comme former un vendeur uniquement sur les forfaits mobile : il ne sait pas
  repondre aux questions sur les accessoires." (cf. ligne *Dataset déséquilibré*)

- **Bug 2** : "J'ai mis un learning rate trop grand (1e-2) -- le modele 'saute' trop loin a chaque
  correction et n'apprend plus rien. Ca se manifeste par une loss qui devient NaN (non-definie) des
  le 1er epoch. C'est comme tourner un bouton de volume trop fort d'un coup : ca grille le haut-parleur."
  (cf. ligne *Learning rate*)

- **Bug 3** : "J'ai omis le fichier de validation -- le modele s'entraine 10 epochs sans qu'on surveille
  s'il apprend par coeur ou s'il generalise. On decouvre l'overfitting seulement au test final, quand
  il est trop tard. C'est comme passer un examen sans jamais faire de controles blancs : la deception
  au vrai examen peut etre severe." (cf. lignes *val_loss* et *Overfitting*)

**Regle anti-cheat** : formule une hypothese sur le comportement observable AVANT de lire le patch.

Lis les explications dans `bugs/v1_explanation.md`, `bugs/v2_explanation.md`, `bugs/v3_explanation.md`.

---

### Mesure-toi (20 min)

**Sur Mac (avant Colab)** :

| Metrique | Cible | Mon resultat |
|---|---|---|
| Taille dataset apres equilibrage | >= 150 paires | ? |
| Category imbalance ratio (max/min) | < 5:1 | ? |
| Longueur mediane question | observable | ? |
| Longueur mediane reponse | observable | ? |
| % paires > 512 tokens (proxy: > 2048 chars) | < 5% | ? |

**Sur Colab (si disponible)** :

| Metrique | Cible | Mon resultat |
|---|---|---|
| Perplexite val apres epoch 1 | en baisse vs epoch 0 | ? |
| Ratio val_loss / train_loss | < 1.3 (pas d'overfitting) | ? |
| F1 test set par catégorie | observable | ? |

---

**Checkpoint final Core** -- lance `python ateliers/atelier-04-finetuning/checkpoints/check_final.py`

- Score >= 80% : pars en Bonus
- Score < 60% : pars en Sprint
- Sinon : prends une pause (5 min), refais le checkpoint le plus faible, puis Bonus

---

## 📦 Garde une trace -- section speciale HF Hub

> Ton modele fine-tune doit vivre quelque part. Sans sauvegarde -> travail perdu.

**Pourquoi pas Git classique ?**
Un modele Mistral-7B = 4 GB. Git refuse les fichiers > 100 MB.
HF Hub utilise git LFS (large file storage) -- c'est gere automatiquement.
(cf. Carnet de bord, ligne *Versionner le dataset*)

**Comment sauvegarder sur HF Hub** (a faire dans Colab) :
```python
# 1. Connexion
from huggingface_hub import login
login()  # saisir son token HF

# 2. Sauvegarder le modele fine-tune
trainer.model.push_to_hub("ton-username/homebutler-merenza-ft")

# 3. Sauvegarder aussi le dataset (pour reproductibilite)
# depuis le terminal local :
# pip install huggingface_hub
# huggingface-cli upload ton-username/homebutler-dataset data/qa_dataset/
```

**Pour le dataset uniquement (Mac, sans training)** :
```bash
pip install huggingface_hub
python -c "
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj='data/qa_dataset/concierge_qa_train.jsonl',
    path_in_repo='concierge_qa_train.jsonl',
    repo_id='ton-username/homebutler-dataset',
    repo_type='dataset',
)
"
```

---

## SPRINT (chemin alternatif, 30 min)

Si tu arrives ici avec moins de 60% au checkpoint final ou si tu es en retard :

**Option A -- Rattrapage dataset** : lance `prepare_dataset.py` et `explore_dataset.py`,
lis chaque commentaire de code, note dans ton carnet ce que fait chaque bloc.
Objective : etre capable d'expliquer le format Alpaca et le split 80/10/10 en 5 lignes.

**Option B -- Rattrapage concepts** : relis le Carnet de bord, ferme le guide, et essaie
d'ecrire de memoire les definitions de : GPU, learning_rate, epoch, val_loss, perplexite.
Compare avec le tableau. Note les 3 termes ou tu as bloque.

Dans les deux cas, remplis la section "Mesure-toi (Mac)" avec toutes les metriques reelles.

---

## BONUS (parcours alternatif, 60-70 min)

Format obligatoire : `examples-supports/reflexion-challenge.md` pour chaque defi.
Notebook a ouvrir : `notebooks/03_finetuning_lora.ipynb`

### 🏆 Défi Bonus 1 — Générer 50 paires sur la catégorie minoritaire et observer la perplexite

**POURQUOI cette question ?**
Sur-échantillonner en dupliquant cree du biais (le modele memorise les formulations exactes).
La bonne approche est de generer de NOUVELLES paires avec des formulations differentes.
Cette difference impacte la perplexite sur le val set.

**Contexte**
Le dataset actuel a ~6 paires "marketplace". Sur-échantillonner en dupliquant donne 30 paires
identiques. Generer 50 nouvelles paires avec des variantes donne 56 paires distinctes.
L'impact sur la perplexite et le F1 "marketplace" est mesurable apres training.

**Question**
Dans `prepare_dataset.py`, ajoute une fonction qui genere 50 nouvelles paires "marketplace"
avec des variantes de formulation (ex: "Ou trouver un artisan de confiance ?" vs
"Connaissez-vous un bon plombier dans le quartier ?" vs "Je cherche un boulanger local...").
Relance `explore_dataset.py`. Lance le training Colab.
Compare la perplexite val avec et sans ces 50 paires supplementaires.

**Pistes**
- Comment mesurer si les nouvelles paires sont vraiment "differentes" des existantes ?
  (indice : compare les longueurs de questions, les mots uniques)
- La perplexite sur "marketplace" baisse-t-elle apres ajout des nouvelles paires ?
- Quel est l'impact sur la perplexite globale (pas seulement "marketplace") ?

---

### 🏆 Défi Bonus 2 — Comparer FT vs baseline sur 5 questions de style

**POURQUOI cette question ?**
Le fine-tuning est couteux (GPU, temps, argent). Il faut pouvoir mesurer s'il a reellement
ameliore la qualite "style" au-dela du placebo.

**Contexte**
Le modele baseline (Mistral-7B sans FT) repond en anglais ou avec un ton neutre.
Le modele FT doit repondre en francais chaleureux avec le format Merenza.
Mais "chaleureux" est subjectif -- il faut une grille d'evaluation.

**Question**
Choisis 5 questions type guest (ex: "Comment fonctionne la machine a laver ?",
"Y a-t-il un boulanger pres de chez vous ?", "Que faire en cas de panne de chaudiere ?").
Pose-les au modele baseline ET au modele FT (via Ollama apres export GGUF).
Evalue chaque reponse sur 3 criteres (1-5 chacun) :
- Langue : francais correct (1=anglais/mixte, 5=francais impeccable)
- Chaleur : ton accueillant (1=froid/generique, 5=chaleureux/personnalise)
- Format : structure respectee (1=bloc texte, 5=sections claires + signature)

**Pistes**
- Utilise un LLM-judge : colle ce prompt dans Claude :
  "Evalue cette reponse sur 3 criteres [Langue/Chaleur/Format] de 1 a 5.
  Sois severe. Liste ce qui manque pour chaque critere."
- Est-ce que le FT ameliore les 3 criteres uniformement ou certains plus que d'autres ?
- Quel critere est le plus difficile a apprendre via FT ? Pourquoi ?

---

## Wrap-up (10 min)

**Checklist finale** :
- [ ] Criteres de succes atteints (section "La mission")
- [ ] Tous les checkpoints valides
- [ ] `bash scripts/verify_branch_scope.sh` passe
- [ ] Dataset sauvegarde sur HF Hub (ou fichiers locaux dates)

**Quiz oral 10 questions (5 min chrono)** :

1. Pourquoi utilise-t-on le FT pour le ton "Merenza" et pas le RAG ?
2. Qu'est-ce que le format Alpaca ? Cite les 3 champs.
3. Split 80/10/10 : a quoi sert chaque partie ?
4. Qu'est-ce que l'overfitting ? Quel signal dans les metriques le trahit ?
5. Qu'est-ce que le catastrophic forgetting ? Comment le mitiger ?
6. Quel est le sweet spot du learning rate pour LoRA ?
7. Qu'est-ce que la perplexite ? Plus c'est haut ou bas qui est bon ?
8. Pourquoi le dataset "66 autres / 6 marketplace" est-il problematique ?
9. Pourquoi ne pas pusher un modele de 4 GB directement sur GitHub ?
10. Dans Merenza, cite 1 use case ou le FT est meilleur que le RAG et justifie.

Si score < 6/10 : refais le Sprint avant de passer a l'atelier suivant.

**Ce que je retiens en 3 lignes** (ecris-le maintenant -- ce sera utile pour At.05) :

```
1.
2.
3.
```

---

## Pour aller plus loin (hors TP, lecture)

**Pont avec ton projet Merenza** (source : `tps.md` lignes 482-556) :

| Use case | Pourquoi FT et pas RAG |
|---|---|
| Ton "Merenza" dans toutes les reponses guest | Le ton (chaleureux, FR, emojis raisonnes) = style -> FT |
| Format strict des reponses (sections, citations) | Format reproductible -> FT |
| Reponses canoniques aux FAQ ultra-frequentes | Latence < 100ms requise -> modele FT local Ollama |
| Generation de descriptions d'annonce dans le style maison | Voice/persona -> FT |

**Cas ou le FT ne convient PAS dans Merenza** :
- Code WiFi, horaires check-in, dispos calendaires -> RAG ou DB direct (ca change)
- Prix dynamiques Stripe -> DB
- Politique de remboursement a jour -> RAG sur PDF officiel

**Approche pragmatique 2026** (source : tps.md lignes 546-556) :
1. Semaine 1 : prompt engineering Claude (system prompt "ton Merenza" + 5 few-shot) -> 80% du resultat
2. Mois suivant : logger TOUTES les interactions guest/AI -> dataset naturel
3. Quand > 2000 logs filtres : fine-tuner via Anthropic Claude FT API ou Mistral/Llama via Together AI

Ne fais pas de FT maintenant si tu n'as pas encore un signal RAG clair.

**Lectures complementaires** :
- QLoRA paper : https://arxiv.org/abs/2305.14314
- Mistral-7B : https://arxiv.org/abs/2310.06825
- RAGAS (eval LLM) : https://arxiv.org/abs/2309.15217
- HuggingFace PEFT (LoRA) : https://huggingface.co/docs/peft/index
