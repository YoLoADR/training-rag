# GUIDE FORMATEUR — Atelier 04 : Fine-tuning LoRA (3h)

> Ce guide s'adresse au formateur. Il n'est pas distribué aux élèves.
> Le guide élève est `GUIDE-ELEVE.md`. Ce fichier couvre tout ce que le formateur
> doit savoir, dire et surveiller pour animer l'atelier dans de bonnes conditions.

---

## 1. Ce que l'élève doit comprendre à la fin

L'objectif de cet atelier n'est pas de produire un modèle fine-tuné fonctionnel en séance
— cela nécessite un GPU et plusieurs heures de calcul. L'objectif est de faire comprendre
pourquoi le fine-tuning est la bonne solution pour le problème de style (et pas le RAG),
et de faire pratiquer la préparation d'un dataset de qualité.

A la fin de l'atelier, chaque élève doit être capable de :

- Expliquer en deux phrases pourquoi le fine-tuning résout le problème de ton "Merenza"
  là où le RAG ne peut pas le faire : "Le RAG apprend à savoir, le FT apprend à parler."
- Décrire le format Alpaca (instruction / input / output) et expliquer pourquoi ce format
  est le standard de l'instruction fine-tuning open-source.
- Justifier le split 80/10/10 : train pour apprendre, val pour surveiller l'overfitting
  en temps réel, test pour le score final.
- Identifier les 5 pièges classiques du fine-tuning et les relier aux trois bugs du Bug Hunt.
- Comprendre que LoRA n'entraîne pas tous les poids du modèle — il ajoute de petites
  matrices d'adaptation sur un modèle gelé, ce qui rend le fine-tuning accessible
  sur un GPU grand public (Colab T4 gratuit).

Le message central à faire passer, et à répéter plusieurs fois en séance :
**"Ce que l'on fait aujourd'hui, c'est de la qualité de données. La qualité du dataset
décide de la qualité du modèle entraîné. Un dataset biaisé donne un modèle biaisé,
quel que soit l'algorithme."**

---

## 2. Setup formateur — avant l'atelier

### 2.1 Vérifications techniques (la veille ou le matin)

```bash
# Passer sur la bonne branche
git checkout atelier/04-finetuning

# Activer l'environnement virtuel
source .venv/bin/activate

# Vérifier que le dataset de base existe
python scripts/generate_qa_dataset.py

# Vérifier que les deux scripts principaux tournent sans erreur
python ateliers/atelier-04-finetuning/explore_dataset.py
python ateliers/atelier-04-finetuning/prepare_dataset.py

# Vérifier que les patches s'appliquent proprement (test rapide)
git apply ateliers/atelier-04-finetuning/bugs/v1.patch
git checkout -- .
git apply ateliers/atelier-04-finetuning/bugs/v2.patch
git checkout -- .
git apply ateliers/atelier-04-finetuning/bugs/v3.patch
git checkout -- .

# Vérifier les checkpoints
python ateliers/atelier-04-finetuning/checkpoints/check_1.py
python ateliers/atelier-04-finetuning/checkpoints/check_final.py
```

Si `generate_qa_dataset.py` échoue avec une erreur d'API, vérifier que `ANTHROPIC_API_KEY`
est bien définie dans le `.env`. Le dataset peut aussi être généré manuellement à partir
du fichier CSV source si la clé API est indisponible.

### 2.2 Ce que les élèves doivent avoir préparé

- Branche `atelier/04-finetuning` checkoutée : `git checkout atelier/04-finetuning`
- Environnement activé : `source .venv/bin/activate`
- Compte Google Colab vérifié (accès GPU T4 gratuit disponible)
- Compte HuggingFace créé sur https://huggingface.co/join (gratuit, moins d'une minute)

Annoncer ces prérequis au moins la veille. Les élèves qui arrivent sans compte Colab
perdront 15 à 20 minutes à créer leur compte en séance.

### 2.3 Matériel formateur à préparer

- Ce guide ouvert en parallèle du guide élève
- Un terminal propre avec la branche et le venv actifs
- Les fichiers `bugs/v1_explanation.md`, `bugs/v2_explanation.md`, `bugs/v3_explanation.md`
  ouverts dans un éditeur (référence rapide pendant le Bug Hunt)
- La section "Carnet de bord — Lexique" du guide élève sous les yeux pour les analogies

---

## 3. Déroulé détaillé

### Vue d'ensemble du timing

| Bloc | Durée | Contenu |
|---|---|---|
| Introduction | 10 min | Rappel RAG vs FT, objectif de la séance |
| Etape 1 — Explorer le dataset | 20 min | `explore_dataset.py`, lecture des stats |
| Mini-lab sur-échantillonnage | 15 min | Modifier `prepare_dataset.py`, comparer distributions |
| Checkpoint 1 | 5 min | `check_1.py`, 3 termes du lexique |
| Etape 2 — Format Alpaca + Colab | 25 min | Vérification format, hyperparamètres |
| Bug Hunt | 20 min | 3 bugs v1/v2/v3 |
| Mesure-toi | 20 min | Remplir le tableau de métriques |
| Checkpoint final | 5 min | `check_final.py`, 5 QCM |
| Sprint ou Bonus | 30 à 70 min | Selon score checkpoint final |

Durée totale tronc commun : environ 1h40. Sprint : 30 min. Bonus : 60 à 70 min.

---

### 3.1 Introduction (10 min)

Commencer par la question orale suivante, avant de toucher au code :

> "Imaginons que le chatbot HomeButler réponde correctement aux questions sur la chaudière,
> mais qu'il le fasse en anglais et avec un ton froid et générique. Est-ce que le RAG
> peut corriger ça ?"

Laisser deux ou trois élèves répondre. Réponse attendue : non, le RAG ajoute du contexte
factuel mais ne change pas la façon dont le modèle génère le texte.

Enchaîner avec la règle d'or à écrire au tableau ou à projeter :
**"Le RAG apprend à savoir. Le Fine-tuning apprend à parler."**

Présenter le périmètre de l'atelier : on travaille sur la préparation du dataset.
Le training lui-même se fait sur Colab (GPU requis). Ce qui se passe en séance,
c'est la phase la plus importante : si le dataset est mauvais, l'entraînement sera mauvais
quelle que soit la puissance du GPU.

---

### 3.2 Etape 1 — Explorer le dataset (20 min)

Faire lancer les commandes dans cet ordre :

```bash
python scripts/generate_qa_dataset.py   # si le dataset est absent
python ateliers/atelier-04-finetuning/prepare_dataset.py
python ateliers/atelier-04-finetuning/explore_dataset.py
```

Ce que `explore_dataset.py` affiche et comment le commenter :

- Distribution des catégories : montrer l'écart entre "autres" (~66 paires) et "marketplace"
  (~6 paires). Poser la question : "Si le modèle voit 66 exemples 'autres' et 6 'marketplace',
  qu'est-ce qu'il va apprendre ?" Réponse : il va apprendre à tout qualifier d'autres.
- Longueur médiane des questions et des réponses : important pour comprendre que les exemples
  trop longs coûtent cher en tokens lors du training.
- Nombre de paires dupliquées : environ 45, c'est voulu pour la robustesse. Expliquer que
  les doublons ne sont pas un problème s'ils sont intentionnels, mais qu'il faut les
  contrôler.

Ce que `prepare_dataset.py` fait en détail (à expliquer à voix haute) :
- Charge les paires depuis le fichier source
- Classe chaque paire dans une catégorie via `categorize()` en cherchant des mots-clés
  (chaudière, DPE, producteurs, commandes, autres)
- Met au format Alpaca : instruction = "Réponds à la question en tant qu'assistant
  HomeButler", input = la question, output = la réponse
- Coupe en 80/10/10 avec `seed=42` pour la reproductibilité
- Sauvegarde trois fichiers JSONL dans `data/qa_dataset/`

Question à poser pendant la manipulation :

> "Pourquoi est-ce qu'on utilise `seed=42` dans le split ? Qu'est-ce qui changerait
> sans ce paramètre ?"

Réponse attendue : sans seed fixe, les fichiers train/val/test seraient différents à chaque
exécution. On ne pourrait pas comparer des expériences entre elles.

---

### 3.3 Mini-lab sur-échantillonnage (15 min)

Les élèves modifient `prepare_dataset.py` pour dupliquer les paires de la catégorie
"marketplace" jusqu'à un ratio raisonnable (< 5:1 avec la catégorie dominante).

L'indice fourni dans le guide élève :

```python
# Filtrer par catégorie avec categorize() existante
# puis utiliser random.choices() pour sur-échantillonner
```

Ne pas donner la solution immédiatement. Laisser 10 minutes d'exploration.
Si un élève est bloqué, lui poser la question : "La fonction `categorize()` existe déjà
dans le fichier. Comment tu l'utiliserais pour filtrer uniquement les paires 'marketplace' ?"

Objectif pédagogique : comprendre que la solution au déséquilibre se traite avant le
training, pas pendant. Et que dupliquer des exemples, c'est bien, mais que générer
de nouvelles variantes, c'est mieux (renvoyé au Bonus 1).

---

### 3.4 Checkpoint 1 (5 min)

```bash
python ateliers/atelier-04-finetuning/checkpoints/check_1.py
```

Ce checkpoint tire 3 termes au hasard parmi 7 du lexique. L'élève doit expliquer
chaque terme avec ses propres mots, puis se noter lui-même (A = à l'aise / B = à renforcer).

Score minimum pour passer : 2/3.

Comment animer : le checkpoint est en auto-évaluation. Expliquer aux élèves qu'être honnête
ici leur rend service — un terme mal compris maintenant entraînera des erreurs de
configuration plus tard (notamment learning rate et split validation).

Si un élève bloque sur "GPU" ou "learning rate", renvoyer directement au Carnet de bord
dans le guide élève. Ne pas expliquer à sa place.

---

### 3.5 Etape 2 — Format Alpaca et préparation Colab (25 min)

Faire exécuter la vérification de format :

```bash
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

Expliquer le format Alpaca simplement :

Le format Alpaca est la "recette" que le trainer attend. Trois champs obligatoires :
- `instruction` : ce qu'on demande au modèle de faire. Ici toujours "Réponds à la question
  en tant qu'assistant HomeButler"
- `input` : la question concrète posée par l'utilisateur. Exemple : "Quelle est la marque
  de ma chaudière ?"
- `output` : la réponse idéale dans le ton Merenza. Exemple : "Votre chaudière est une
  Viessmann Vitodens 100-W, installée en 2018. N'hésitez pas à consulter la notice..."

Pourquoi ce format ? C'est le standard adopté par la communauté open-source pour
l'instruction fine-tuning. Le notebook Colab l'attend directement. Changer de format
nécessiterait de modifier le code du trainer.

Présenter ensuite le tableau des hyperparamètres (à projeter ou dicter) :

| Paramètre | Valeurs à tester | Effet |
|---|---|---|
| `learning_rate` | 1e-5 / 2e-4 / 1e-3 | Stabilité — 1e-3 provoque NaN |
| `r` (rang LoRA) | 4 / 8 / 64 | Mémoire GPU vs qualité |
| `epochs` | 3 / 5 / 10 | Risque d'overfitting croissant |
| `batch_size` | 4 / 8 | Vitesse vs mémoire GPU |

Insister sur le signal d'arrêt d'urgence en Colab : si après une epoch,
`val_loss > train_loss × 1.3`, le modèle overfit. Il faut arrêter et diagnostiquer
avant de continuer.

---

### 3.6 Bug Hunt (20 min)

C'est la partie la plus dense en apprentissage. Bien insister sur la règle :

> **Formuler une hypothèse AVANT d'appliquer le patch et AVANT de lire l'explication.**

La discipline à imposer : "Qu'est-ce que tu t'attends à voir comme comportement
si ce bug est présent ?" L'élève écrit sa réponse, puis applique le patch pour vérifier.

Ordre des bugs, commandes et comportements attendus :

**Bug v1 — Dataset 100% "autres"**

```bash
git apply ateliers/atelier-04-finetuning/bugs/v1.patch
pytest ateliers/atelier-04-finetuning/bugs/test_v1.py -v
# Observer la distribution : toutes les paires tombent dans "autres"
git checkout -- .
```

Ce qui se passe : les quatre branches `if` de `categorize()` sont toutes cassées. La
fonction retourne "autres" pour n'importe quel input. Résultat : le dataset est 100%
biaisé avant même de commencer le training.

Analogie à utiliser : "C'est comme former un vendeur en lui faisant lire uniquement des
guides de cuisine. Le jour où un client pose une question sur l'électroménager, il ne
sait rien répondre."

Fix à guider : restaurer la logique de détection de mots-clés pour chacune des quatre
catégories (chaudière/DPE/producteurs/commandes). Les mots-clés sont documentés dans
`bugs/v1_explanation.md`.

**Bug v2 — Learning rate trop grand**

```bash
git apply ateliers/atelier-04-finetuning/bugs/v2.patch
pytest ateliers/atelier-04-finetuning/bugs/test_v2.py -v
git checkout -- .
```

Ce qui se passe : `LEARNING_RATE = 1e-2` est ajouté en haut de `prepare_dataset.py`.
Valeur 50 à 500 fois trop grande pour LoRA. Lors du training sur Colab, la loss devient
NaN dès le premier epoch et le modèle est définitivement inutilisable.

Analogie à utiliser : "Tourner le bouton de volume à fond d'un coup — ça grille le
haut-parleur. Une fois que la loss est NaN, on ne répare pas en continuant : il faut
arrêter, corriger, et recommencer."

Fix : supprimer la ligne `LEARNING_RATE = 1e-2`. La valeur correcte pour LoRA est
comprise entre 1e-4 et 3e-4. Suggérer 2e-4 comme point de départ.

**Bug v3 — Absence de validation split**

```bash
git apply ateliers/atelier-04-finetuning/bugs/v3.patch
pytest ateliers/atelier-04-finetuning/bugs/test_v3.py -v
git checkout -- .
```

Ce qui se passe : `n_train = n` et `n_val = 0`. Toutes les paires vont en train,
les fichiers val et test sont vides. Sans val set, on ne peut pas détecter l'overfitting
pendant le training.

Analogie à utiliser : "Préparer un examen sans jamais faire de contrôles blancs. On
découvre qu'on a appris par coeur seulement le jour du vrai examen — trop tard."

Fix : restaurer `n_train = int(n * 0.8)` et `n_val = int(n * 0.1)`.

---

### 3.7 Mesure-toi (20 min)

Les élèves remplissent le tableau de métriques locales (Mac, sans GPU) :

| Métrique | Cible | Résultat élève |
|---|---|---|
| Taille dataset après équilibrage | >= 150 paires | ? |
| Ratio catégorie max / catégorie min | < 5:1 | ? |
| Longueur médiane question | observable | ? |
| % paires > 2048 caractères | < 5% | ? |

Ce moment sert à ancrer l'idée que la qualité du dataset se mesure avant le training.
Les élèves qui ne remplissent pas ce tableau n'ont pas de référence pour comparer
leurs résultats Colab.

---

### 3.8 Checkpoint final (5 min)

```bash
python ateliers/atelier-04-finetuning/checkpoints/check_final.py
```

5 QCM sur l'ensemble de l'atelier. Score et orientation :
- >= 4/5 : Bonus (Colab + génération de nouvelles paires + comparaison FT vs baseline)
- < 3/5 : Sprint (relecture ciblée + questions ouvertes)
- 3/5 : choix libre élève

---

## 4. Bug Hunt — ce qui se passe concrètement

Cette section détaille la mécanique interne de chaque bug pour que le formateur puisse
répondre aux questions sans ouvrir les fichiers source.

### Bug v1 — Catégorisation cassée

Le code normal de `categorize()` teste si la question contient des mots-clés métier.
Le patch sabote les quatre branches conditionnelles pour qu'elles ne se déclenchent
jamais. Chaque paire tombe donc dans le `else` final qui retourne "autres".

Conséquence observable immédiate : après `prepare_dataset.py`, le terminal affiche une
distribution avec "autres" = 100% et les quatre autres catégories = 0. Si un élève
lance ensuite un training Colab avec ce dataset, le modèle sera incapable de répondre
à n'importe quelle question hors de la catégorie "autres".

Le test `test_v1.py` vérifie que plusieurs questions représentatives de chaque catégorie
sont bien classées dans la bonne catégorie. Avec le bug actif, tous ces tests échouent.

Comment débloquer un élève : lui demander d'afficher la distribution après avoir
appliqué le patch (`python prepare_dataset.py`). Quand il voit "autres : 150 / reste : 0",
lui poser : "Si tu devais parier, qu'est-ce qui classe tout en 'autres' dans le code ?"
Cela l'oriente vers la fonction `categorize()`.

### Bug v2 — Learning rate explosif

Le patch ajoute une seule ligne en haut du fichier :
```python
LEARNING_RATE = 1e-2
```

Cette valeur est importée ou utilisée dans la configuration du training Colab.
0.01 = 50 à 500 fois trop grand pour LoRA sur un modèle 7B. Le gradient explose dès
les premiers batches et la loss devient NaN.

Point pédagogique important : ce bug ne provoque aucune erreur Python en local.
Le fichier de préparation du dataset tourne sans problème. L'explosion se produit
uniquement lors du training sur Colab. C'est exactement pourquoi il faut vérifier
les hyperparamètres avant de lancer l'entraînement, pas après avoir perdu deux heures
de quota GPU.

Le test `test_v2.py` vérifie que `LEARNING_RATE` n'est pas défini dans le fichier
(ou qu'il est dans la plage 1e-5 à 5e-4). Avec le bug actif, le test échoue.

### Bug v3 — Val set vide

Le patch modifie deux lignes dans `split_train_val_test()` :
```python
n_train = n      # au lieu de int(n * 0.8)
n_val   = 0      # au lieu de int(n * 0.1)
```

Résultat : `concierge_qa_val.jsonl` et `concierge_qa_test.jsonl` sont vides.
Le trainer Colab ne peut pas calculer `val_loss`. On ne peut donc pas détecter
si le modèle overfit, ni savoir quand arrêter le training.

Ce bug est particulièrement dangereux car le training semble se passer normalement
(train_loss descend bien) jusqu'à ce qu'on évalue le modèle sur de vraies questions
et qu'on réalise qu'il a mémorisé les exemples sans generaliser.

Le test `test_v3.py` vérifie que les fichiers val et test contiennent au moins
un certain nombre de paires (environ 15 chacun pour un dataset de 150 paires).
Avec le bug actif, les deux vérifications échouent.

---

## 5. Checkpoints — comment les animer

### Checkpoint 1 — Lexique (après Etape 1)

Le script `check_1.py` tire 3 termes au hasard parmi les 7 du lexique :
GPU, Learning rate, Epoch, Perplexité, Dataset déséquilibré, Catastrophic forgetting,
Quantization 4-bit.

Format : auto-évaluation. L'élève répond à voix haute ou par écrit, puis compare avec
la définition affichée, puis se note A (à l'aise) ou B (à renforcer).

Conseils d'animation :

Annoncer à l'avance que ce checkpoint arrive. Les élèves qui ont ouvert le Carnet de bord
dès le début de l'atelier le passent sans problème. Ceux qui ont sauté cette section
seront en difficulté, ce qui est un signal utile pour le formateur.

Ne pas accélérer ce moment. Si un élève hésite sur "learning rate", c'est exactement
le terme qui détermine si le Bug v2 lui semblera évident ou mystérieux. Prendre le temps.

Résultat attendu : 2/3 minimum pour passer à l'Etape 2. Si un élève est à 1/3,
le renvoyer au Carnet de bord pour les deux termes manquants, puis relancer le checkpoint.
Ne pas lui donner les réponses directement.

### Checkpoint final — QCM (après Mesure-toi)

Le script `check_final.py` pose 5 questions à choix multiples couvrant :
- Pourquoi LoRA (pas full FT)
- Lecture de métriques d'overfitting (train_loss vs val_loss)
- RAG vs FT pour le problème de style
- Stratégie face à un dataset déséquilibré
- Catastrophic forgetting et rôle de LoRA

Format : QCM avec correction immédiate et explication de chaque bonne réponse.

Résultats et orientation :

| Score | Message à donner |
|---|---|
| 5/5 | "Excellent. Part sur le Bonus Colab, observe la perplexité sur au moins une epoch." |
| 4/5 | "Bon travail. Bonus recommandé — relis l'explication de la question ratée avant de commencer." |
| 3/5 | "Correct. Tu choisis : consolider avec le Sprint ou tenter le Bonus en sachant que les deux questions ratées réapparaîtront." |
| 2/5 ou moins | "Sprint obligatoire. Les concepts RAG vs FT et overfitting sont des prérequis pour At.05." |

Ne pas laisser un élève à 2/5 partir directement en Bonus — les concepts manquants
reviennent dans chaque atelier suivant.

---

## 6. Questions fréquentes

**"Pourquoi on ne fait pas le training maintenant ?"**

Réponse directe et sans détour : entraîner Mistral-7B en QLoRA requiert un GPU avec
au moins 12 Go de VRAM. Un Mac sans GPU (même récent) ne peut pas le faire en temps
raisonnable — cela prendrait des heures pour un résultat médiocre. Colab T4 gratuit
fournit un GPU adapté. Le notebook est prêt dans `notebooks/03_finetuning_lora.ipynb`.
Ce qui compte aujourd'hui, c'est que le dataset soit bon. Garbage in, garbage out :
un training parfait sur un mauvais dataset donnera un mauvais modèle.

**"1e-2 c'est quoi comme nombre ?"**

1e-2 = 0.01. C'est la notation scientifique : 10 exposant -2. Pour LoRA, le sweet spot
est entre 1e-4 (0.0001) et 3e-4 (0.0003). 1e-2 est donc de 30 à 100 fois trop grand.
Analogie : c'est comme régler le chauffage à 100 degrés pour une pièce cible à 20 degrés.
Ça explose avant d'être utile.

**"Pourquoi le format Alpaca et pas autre chose ?"**

C'est le standard adopté par la majorité des projets open-source d'instruction
fine-tuning depuis 2023 (Stanford Alpaca, LLaMA-Instruct, Mistral). Le notebook Colab
fourni l'attend directement. Il existe d'autres formats (ShareGPT, ChatML) mais ils
nécessiteraient de modifier le code du trainer. En atelier, on fixe le format pour
se concentrer sur la qualité des données, pas sur le plomberie du code.

**"Est-ce que le fine-tuning va remplacer le RAG dans At.05 et At.06 ?"**

Non. RAG et fine-tuning sont complémentaires. RAG pour les faits qui changent (prix,
disponibilités, DPE), FT pour le style fixe (ton Merenza, format de réponse). At.06
fait la comparaison expérimentale. Pour l'instant : FT = style, RAG = faits.

**"Catastrophic forgetting : est-ce que ça arrive vraiment ?"**

Oui, c'est documenté et reproductible. Si on fine-tune sur 100% de données HomeButler
sans données générales, le modèle peut perdre sa capacité à répondre en anglais ou à
faire des tâches génériques comme de la synthèse. LoRA atténue fortement ce problème
(les poids originaux sont gelés), mais la bonne pratique reste d'inclure 20 à 30%
de données générales dans le mix.

**"On peut pas juste augmenter le dataset avec un LLM ?"**

Si, c'est exactement ce que fait le Bonus 1. Mais attention : les données générées
artificiellement peuvent introduire des biais (le LLM reproductible à certaines
formulations). Il faut les contrôler (variété des questions, longueur, vocabulaire).
C'est l'objet du Bonus 1 : générer 50 nouvelles paires marketplace et mesurer l'impact
sur la perplexité.

---

## 7. Signaux d'alerte (élève bloqué)

### Signal 1 — L'élève applique le patch sans formuler d'hypothèse

C'est le signe qu'il cherche la réponse dans le code plutôt que dans le raisonnement.
Intervention : "Attends. Avant de lire le patch, dis-moi : d'après toi, quel est le
symptôme observable de ce bug ?" Si l'élève ne sait pas répondre, c'est qu'il n'a
pas compris l'étape précédente. Revenir sur le concept (catégorisation, learning rate,
ou split) avant de lancer le Bug Hunt.

### Signal 2 — L'élève est bloqué sur la commande `git apply`

Vérifier que la branche est propre (pas de modifications non commitées) :
```bash
git status
git checkout -- .   # si nécessaire
git apply ateliers/atelier-04-finetuning/bugs/vX.patch
```

Si le patch échoue avec "patch does not apply", c'est souvent parce qu'un bug
précédent n'a pas été proprement annulé avec `git checkout -- .`.

### Signal 3 — pytest retourne des erreurs d'import

Vérifier que le venv est actif : `which python` doit pointer vers `.venv/bin/python`.
Si ce n'est pas le cas : `source .venv/bin/activate`.

### Signal 4 — L'élève n'a pas de résultats dans le tableau Mesure-toi

C'est un signe qu'il a suivi les étapes mécaniquement sans observer les sorties.
Lui demander de relancer `explore_dataset.py` et de lire les chiffres à voix haute.
Le tableau de métriques doit être rempli avec de vrais chiffres, pas des points
d'interrogation.

### Signal 5 — Score checkpoint final < 3/5 sur RAG vs FT

C'est le concept le plus important de l'atelier et le prérequis direct pour At.05.
Prendre 5 minutes en tête-à-tête : "Donne-moi un exemple concret où le RAG est la
bonne solution. Donne-moi un exemple où le FT est meilleur." Si l'élève ne peut pas
répondre, lui faire relire la section "RAG vs Fine-tuning — la confusion numéro 1"
dans le guide élève, puis le faire expliquer sans relire.

### Signal 6 — L'élève ne comprend pas pourquoi val_loss > train_loss signifie overfitting

Utiliser cette analogie : "Tu t'entraînes sur les exercices du cours (train_loss baisse).
Mais au contrôle blanc (val_loss), tu te plantes — tu avais mémorisé les solutions
sans comprendre. C'est exactement l'overfitting." Si le concept ne passe pas, renvoyer
vers le Sprint avant le Bonus.

---

## 8. Transition vers l'atelier 05

A la fin de l'atelier 04, s'assurer que chaque élève peut répondre aux trois questions
suivantes sans hésitation. Ce sont les prérequis d'At.05 (API FastAPI + déploiement) :

1. "Quelle est la différence entre RAG et fine-tuning pour le cas HomeButler ?"
   Réponse minimale : RAG = faits dynamiques, FT = style/ton fixe.

2. "Pourquoi le val set est-il obligatoire ?"
   Réponse minimale : pour détecter l'overfitting avant la fin du training.

3. "Qu'est-ce que le format Alpaca ?"
   Réponse minimale : trois champs JSON — instruction, input, output — qui structurent
   les données d'entraînement pour l'instruction fine-tuning.

Annoncer aux élèves ce qui les attend en At.05 :
"On a préparé le dataset et compris le training. En At.05, on va exposer le modèle
via une API FastAPI et une interface Streamlit. Le modèle fine-tuné (ou le modèle
baseline si Colab n'a pas pu tourner) sera derrière l'API."

Rappeler aussi que le dataset HuggingFace Hub doit être sauvegardé avant de fermer
le laptop. Un dataset non sauvegardé = perte du travail de préparation.

---

*Ce guide couvre la branche `atelier/04-finetuning`. Dernière mise à jour : 2026-05-25.*
