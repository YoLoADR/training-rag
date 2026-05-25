# GUIDE FORMATEUR — Atelier 02 : RAG Simple FAISS (3h)

> Document réservé au formateur. Ne pas distribuer aux élèves.
> Version : 2026-05-25 | Branche : `atelier/02-rag-simple`

---

## 1. Ce que l'élève doit comprendre à la fin

A l'issue de cet atelier, chaque élève doit pouvoir expliquer à voix haute, sans relire le guide :

**La grande idée du RAG.** L'atelier 01 a prouvé que le LLM invente des informations qu'il ne connaît pas (hallucinations). Cet atelier apporte la solution : au lieu de demander au modèle de "se souvenir" d'une information, on lui soumet les bons documents directement dans le prompt. Le modèle n'a plus qu'à lire et synthétiser — il ne peut plus inventer. La question fil rouge le démontre en quelques secondes : "Quelle est la marque de ma chaudière ?" donne une réponse inventée sans RAG, et "Viessmann Vitodens 100-W" avec RAG, source citée.

**Pourquoi il faut découper les PDFs.** Un PDF entier fait souvent plusieurs dizaines de milliers de caractères. Transformer ce bloc en un seul vecteur numérique produit un "embedding moyen" qui ne représente précisément aucun sujet. Découper en morceaux (chunks) permet d'obtenir un vecteur par concept, ce qui rend la recherche précise.

**La différence entre chunking fixe et chunking récursif.** Le chunking fixe coupe tous les 512 caractères sans se soucier des phrases ou des paragraphes — une phrase peut être tranchée en plein milieu. Le chunking récursif essaie d'abord de couper aux séparateurs naturels (saut de paragraphe, saut de ligne, point) et ne coupe "brutalement" que si aucun séparateur n'est disponible. Sur des PDFs techniques, le récursif donne de meilleurs résultats.

**Ce qu'est chunk_overlap et pourquoi il est nécessaire.** Les 50 derniers caractères du chunk N sont répétés au début du chunk N+1. Cela garantit qu'une information courte (un code erreur, un numéro de modèle) qui se situe exactement à la frontière entre deux chunks sera entièrement présente dans au moins l'un d'eux.

**Ce qu'est FAISS et pourquoi c'est plus rapide qu'une boucle.** FAISS est une bibliothèque Meta qui construit un index sur des vecteurs et retrouve les plus proches en quelques millisecondes via un algorithme ANN (Approximate Nearest Neighbors). Sans FAISS, il faudrait comparer la requête à chaque chunk un par un — pour 50 chunks c'est tolérable, pour 50 000 chunks c'est inutilisable.

**Ce que mesure le Recall@k et quel est l'objectif.** Sur les 5 questions étalons pour lesquelles on connaît le bon document, combien de fois le bon document apparaît-il dans les k premiers résultats du retriever ? Recall@5 = 0.80 signifie que dans 4 cas sur 5, le bon document est dans le top 5. C'est le seuil minimal attendu à la fin de l'atelier.

**Pourquoi on ne reconstruit pas l'index à chaque requête.** Construire l'index = calculer les embeddings de tous les chunks = opération coûteuse (plusieurs secondes). Interroger l'index = recherche ANN dans les vecteurs existants = opération rapide (< 1 seconde). On construit une fois, on interroge autant de fois qu'on veut.

---

## 2. Setup formateur — avant l'atelier

### 2.1 Préparation la veille (environ 20 minutes)

Branchez-vous sur la bonne branche et vérifiez que tout tourne sur votre machine avant d'accueillir les élèves. Cela vous évite de perdre du temps en séance.

```bash
git checkout atelier/02-rag-simple
source .venv/bin/activate
```

Vérifiez que les PDFs du logement sont présents :

```bash
ls data/documents/
```

Vous devez voir au minimum : `notice_chaudiere.pdf`, `notice_vmc.pdf`, `bail.pdf`. Si le répertoire est vide ou absent, générez-les :

```bash
python scripts/generate_documents.py
```

Pré-téléchargez le modèle d'embeddings (environ 300 Mo, une seule fois) :

```bash
python scripts/preload_models.py
```

Ce téléchargement se fait dans `~/.cache/fastembed/`. Si vous animez en salle sans accès internet, faites-le impérativement la veille. Le modèle utilisé est `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` — il fonctionne en français et en anglais sans GPU.

Lancez le script exercice.py de la solution pour vous assurer que tout tourne bien :

```bash
python ateliers/atelier-02-rag-simple/solution.py
```

Vous devez voir la réponse "Viessmann Vitodens 100-W" et un Recall@5 affiché supérieur ou égal à 0.80. Si ce n'est pas le cas, consultez la section 7 (Signaux d'alerte) de ce guide.

Vérifiez les patches de bugs — chacun doit s'appliquer proprement :

```bash
git apply --check ateliers/atelier-02-rag-simple/bugs/v1.patch
git apply --check ateliers/atelier-02-rag-simple/bugs/v2.patch
git apply --check ateliers/atelier-02-rag-simple/bugs/v3.patch
```

Si l'une de ces commandes retourne une erreur, l'index git a pu être modifié. Faites `git checkout -- .` pour repartir d'un état propre.

### 2.2 Vérifications le matin de l'atelier (5 minutes)

```bash
# Vérifier que la branche est la bonne
git branch

# Lancer le vérificateur automatique
bash scripts/check_atelier_ready.sh 02

# Vérifier que la clé API est présente
grep ANTHROPIC_API_KEY .env
```

### 2.3 Avertissements courants à connaître à l'avance

**Warning fastembed "mean pooling instead of CLS embedding".** Ce message s'affiche depuis la version 0.5.2 de fastembed. Il est normal et sans conséquence. Dites aux élèves de l'ignorer.

**Erreur FAISS sur Mac ARM (M1/M2/M3).** Si un élève a une erreur lors de `pip install faiss-cpu`, la solution est :
```bash
pip install faiss-cpu --upgrade
```
Cette commande télécharge le binaire pré-compilé pour ARM au lieu de tenter une compilation locale.

---

## 3. Déroulé détaillé

### Budget temps global

| Segment | Durée | Notes |
|---|---|---|
| Accroche + briefing | 10 min | Posez la question fil rouge sans RAG devant tout le monde |
| Etape 1 : chargement + chunking | 25 min | Tronc commun |
| Mini-lab fixed vs recursive | 15 min | Tronc commun |
| Etape 2 : FAISS + chaîne RAG | 30 min | Tronc commun |
| Bug Hunt (3 bugs) | 20 min | Tronc commun |
| Mesure Recall@5 + checkpoint final | 15 min | Tronc commun |
| Sprint (si nécessaire) | 30 min | Pour élèves < 60% au checkpoint final |
| Bonus (si avance) | 60-70 min | Pour élèves >= 80% au checkpoint final |

### 3.1 Accroche (10 min)

Ouvrez un terminal devant la classe et posez la question fil rouge SANS RAG, directement au LLM :

```bash
python -c "
from homebutler.llm.provider import get_llm
llm = get_llm()
print(llm.invoke('Quelle est la marque de ma chaudière ?'))
"
```

Le LLM va inventer une marque — parfois "Viessmann", parfois "Atlantic", parfois "Vaillant". Relancez deux fois pour montrer que la réponse change. Demandez à la classe : "Ce LLM ment-il ?" La réponse est non — il extrapole depuis ses données d'entraînement, il ne connaît pas votre logement fictif.

Annoncez l'objectif de l'atelier : à la fin, la même question retournera "Viessmann Vitodens 100-W" avec la source `notice_chaudiere.pdf`. Et ce sera reproductible, car la réponse vient des documents, pas des poids du modèle.

### 3.2 Etape 1 — Chargement des PDFs et chunking (25 min)

Les élèves ouvrent `exercice.py` et complètent les TODO 1 à 3.

**Commandes à faire lancer par les élèves :**

```bash
git checkout atelier/02-rag-simple
source .venv/bin/activate
python scripts/generate_documents.py  # si les PDFs ne sont pas encore là
python ateliers/atelier-02-rag-simple/exercice.py
```

**Observation attendue** quand les TODO 1-3 sont complétés :

```
Pages chargées : ~15-20 pages
chunks_fixed     : ~40-60 chunks
chunks_recursive : ~35-55 chunks
```

Le nombre exact peut varier selon les PDFs générés, mais l'ordre de grandeur doit être cohérent. Si un élève obtient 2 ou 3 chunks en tout, c'est que le chunk_size est anormalement grand — vérifiez son paramètre.

**Point formateur sur le mini-lab fixed vs recursive :** Après l'étape 1, faites construire deux index FAISS, un sur `chunks_fixed` et un sur `chunks_recursive`, et mesurez le Recall@5 de chacun. Les élèves remplissent le tableau comparatif du guide élève. Sur les PDFs HomeButler, le chunking récursif donne en général un Recall@5 légèrement supérieur — mais l'écart peut être faible. L'important n'est pas le chiffre exact, c'est que l'élève comprenne pourquoi les deux nombres diffèrent.

### 3.3 Etape 2 — FAISS et chaîne RAG (30 min)

Les élèves complètent les TODO 4 à 6.

Les deux points de blocage fréquents à cette étape :

Premier point : l'élève appelle `build_faiss_index` avec `force_rebuild=True` à l'intérieur de la boucle de requêtes Recall@5 (c'est précisément le bug v3 — certains élèves tombent dedans naturellement avant même le Bug Hunt). Si vous voyez la console afficher "Construction de l'index FAISS..." plusieurs fois de suite, c'est ce problème.

Second point : l'élève oublie de passer `format_docs` dans la chaîne LCEL. La chaîne retourne alors des objets `Document` bruts au lieu d'une chaîne de texte, et le LLM reçoit un contexte mal formaté.

**La question de démonstration à faire tourner devant la classe** une fois l'étape 2 terminée :

```bash
python -c "
# Equivalent de ce que fait solution.py
# La réponse doit citer notice_chaudiere.pdf
"
```

Ou plus simplement, faites lancer `python ateliers/atelier-02-rag-simple/solution.py` pour montrer le résultat attendu.

---

## 4. Bug Hunt — ce qui se passe concrètement

Le Bug Hunt dure environ 20 minutes. Les trois bugs sont appliqués un par un — on répare entièrement le premier avant de passer au suivant. Chaque bug s'applique avec `git apply`, produit un comportement observable, et se répare avec une modification d'une ou deux lignes.

### Bug v1 — chunk_size trop grand (512 → 2000)

**Appliquer le bug :**

```bash
git apply ateliers/atelier-02-rag-simple/bugs/v1.patch
```

**Lancer le test (doit echouer) :**

```bash
pytest ateliers/atelier-02-rag-simple/bugs/test_v1.py -v
```

**Ce que l'élève observe.** Le Recall@5 chute. Avec chunks de 2000 caractères, chaque chunk couvre plusieurs sujets différents (marque de la chaudière, codes erreur, instructions d'entretien). L'embedding de ce bloc générique est moins proche de la requête précise "Quelle est la marque de ma chaudière ?" que ne l'était l'embedding d'un petit chunk centré sur ce seul sujet.

**Ce que vous expliquez au tableau.** Imaginez un index de bibliothèque où chaque fiche résume un chapitre entier au lieu d'un seul concept. Si vous cherchez "Viessmann Vitodens", la fiche "Chaudières au gaz - chapitre 3" est moins utile qu'une fiche "Modèle exact Viessmann Vitodens 100-W". Les chunks trop grands diluent le signal.

**Le fix :**

Dans `exercice.py` (ou là où le paramètre a été changé par le patch), restaurer `chunk_size=512`.

**Valider :**

```bash
pytest ateliers/atelier-02-rag-simple/bugs/test_v1.py -v
```

Le test doit passer (PASSED en vert).

### Bug v2 — chunk_overlap nul (50 → 0)

**Appliquer le bug :**

```bash
git apply ateliers/atelier-02-rag-simple/bugs/v2.patch
```

**Lancer le test :**

```bash
pytest ateliers/atelier-02-rag-simple/bugs/test_v2.py -v
```

**Ce que l'élève observe.** Sur certaines questions précises (notamment "Code erreur F4 chaudière"), la réponse perd une partie de l'information. L'information courte se trouve exactement à la frontière entre deux chunks — ni l'un ni l'autre ne la contient en entier.

**Ce que vous expliquez au tableau.** Imaginez un livre découpé en feuillets sans jamais reprendre la dernière ligne d'un feuillet sur le suivant. Si "Code erreur F4 : signifie surchauffe" est coupé entre deux feuillets, aucun des deux ne contient l'information complète. L'overlap de 50 caractères garantit que les 50 derniers caractères du chunk N apparaissent aussi au début du chunk N+1 — la frontière est couverte deux fois.

**Le fix :**

Restaurer `chunk_overlap=50`.

**Valider :**

```bash
pytest ateliers/atelier-02-rag-simple/bugs/test_v2.py -v
```

### Bug v3 — rebuild de l'index dans la boucle de requêtes

**Appliquer le bug :**

```bash
git apply ateliers/atelier-02-rag-simple/bugs/v3.patch
```

**Lancer le test :**

```bash
pytest ateliers/atelier-02-rag-simple/bugs/test_v3.py -v
```

**Ce que l'élève observe.** Le programme prend soudainement 10 fois plus de temps. Chaque question dans la boucle Recall@5 déclenche un recalcul complet de tous les embeddings avant de faire la recherche. La console affiche "Construction de l'index FAISS..." cinq fois de suite au lieu d'une seule.

**Ce que vous expliquez au tableau.** Construire l'index, c'est vectoriser tous les chunks et bâtir la structure de recherche — c'est l'opération coûteuse. Interroger l'index, c'est projeter la requête dans le même espace vectoriel et trouver les voisins — c'est rapide. Si l'index ne change pas entre deux requêtes (et il ne change pas, les documents sont les mêmes), le reconstruire à chaque fois est une pure perte de temps.

**Le fix.** Déplacer `build_faiss_index(force_rebuild=True)` à l'extérieur de la boucle de requêtes. Le code correct ressemble à ceci :

```python
# Construction — une seule fois, avant la boucle
faiss_store = build_faiss_index(chunks, force_rebuild=True)

# Retrieval — à l'intérieur de la boucle, rapide
for question, expected_source in BENCHMARK_QUESTIONS:
    results = faiss_store.similarity_search(question, k=5)
```

**Valider :**

```bash
pytest ateliers/atelier-02-rag-simple/bugs/test_v3.py -v
```

---

## 5. Checkpoints — comment les animer

### Checkpoint 1 — après l'étape chargement + chunking

Le checkpoint 1 est un quiz de 3 questions sur les concepts chunking, fixed vs recursive, et chunk_overlap. Le score de passage est 2 questions sur 3.

```bash
python ateliers/atelier-02-rag-simple/checkpoints/check_1.py
```

**Comment animer.** Ne lisez pas les questions à voix haute avant que les élèves aient lancé le script — laissez-les répondre seuls. Après le résultat, demandez à deux ou trois élèves d'expliquer leur raisonnement sur la question qu'ils ont ratée, sans donner vous-même la réponse. Utilisez les analogies du guide élève si un concept reste flou.

Si un élève est à 1/3, c'est le signal pour un accompagnement individuel. Demandez-lui d'ouvrir le Carnet de bord du guide élève et de vous lire la définition du concept raté — pas de mémoire, à voix haute — avant de retenter.

### Checkpoint final — après le Bug Hunt et la mesure

Le checkpoint final est un quiz de 5 questions. Il détermine si l'élève part en Bonus ou en Sprint.

```bash
python ateliers/atelier-02-rag-simple/checkpoints/check_final.py
```

**Grille de décision :**

- Score 4/5 ou 5/5 (80% et plus) : Bonus. L'élève peut attaquer les défis avancés.
- Score 3/5 (60%) : entre les deux. Invitez l'élève à relire le Carnet de bord sur les deux concepts ratés, puis à choisir librement Bonus ou Sprint.
- Score 2/5 ou moins (moins de 60%) : Sprint. L'élève a besoin de consolider avant de passer à l'atelier 03.

**Comment gérer les deux flux en parallèle.** Pendant que les élèves en Sprint travaillent sur les exercices guidés, passez du temps avec les élèves Bonus sur les défis avancés (variation de chunk_size, comparaison MMR vs similarity). Les deux groupes convergent sur la wrap-up de 10 minutes.

---

## 6. Questions fréquentes

**"Pourquoi découper ? FAISS ne peut pas prendre le PDF entier ?"**

Techniquement il peut — rien n'empêche de créer un seul embedding pour le PDF entier. Mais cet embedding sera une moyenne de tous les sujets abordés dans le PDF. Si le PDF parle de la marque de la chaudière, des codes erreur, de l'entretien et des garanties, l'embedding de ce PDF sera "au milieu" de tous ces sujets, et précis sur aucun. Quand la requête "Quelle est la marque ?" arrive, le retriever ne trouvera pas ce PDF aussi bien qu'un petit chunk centré uniquement sur la marque. Le chunking est une question de précision de signal, pas une limitation technique de FAISS.

**"Fixed vs recursive, quelle différence concrète ?"**

Sur une phrase comme "La chaudière Viessmann Vitodens 100-W est une chaudière à condensation.", le chunking fixe à 30 caractères va peut-être couper après "Viessmann Vitodens 10" — en plein milieu du numéro de modèle. Le chunking récursif va d'abord chercher un saut de paragraphe, puis un saut de ligne, puis un point — et coupera après la phrase complète. Résultat : le numéro de modèle reste entier dans le chunk. Pour des PDFs techniques avec des valeurs précises (marques, codes, dimensions), le récursif préserve mieux l'intégrité des données.

**"chunk_overlap sert à quoi ?"**

Imaginez un livre découpé en feuillets de 10 lignes. Si une information importante commence à la ligne 9 du feuillet 3 et se termine à la ligne 2 du feuillet 4, sans overlap vous avez une moitié de cette information dans chaque feuillet — et aucun feuillet ne la contient en entier. Avec un overlap de 2 lignes, les 2 dernières lignes du feuillet 3 sont répétées au début du feuillet 4 : l'information est entière dans le feuillet 4. L'overhead (quelques caractères en double) est négligeable, le gain de qualité est significatif.

**"FAISS, c'est quoi exactement ?"**

C'est une bibliothèque développée par Meta pour faire de la recherche de voisins proches sur des vecteurs, très rapidement. Sans FAISS, pour trouver les 5 chunks les plus proches d'une requête, il faut calculer la distance entre la requête et chaque chunk — si vous avez 10 000 chunks, c'est 10 000 calculs. FAISS construit une structure d'index (comparable à un index alphabétique) qui permet de "sauter" directement aux voisins proches sans tout parcourir. Sur 10 000 vecteurs, FAISS est instantané ; une boucle brute prendrait plusieurs secondes.

**"Recall@5 = 0.80, ça signifie que le LLM répond correctement 80% du temps ?"**

Pas exactement — ce sont deux métriques différentes. Le Recall@5 mesure uniquement le retriever : est-ce que le bon document est dans les 5 premiers résultats ? Si le Recall@5 est 0.80, dans 80% des cas le retriever donne le bon document au LLM. Mais même si le bon document est là, le LLM peut encore "interpréter" incorrectement — c'est ce que mesure la faithfulness. Le Recall@k est le plafond de qualité : si le retriever rate un document, le LLM ne peut pas le mentionner, même s'il est excellent.

**"Pourquoi le modèle d'embeddings est téléchargé une seule fois ?"**

Les poids du modèle sont stockés dans `~/.cache/fastembed/`. Une fois téléchargés, ils restent sur la machine. Les appels suivants chargent les poids depuis le disque local, sans accès internet. C'est pourquoi il faut faire `python scripts/preload_models.py` avant l'atelier dans une salle sans internet stable.

**"La Piste Vibe, l'élève peut-il tout déléguer à l'IA ?"**

Non. La Piste Vibe permet la délégation à un outil IA, mais impose une obligation contractuelle : à chaque étape, l'élève doit être capable d'expliquer ce que fait le code généré et pourquoi ces paramètres. Le CLAUDE.md local refuse d'afficher `solution.py` et refuse de donner la réponse directe aux checkpoints.

---

## 7. Signaux d'alerte (élève bloqué)

**Recall@5 = 0.00 ou 0.20 en fin d'atelier.**

Trois causes probables. La première : le mauvais fichier PDF est ciblé dans les questions benchmark — vérifiez que les noms de fichiers dans `BENCHMARK_QUESTIONS` (dans `exercice.py`) correspondent aux vrais noms dans `data/documents/`. La deuxième : le chunk_size est encore à 2000 (bug v1 non réparé) ou chunk_overlap est à 0 (bug v2 non réparé). La troisième : l'index FAISS a été construit sur `chunks_fixed` au lieu de `chunks_recursive`, ce qui peut faire varier légèrement le résultat.

**"Construction de l'index FAISS..." s'affiche à chaque requête.**

C'est le bug v3 — intentionnel dans le Bug Hunt, mais parfois introduit involontairement par l'élève. Le `build_faiss_index(force_rebuild=True)` est à l'intérieur de la boucle de requêtes. Demandez à l'élève de localiser la ligne et de la déplacer avant la boucle.

**Erreur `NotImplementedError: TODO 2 — charger les PDFs` après avoir lancé `exercice.py`.**

L'élève n'a pas complété le TODO 2. C'est normal en début d'atelier, mais si ce message apparaît 30 minutes après le démarrage, c'est qu'il est bloqué sur l'import ou la boucle de chargement. La solution est dans le commentaire juste au-dessus du `raise` — les lignes commentées montrent exactement le code à décommenter.

**Erreur `ModuleNotFoundError: No module named 'homebutler'`.**

Le package n'est pas installé en mode éditable. Lancer :

```bash
pip install -e .
```

**Erreur `faiss.swigfaiss` ou `ImportError` lié à FAISS.**

Sur Mac ARM, l'installation binaire est nécessaire :

```bash
pip install faiss-cpu --upgrade
```

**L'élève a un Recall@5 de 1.00 dès le début.**

Ce n'est pas impossible sur les 5 questions étalons avec les PDFs HomeButler — les questions sont bien calibrées pour ces documents. C'est un bon signe : l'élève peut directement passer aux défis Bonus.

**L'élève ne comprend pas la chaîne LCEL.**

Ne détaillez pas toute la syntaxe de LCEL — c'est hors scope de cet atelier. Dites-lui de traiter la chaîne comme une recette en 3 ingrédients : le retriever qui trouve les documents, le template qui formate la question + les documents, et le LLM qui génère la réponse. Il complète les TODO en copiant le modèle fourni dans les commentaires. La compréhension fine de LCEL est prévue en atelier 03.

---

## 8. Transition vers l'atelier 03

L'atelier 02 est terminé quand :

1. `python ateliers/atelier-02-rag-simple/solution.py` répond "Viessmann Vitodens 100-W" en citant `notice_chaudiere.pdf`.
2. Le Recall@5 affiché est supérieur ou égal à 0.80.
3. Les trois tests de bugs sont au vert (`pytest ateliers/atelier-02-rag-simple/bugs/test_v1.py test_v2.py test_v3.py -v`).
4. L'élève a passé le checkpoint final avec un score supérieur ou égal à 3/5.

**La question ouverte à poser avant de clore l'atelier.** Demandez à la classe : "FAISS est rapide, mais si demain on a 10 000 documents et qu'on veut garder l'index à jour en temps réel, quel problème pose FAISS ?" — FAISS est un index en mémoire, sans persistance native entre deux processus Python (sauf sauvegarde/rechargement explicite), et il ne gère pas les mises à jour incrémentales simplement. C'est pour cela qu'on utilisera ChromaDB à l'atelier 03 : une base vectorielle persistante avec des capacités de filtrage par métadonnées.

**Ce que l'atelier 03 apporte en plus.** L'atelier 02 construit un RAG simple : une question → un retriever → une réponse. L'atelier 03 ajoute un agent ReAct multi-outils : HomeButler pourra non seulement chercher dans les PDFs, mais aussi appeler des outils (API météo, calendrier, commandes domotique). La brique RAG construite ici devient l'un des outils de cet agent.

**Commande de préparation pour l'atelier 03 :**

```bash
git checkout atelier/03-agent-react
source .venv/bin/activate
bash scripts/check_atelier_ready.sh 03
```

Si l'élève voit "OK" sur les trois vérifications du script, il est prêt.
