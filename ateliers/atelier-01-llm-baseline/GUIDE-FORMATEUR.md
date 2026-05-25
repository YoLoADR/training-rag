# GUIDE FORMATEUR — Atelier 01 : LLM Baseline (3h)

> Ce guide est destiné au formateur. Il contient tout ce dont vous avez besoin pour animer
> l'atelier du début à la fin, même si vous n'êtes pas expert Python. Lisez-le en entier
> la veille de la session.

---

## 1. Ce que l'élève doit comprendre à la fin

À l'issue de cet atelier, chaque participant doit être capable d'expliquer oralement, sans
relire ses notes, les quatre points suivants.

**Un LLM ne sait pas ce qu'il ne sait pas.** Sur des questions portant sur des données
privées (marque de la chaudière, numéro du bail, classe DPE du logement), il produit une
réponse plausible mais inventée. Ce comportement porte un nom : l'hallucination. Ce n'est
pas un bug, c'est le fonctionnement normal d'un modèle de langage qui prédit le token
suivant sans aucun mécanisme de vérification factuelle.

**La temperature contrôle le degré d'aléatoire.** À `temperature=0`, le modèle choisit
toujours le token le plus probable : deux appels identiques donnent des réponses identiques
(déterminisme). À `temperature=0.9`, le modèle puise dans des tokens moins probables :
les réponses varient d'un appel à l'autre.

**Le knowledge cutoff explique l'ignorance des données récentes et privées.** Le modèle
a été entraîné sur des données collectées jusqu'à une certaine date. Tout ce qui existe
après, ou tout ce qui n'a jamais été publié (le logement de l'utilisateur), est
inconnu du modèle.

**Le system prompt est la fiche de poste du modèle.** Sans system prompt, le modèle se
comporte comme un assistant généraliste non contrôlé. Avec un system prompt, on lui donne
son rôle, ses contraintes de ton, et ses limites explicites avant même que l'utilisateur
pose une question.

Ces quatre points serviront de fondations pour tout le reste de la formation. Si un élève
sort de l'atelier sans maîtriser l'un d'eux, il aura du mal à comprendre pourquoi le RAG
est nécessaire dès l'atelier 02.

---

## 2. Setup formateur — avant l'atelier

### 2.1 La veille : vérifier son propre environnement

Faites ces vérifications sur votre machine avant d'entrer en salle. Si quelque chose échoue,
vous aurez le temps de corriger.

```bash
# Se placer à la racine du projet
cd /chemin/vers/pre-training-rag

# Passer sur la branche de l'atelier
git checkout atelier/01-llm-baseline

# Activer le venv
source .venv/bin/activate

# Vérifier que le package HomeButler est installé
python -c "import homebutler; print('Package OK')"

# Vérifier que .env est configuré avec une clé Anthropic valide
grep ANTHROPIC_API_KEY .env
# → doit afficher : ANTHROPIC_API_KEY=sk-ant-...  (pas de "..." littéral)

# Lancer le script check complet
bash scripts/check_atelier_ready.sh 01
# → doit afficher : Atelier 01 : PRÊT

# Lancer la solution pour vérifier que l'API répond
python ateliers/atelier-01-llm-baseline/solution.py
# → vous devez voir 5 réponses inventées sur les questions du logement
```

Si `check_atelier_ready.sh` retourne une erreur sur les PDFs, lancez le générateur :

```bash
python scripts/generate_documents.py
```

### 2.2 Ce matin : vérifier que les élèves ont leur .env

Avant de commencer, demandez à chaque élève de lancer :

```bash
bash scripts/check_atelier_ready.sh 01
```

Tout élève qui voit une croix sur `ANTHROPIC_API_KEY` doit régler son `.env` avant que
le reste du groupe avance. Prenez 5 minutes pour ça, c'est du temps gagné plus tard.

Structure minimale du `.env` pour cet atelier :

```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-6
```

Si un élève n'a pas de clé Anthropic, deux solutions : partager votre clé de démo le
temps de l'atelier, ou basculer sur Ollama si le modèle est déjà installé sur sa machine.
Pour Ollama, il faut modifier `.env` :

```
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=homebutler
```

Et vérifier qu'Ollama tourne : `ollama list` doit afficher le modèle `homebutler`.

### 2.3 Ce que vous devez avoir ouvert sur votre écran

Pour projeter et guider en temps réel, ayez ces fichiers ouverts dans votre éditeur :

- `ateliers/atelier-01-llm-baseline/exercice.py` — le fichier que les élèves complètent
- `ateliers/atelier-01-llm-baseline/solution.py` — votre référence (ne pas projeter)
- `homebutler/llm/provider.py` — la fonction `get_llm()` que les élèves vont importer
- `homebutler/llm/prompts.py` — le system prompt HomeButler

---

## 3. Déroulé détaillé

### Pré-vol (20 min) — Avant de coder, vérifier les bases

Ce n'est pas du temps perdu. Chaque élève qui passe ce cap sans problème ne vous dérangera
pas pendant les exercices.

Demandez à chaque élève de lancer `bash scripts/check_atelier_ready.sh 01` et d'attendre
le "Atelier 01 : PRÊT". Pendant ce temps, parcourez la salle.

Pendant le pré-vol, posez cette question à voix haute au groupe : "Avant de toucher au
code, quelqu'un peut me dire : pourquoi est-ce qu'un LLM n'est pas capable de répondre
à 'Quelle est la marque de ma chaudière ?' ?" Ne donnez pas la réponse. Laissez les élèves
proposer. L'objectif est d'ancrer la problématique avant l'expérience.

### Tronc commun (1h40)

Le tronc commun se découpe en deux parties : les étapes de code, et le Bug Hunt intégré.

#### Étape 1 — Instancier le LLM et poser les 5 questions privées (25 min)

Les élèves ouvrent `exercice.py`. Le fichier contient 5 TODO commentés. Ils doivent
commencer par le TODO 1 : décommenter l'import de `get_llm` et instancier le LLM.

La commande pour lancer le script est :

```bash
python ateliers/atelier-01-llm-baseline/exercice.py
```

Au premier lancement, le script lève `NotImplementedError` car les TODO ne sont pas
complétés. C'est intentionnel. Demandez aux élèves de lire le message d'erreur avant
de coder : "que vous dit Python ?"

Une fois le TODO 1 complété (l'import et `llm = get_llm(temperature=0.1)`), les élèves
décommentent le TODO 2 pour poser les 5 questions. Le script affiche les réponses.

**Ce que vous observez à l'écran** : le modèle répond avec confiance à chaque question.
Il propose une marque de chaudière (souvent "Viessmann" ou "De Dietrich"), une classe DPE
(souvent "C"), un numéro de téléphone plausible. Tout est faux. Personne dans la salle
ne sait quelle chaudière est dans le logement fictif HomeButler — et le modèle non plus.
C'est le moment de marquer une pause et de dire : "Ce que vous voyez là, c'est une
hallucination. Le modèle prédit des tokens statistiquement plausibles. Il ne ment pas
intentionnellement — il ne sait tout simplement pas."

**Checkpoint 1** — À la fin de l'étape 1, faites lancer le checkpoint interactif :

```bash
python ateliers/atelier-01-llm-baseline/checkpoints/check_1.py
```

Ce checkpoint pose 3 questions à l'élève sur hallucination, temperature=0 et token.
Le seuil de passage est 2/3. Si un élève est en dessous, il doit relire le Carnet de bord
dans son GUIDE-ELEVE.md avant de continuer. Ne le laissez pas avancer mécaniquement
sans comprendre.

#### Mini-lab temperature (15 min)

Demandez aux élèves de compléter le TODO 3 : créer un second LLM avec `temperature=0.9`
et poser la même question deux fois de suite. L'objectif est d'observer la variabilité.

Posez la question au groupe : "Combien d'entre vous ont eu deux réponses différentes avec
T=0.9 ?" En général, tout le monde lève la main. "Et avec T=0 ?" En général, personne.

C'est le moment d'expliquer l'analogie du curseur : température 0 = robot qui répond
toujours pareil, température 0.9 = artiste qui improvise. Pour un assistant maison
qui doit donner des faits fiables, lequel veut-on ?

#### Étape 2 — Hallucination rate (30 min)

Les élèves ajoutent les 5 questions générales et calculent le hallucination rate. Sur les
questions générales (comment purger un radiateur, qu'est-ce que le DPE), le modèle répond
souvent correctement. Sur les questions privées, il hallucine quasi systématiquement.

Le hallucination rate se calcule ainsi : nombre de réponses inventées sur les 5 questions
privées, divisé par 5. Si le modèle répond à toutes les questions privées sans dire
"je ne sais pas", le taux est de 100 %. C'est le résultat attendu et c'est pédagogiquement
souhaitable : il faut voir l'échec pour comprendre pourquoi le RAG est nécessaire.

Dites aux élèves : "Ce taux, vous l'affichez à la fin de votre script. À l'atelier 02,
vous viserez 0 % sur ces mêmes questions en injectant les vrais documents."

#### Bug Hunt (20 min)

Le Bug Hunt est intégré dans le tronc commun. Trois bugs, un par un, appliqués via des
patches git. Chaque bug crée un comportement observable différent.

Avant d'appliquer chaque patch, demandez aux élèves de formuler une hypothèse : "D'après
vous, que va changer ce bug ?" Puis ils appliquent, constatent, réparent, valident.

**Bug v1 — Temperature trop haute dans run_1**

Ce bug remplace `temperature=0.1` par `temperature=0.9` dans le premier bloc d'appels.
Résultat : la baseline censée être stable devient non déterministe. Les élèves qui relancent
deux fois le script obtiennent des réponses différentes sur les mêmes questions.

```bash
git apply ateliers/atelier-01-llm-baseline/bugs/v1.patch
pytest ateliers/atelier-01-llm-baseline/bugs/test_v1.py -v
```

Le test échoue — c'est normal, le bug est actif. Demandez aux élèves de trouver la ligne
à corriger sans regarder le patch. La réparation est simple : changer `0.9` en `0.1`.
Une fois réparé :

```bash
pytest ateliers/atelier-01-llm-baseline/bugs/test_v1.py -v
# → doit PASSER
```

Faites ensuite lire `bugs/v1_explanation.md` : il contient 3 questions vrai/faux que les
élèves répondent en silence (2 minutes). C'est un moment de consolidation rapide.

**Bug v2 — max_tokens=50 dans les deux appels à get_llm()**

Ce bug fixe `max_tokens=50` dans la configuration du LLM. Cinquante tokens, c'est
environ 200 caractères — la réponse s'arrête en plein milieu d'une phrase. Il n'y a
aucun message d'erreur : la réponse est simplement tronquée, ce qui peut passer inaperçu
si on ne lit pas attentivement.

```bash
git apply ateliers/atelier-01-llm-baseline/bugs/v2.patch
pytest ateliers/atelier-01-llm-baseline/bugs/test_v2.py -v
```

La réparation : supprimer le paramètre `max_tokens=50` ou le remplacer par `max_tokens=1024`.
Après réparation, le test passe et les réponses sont complètes.

Ce bug est l'occasion d'expliquer ce qu'est un token concrètement : "Le mot 'chaudière'
fait environ 3 tokens. 50 tokens, c'est une réponse de 15 mots. Voilà pourquoi on fixe
généralement `max_tokens=1024` pour un assistant conversationnel."

**Bug v3 — HumanMessage à la place de SystemMessage pour le system prompt**

Ce bug remplace `SystemMessage(content=SYSTEM_PROMPT)` par
`HumanMessage(content=SYSTEM_PROMPT)`. Le modèle reçoit donc le texte de la fiche de
poste comme si c'était une question utilisateur. Il répond à la fiche de poste au lieu
de l'utiliser comme cadre de comportement, ce qui donne des réponses hors sujet.

```bash
git apply ateliers/atelier-01-llm-baseline/bugs/v3.patch
pytest ateliers/atelier-01-llm-baseline/bugs/test_v3.py -v
```

La réparation : remettre `SystemMessage` pour le system prompt. L'ordre correct dans
la liste envoyée au LLM est toujours `[SystemMessage(...), HumanMessage(...)]`.

Après ce bug, posez la question : "Pourquoi l'ordre des messages compte-t-il ?" La réponse
intuitive est bonne : le modèle lit la conversation dans l'ordre. Si la fiche de poste
arrive en dernier, il a déjà commencé à répondre sans elle.

#### Mesure finale et Checkpoint final (15 min)

Les élèves remplissent le tableau de métriques (hallucination rate, determinism rate,
latence) et lancent le checkpoint final :

```bash
python ateliers/atelier-01-llm-baseline/checkpoints/check_final.py
```

Ce checkpoint pose 5 questions. Le résultat oriente l'élève vers la suite :
- Score 4/5 ou 5/5 : direction Bonus
- Score 3/4 sur 5 : 5 minutes de relecture du concept raté, puis Bonus
- Score inférieur à 3/5 : direction Sprint

### Sprint (30 min) — Pour les élèves en retard ou en difficulté

Le Sprint est un chemin alternatif qui consolide les deux concepts les plus importants :
temperature et system prompt. Ce n'est pas une punition. Présentez-le ainsi : "Le Sprint,
c'est 30 minutes pour être solide sur les fondations avant d'aller plus loin."

Les élèves en Sprint ouvrent `homebutler/llm/provider.py` pour lire comment `temperature`
est passée à `ChatAnthropic`, puis font un exercice de comparaison 5x T=0 vs 5x T=0.9.
Ensuite ils ajoutent manuellement un system prompt dans leur script et observent si le
ton du modèle change sur les questions privées.

### Bonus (60-70 min) — Pour les élèves en avance

Deux défis disponibles :

**Défi Bonus 1 — Sonnet vs Haiku.** L'élève compare les deux modèles Anthropic sur les
5 questions privées et mesure latence, tokens consommés, et qualité perçue des réponses.
Pour changer de modèle, il modifie `ANTHROPIC_MODEL` dans `.env` ou instancie directement
`ChatAnthropic(model="claude-haiku-4-5", ...)`. L'objectif est de comprendre l'arbitrage
coût/latence/qualité.

**Défi Bonus 2 — Few-shot prompting.** L'élève ajoute 2-3 exemples de question/réponse
dans le system prompt pour apprendre au modèle à répondre "Je n'ai pas accès à ces
informations" plutôt que d'inventer. Puis il recalcule le hallucination rate. Ce défi
prépare la réflexion de l'atelier 02 : le few-shot est-il suffisant, ou faut-il vraiment
injecter les documents ?

---

## 4. Bug Hunt — ce qui se passe concrètement

Cette section vous donne le détail technique de chaque bug pour que vous puissiez répondre
aux questions des élèves sans ouvrir les patches vous-même.

### Bug v1 — Temperature non déterministe

**Ligne modifiée dans exercice.py (ou solution.py)** : l'appel `get_llm(temperature=0.1)`
dans `run_1_baseline_temperature_basse()` devient `get_llm(temperature=0.9)`.

**Effet observable** : si l'élève lance le script deux fois de suite, les réponses aux
5 questions privées changent entre les deux runs. Le script est censé servir de baseline
stable. Avec T=0.9, il est imprévisible.

**Pourquoi c'est un vrai problème en production** : une baseline non reproductible rend
les comparaisons impossibles. Si on ne peut pas répéter le même résultat, on ne peut pas
mesurer si une amélioration (ajout de RAG, changement de prompt) a vraiment un effet.

**Réparation** : une seule ligne, remplacer `0.9` par `0.1`.

**Signal d'alerte** : si un élève dit "mon test passe déjà sans rien changer", c'est qu'il
a peut-être appliqué le patch sur du code déjà corrigé. Demandez-lui de vérifier avec
`git diff` que le patch est bien actif.

### Bug v2 — Réponse tronquée

**Ligne modifiée** : `max_tokens=50` ajouté dans les deux appels à `get_llm()`.

**Effet observable** : les réponses s'arrêtent en plein milieu d'une phrase, souvent après
le deuxième ou troisième mot d'une explication. Il n'y a aucun message d'erreur ni
indication que la réponse est incomplète. L'élève doit reconnaître visuellement la
troncature.

**Un token en pratique** : 1 token vaut environ 4 caractères en anglais et 3 à 4 caractères
en français. Le mot "chaudière" vaut environ 3 tokens. 50 tokens, c'est à peu près
35 à 40 mots — insuffisant pour une réponse explicative.

**Point important à souligner** : `max_tokens` est un plafond, pas une cible. Si la
réponse fait 80 tokens et que `max_tokens` vaut 1024, on paie et on attend 80 tokens, pas
1024. Il n'y a donc pas d'inconvénient à mettre une valeur généreuse.

**Réparation** : supprimer `max_tokens=50` ou le remplacer par `max_tokens=1024`.

### Bug v3 — Absence de SystemMessage

**Ligne modifiée** : `SystemMessage(content=SYSTEM_PROMPT)` remplacé par
`HumanMessage(content=SYSTEM_PROMPT)`.

**Effet observable** : le modèle reçoit le texte de la fiche de poste comme s'il s'agissait
d'une question de l'utilisateur. Il va souvent répondre à la fiche de poste (expliquer
ce qu'est un assistant maison, acquiescer aux instructions) plutôt que d'exécuter les
instructions. Sur les 5 questions privées, les réponses deviennent génériques ou
hors sujet.

**Pourquoi la distinction SystemMessage / HumanMessage est importante** : les API de LLM
distinguent trois rôles dans une conversation : `system` (instructions générales invisibles
de l'utilisateur), `user` (ce que dit l'utilisateur), et `assistant` (ce que répond le
modèle). Si on met les instructions dans le message `user`, le modèle les traite comme
une requête normale et non comme une contrainte de comportement.

**Réparation** : remettre `SystemMessage` pour le system prompt. Rappeler l'ordre correct :
`[SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=question)]`.

---

## 5. Checkpoints — comment les animer

### Checkpoint 1 (après l'étape 1)

Ce checkpoint se lance en terminal. L'élève répond aux 3 questions en tapant A, B, C ou D.
Le script affiche le score et une explication pour chaque réponse.

**Comment l'animer en groupe** : après que tout le monde a lancé le checkpoint, demandez
à voix haute : "Qui a eu 3/3 ?" Levée de main. "Qui a eu 2/3 ?" Levée de main. Pour ceux
qui ont eu 1/3 ou moins, ne les stigmatisez pas : "Prenez 5 minutes pour lire la définition
de 'hallucination' dans le Carnet de bord du GUIDE-ELEVE, puis relancez le quiz."

Ne passez pas à l'étape suivante avant que chaque élève ait au moins 2/3. Ce seuil est
délibérément bas — 2/3 signifie qu'on a compris l'essentiel.

**Les 3 questions et réponses attendues :**

Question 1 : définition de l'hallucination LLM. Réponse correcte B — "réponse fausse mais
plausible produite par le LLM faute d'informations réelles". Erreur fréquente : confondre
hallucination et bug Python (réponse A) ou erreur réseau (réponse C).

Question 2 : comportement à temperature=0. Réponse correcte B — "les 3 réponses sont
identiques ou quasi-identiques". Erreur fréquente : penser que le LLM est toujours
aléatoire par nature (réponse A).

Question 3 : définition d'un token. Réponse correcte C — "unité de texte d'environ 3-4
caractères". Erreur fréquente : confondre token et mot (réponse A) ou token et clé API
(réponse B).

### Checkpoint final

Ce checkpoint lance 5 questions. Il oriente ensuite l'élève automatiquement vers Sprint,
continuation ou Bonus selon le score.

**Règle d'animation** : laissez les élèves passer le checkpoint en silence et individuellement.
Après, affichez au tableau la répartition : "Combien vont en Bonus ? Combien en Sprint ?"
Ne donnez pas les bonnes réponses à voix haute — les explications sont dans le script.

**Les 5 questions portent sur** :
1. LLM sans RAG pour données privées — réponse B (hallucination systématique).
2. Différence system prompt / user prompt — réponse C (rôle vs requête).
3. Comportement à temperature=0.9 puis temperature=0 — réponse B (déterminisme).
4. Définition du knowledge cutoff — réponse B (date de fin d'entraînement).
5. Correction de max_tokens=50 — réponse C (augmenter à 1024 ou supprimer).

**Si un élève conteste un résultat** : lisez l'explication affichée par le script. Elle
est détaillée et justifiée. Ne la court-circuitez pas en donnant votre propre résumé.

---

## 6. Questions fréquentes

### "Pourquoi le modèle invente au lieu de dire 'je ne sais pas' ?"

Explication à donner : le modèle a été entraîné à prédire le token le plus probable étant
donné ce qui précède. Sa tâche est de compléter du texte de manière plausible, pas de
vérifier si ce texte est vrai. Quand on lui pose une question sur votre chaudière, il n'a
pas accès à un dictionnaire de vérité — il n'a que des statistiques. Il répond donc avec
ce qui statistiquement ressemble à une bonne réponse sur les chaudières, sans savoir que
c'est faux pour votre logement précis.

Analogie utile : imaginez quelqu'un qui a lu des milliers de notices de chaudière et
d'articles sur le logement, mais qui n'a jamais vu votre appartement. Posez-lui "quelle
est ma chaudière ?" Il va improviser avec les marques qu'il connaît le mieux. C'est
exactement ce que fait le modèle.

### "Temperature=0 donne-t-elle toujours exactement la même réponse ?"

Réponse honnête : quasi-toujours. Temperature=0 est déterministe au sens strict pour un
modèle donné, une version donnée, et une infrastructure donnée. En pratique, sur des
services hébergés comme Claude, des micro-variations d'infrastructure peuvent très
rarement produire des réponses légèrement différentes. Pour tous les usages pratiques,
temperature=0 est équivalent à "déterministe".

Si un élève observe deux réponses différentes à temperature=0, demandez-lui de vérifier
qu'il utilise bien le même modèle (ANTHROPIC_MODEL dans .env) et qu'il ne comparait pas
une réponse obtenue hier (quand Claude était une version différente) avec une d'aujourd'hui.

### "Comment changer de modèle ?"

Deux façons. La plus simple : modifier `ANTHROPIC_MODEL` dans le fichier `.env`.

```
ANTHROPIC_MODEL=claude-haiku-4-5
```

Les valeurs disponibles sont les noms de modèles Anthropic : `claude-haiku-4-5`,
`claude-sonnet-4-5`, `claude-sonnet-4-6`. Le code dans `homebutler/llm/provider.py` lit
cette variable automatiquement — il n'y a rien d'autre à toucher.

La seconde façon : passer le modèle directement en argument à `get_llm()` si la fonction
le supporte, ou instancier `ChatAnthropic(model="...")` directement (surtout dans le
contexte du Bonus).

### "Pourquoi utiliser LangChain plutôt que l'API Anthropic directement ?"

LangChain fournit une couche d'abstraction qui permet de changer de fournisseur LLM
sans réécrire le code applicatif. Dans cet atelier, la fonction `get_llm()` renvoie soit
un `ChatAnthropic`, soit un `ChatOllama` selon `LLM_PROVIDER` dans `.env`. Le reste du
code (invoquer le LLM, passer des messages) est identique dans les deux cas. Cette
abstraction est utile dès qu'on veut comparer des fournisseurs ou passer d'un modèle local
à un modèle hébergé.

### "Les tokens coûtent combien ?"

Pour Claude Sonnet, le tarif Anthropic à la date de la formation est environ 3 dollars
pour 1 million de tokens en entrée et 15 dollars pour 1 million de tokens en sortie
(vérifiez sur https://anthropic.com/pricing car ces tarifs changent). Pour cet atelier,
chaque question fait environ 50 tokens en entrée et 200 tokens en sortie. Cinq questions
coûtent donc moins d'un centime. Il n'y a pas de risque de facture surprise pour cet
atelier.

### "Peut-on voir les tokens consommés dans le code ?"

Oui. Après `response = llm.invoke([HumanMessage(content=question)])`, l'objet `response`
contient `response.usage_metadata` avec les champs `input_tokens` et `output_tokens`.
Affichez-les avec `print(response.usage_metadata)`.

### "Le system prompt est-il facturé ?"

Oui. Chaque token envoyé à l'API, qu'il soit dans le system prompt ou le user prompt,
est facturé en tokens d'entrée. Un system prompt de 200 tokens répété sur 1000 requêtes
coûte 200 000 tokens d'entrée. C'est à garder à l'esprit pour la production, mais
négligeable pour un atelier.

---

## 7. Signaux d'alerte (élève bloqué)

### L'élève n'arrive pas à importer get_llm

Vérifiez que le package HomeButler est installé en mode développement :

```bash
pip install -e .
```

La commande doit être lancée depuis la racine du projet, avec le venv activé. Si le
fichier `homebutler/__init__.py` n'existe pas, il y a un problème de structure. Vérifiez
avec `ls homebutler/`.

### Le script lève ModuleNotFoundError sur anthropic ou langchain

Les dépendances n'ont pas été installées. Lancer :

```bash
pip install -r requirements_atelier01.txt
```

Puis revérifier avec `bash scripts/check_atelier_ready.sh 01`.

### L'API retourne une erreur d'authentification (401 ou AuthenticationError)

La clé `ANTHROPIC_API_KEY` dans `.env` est incorrecte, vide, ou contient des espaces.
Ouvrez `.env` dans un éditeur et vérifiez qu'il n'y a pas d'espace autour du `=` et que
la clé commence bien par `sk-ant-`. Après correction, relancez le script — Python relit
`.env` à chaque lancement.

### L'API retourne une erreur de quota ou RateLimitError

Trop de requêtes simultanées depuis la même clé. Solutions : attendre 60 secondes,
ou réduire le nombre de questions posées en une seule fois. Pour cet atelier, 5 questions
en séquence ne devrait pas dépasser les limites Anthropic d'un compte standard.

### Le test pytest échoue après réparation du bug

L'élève a peut-être réparé le bug dans le mauvais fichier. Chaque test vérifie un
comportement précis sur `exercice.py`. Si l'élève a modifié `solution.py` par erreur,
le test continuera d'échouer. Demandez-lui de relire le test avec `cat` pour identifier
quel fichier est testé.

Il est aussi possible que l'élève ait réparé partiellement : par exemple pour le bug v1,
il a changé `temperature` dans un seul appel sur deux. Demandez-lui de relire son fichier
entier.

### L'élève ne voit pas de variabilité avec temperature=0.9

Sur des questions très courtes et très contraintes, même à T=0.9 le modèle tend à
reproduire les mêmes réponses. Pour observer clairement la variabilité, suggérez de poser
une question ouverte : "Décris en quelques mots à quoi ressemble mon appartement." Avec
T=0.9, les réponses varieront nettement d'un run à l'autre.

### L'élève a moins de 3/5 au checkpoint final mais veut quand même aller en Bonus

Tenez la règle. Le Sprint est conçu pour être rapide (30 minutes) et ciblé. Un élève qui
passe en Bonus sans maîtriser temperature et system prompt va se perdre dans le défi 1
(comparaison Haiku/Sonnet requiert de comprendre les paramètres) et le défi 2 (few-shot
requiert de comprendre les system prompts). Investir 30 minutes en Sprint maintenant
économise 60 minutes de confusion en Bonus.

---

## 8. Transition vers l'atelier 02

### Ce que vous dites en clôture

Prenez 5 minutes à la fin pour synthétiser. Posez ces deux questions au groupe :

"Quel est le hallucination rate que vous avez mesuré sur les 5 questions privées ?" En
général, les réponses varient entre 80 % et 100 %. Notez le chiffre au tableau.

"Si vous étiez le PM HomeButler et que vous voyiez ce chiffre, quelle serait votre
décision ?" L'objectif est que les élèves articulent eux-mêmes le problème avant que
vous ne présentiez la solution.

Puis : "L'atelier 02 va résoudre exactement ce problème. On va injecter les vrais
documents du logement dans le modèle, au moment où il répond. Ce mécanisme s'appelle
le RAG — Retrieval-Augmented Generation. Votre premier exercice de demain matin sera
de repasser ce même jeu de 5 questions. Le taux cible : 0 %."

### Ce que les élèves doivent avoir en main pour l'atelier 02

Avant de quitter la salle, chaque élève doit :

1. Avoir son hallucination rate noté (celui de l'atelier 01, sans RAG). Ce chiffre sera
   la baseline de comparaison à l'atelier 02.
2. Avoir passé le checkpoint final avec un score d'au moins 3/5.
3. Savoir lancer `python ateliers/atelier-01-llm-baseline/exercice.py` sans erreur.

### Ce que vous devez préparer pour l'atelier 02

La branche suivante est `atelier/02-rag-pipeline`. Avant l'atelier 02, faites un
`git checkout atelier/02-rag-pipeline` sur votre machine et lancez
`bash scripts/check_atelier_ready.sh 02`. L'atelier 02 requiert des PDFs dans
`data/documents/` et la construction d'un index FAISS. Si les PDFs sont absents :

```bash
python scripts/generate_documents.py
```

Si l'index FAISS n'est pas encore construit, il le sera automatiquement au premier
lancement de l'exercice 02.
