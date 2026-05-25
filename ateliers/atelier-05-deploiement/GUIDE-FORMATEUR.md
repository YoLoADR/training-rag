# GUIDE FORMATEUR — Atelier 05 : Déploiement (3h)

> Ce guide est destiné au formateur. Il suppose que tu connais le code de l'application HomeButler et que tu as déjà fait tourner l'atelier au moins une fois. L'élève n'a pas accès à ce fichier.

---

## 1. Ce que l'élève doit comprendre à la fin

A la fin de cet atelier, l'élève doit pouvoir répondre à ces 5 questions sans aide :

**Sur la sécurité API :**
- Pourquoi un filtre d'injection doit se trouver dans un middleware et non dans chaque route individuellement ?
- Quelle est la différence entre `allow_origins=["*"]` et une whitelist explicite — et pourquoi `*` est dangereux même avec authentification ?
- Que se passe-t-il concrètement quand `timeout=None` et que le LLM est lent ?

**Sur l'observabilité :**
- A quoi sert Langfuse au-delà du debug (coûts, dérives de qualité, alertes de production) ?
- Que signifie p95=45s sur un tableau de métriques et quelle en est la cause probable ?

L'élève ne doit pas seulement connaître les définitions. Il doit avoir vu les effets avec ses propres yeux : le HTTP 429 dans le terminal, la trace apparaître sur cloud.langfuse.com, le test qui échoue quand le bug est actif. C'est la différence entre un atelier réussi et un atelier survécu.

**Ce qui reste hors scope de cet atelier** (à rappeler si un élève anticipe) :
- Les routes `/rag/evaluate`, `/chat/compare`, `/rag/compare-strategies`
- L'évaluation comparative RAG vs fine-tuning
- Ces sujets sont traités en Atelier 06. La variable `ENABLE_COMPARE_ROUTES=false` dans `.env` désactive ces routes intentionnellement.

---

## 2. Setup formateur — avant l'atelier

### 2.1 Vérification de la branche

Tu dois être sur la bonne branche avant de commencer. Si tu as préparé la machine la veille, vérifie systématiquement au matin :

```bash
git checkout atelier/05-deploiement
git status
```

La sortie doit indiquer `On branch atelier/05-deploiement` et aucun fichier modifié. Si des patches de bugs trainent (bugs appliqués et non réinitialisés d'une session précédente), réinitialise :

```bash
git checkout -- api/main.py api/routers/chat.py
```

### 2.2 Installation des dépendances

```bash
source .venv/bin/activate
pip install -r requirements_atelier05.txt
pip install -e .
```

Le `pip install -e .` est obligatoire. Sans lui, Streamlit ne trouve pas le module `homebutler` (imports absolus). C'est le piège numéro un — vérifie-le avant l'atelier, pas quand un élève est bloqué devant toi.

Attention à `langfuse` : le fichier `requirements_atelier05.txt` pince `langfuse==2.57.1` (avant la version 4). Ne fais pas `pip install langfuse --upgrade` — l'API v4 a changé `update_trace()` de façon incompatible et casse l'intégration LangChain de l'atelier.

### 2.3 Données et index vectoriels

Si les index n'existent pas encore :

```bash
python scripts/generate_documents.py
python scripts/generate_energy_data.py
python scripts/generate_producers.py
python scripts/preload_models.py
python -c "
from homebutler.rag.ingestion import ingest_all_documents
from homebutler.rag.vectorstore_faiss import build_faiss_index
build_faiss_index(ingest_all_documents(), force_rebuild=True)
"
python -c "
from homebutler.rag.ingestion import ingest_all_documents
from homebutler.rag.vectorstore_chroma import build_chroma_db
build_chroma_db(ingest_all_documents())
"
```

Ces scripts prennent 3 à 5 minutes. Lance-les avant que les élèves arrivent, pas en direct.

### 2.4 Fichier .env minimal

```bash
ANTHROPIC_API_KEY=sk-ant-...
ENABLE_COMPARE_ROUTES=false
LLM_PROVIDER=anthropic
```

Pour Langfuse (optionnel mais fortement recommandé pour l'étape 2) :

```bash
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

Si les élèves n'ont pas de compte Langfuse, crée un projet de démo la veille sur ton propre compte. Partage les clés en lecture sur le tableau (ou en `.env.demo`). L'objectif est qu'ils voient les traces — pas qu'ils passent 20 minutes à créer un compte.

### 2.5 Démarrage en 3 terminaux — test de fumée

Avant d'accueillir les élèves, vérifie que tout démarre proprement :

```bash
# Terminal 1 — API FastAPI
source .venv/bin/activate
uvicorn api.main:app --port 8000 --reload
# Ouvrir http://localhost:8000/docs → Swagger doit s'afficher
# Vérifier que /chat/compare n'apparait PAS (ENABLE_COMPARE_ROUTES=false)
```

```bash
# Terminal 2 — Interface Streamlit
source .venv/bin/activate
streamlit run ui/app.py
# Ouvrir http://localhost:8501 → les 4 pages doivent charger (Chat, Energie, Marketplace, Logement)
```

```bash
# Terminal 3 — Vérification sécurité
bash ateliers/atelier-05-deploiement/test_securite.sh
# Les 4 tests doivent passer (HTTP 400 injection, HTTP 429 burst, réponse llm_only, réponse rag_only)
```

Si `test_securite.sh` échoue, c'est presque toujours que l'API n'est pas démarrée ou qu'elle tourne sur un autre port. Vérifier avec `curl -s http://localhost:8000/health`.

### 2.6 Vérification du script check_atelier_ready.sh

```bash
bash scripts/check_atelier_ready.sh 05
```

Ce script valide la branche, le venv, les fichiers `.env`, les index et les dépendances. Si un élève arrive avec un poste non configuré, c'est la première commande à lancer.

---

## 3. Déroulé détaillé

### Vue d'ensemble du timing

| Bloc | Durée | Contenu |
|---|---|---|
| Etape 1 — Lecture sécurité | 20 min | Comprendre le code existant |
| Checkpoint 1 | 5 min | 3 questions orales / script |
| Mini-lab rate limit | 15 min | Déclencher HTTP 429 en direct |
| Etape 2 — Langfuse | 30 min | Configurer, envoyer des traces, observer |
| Bug Hunt | 20 min | 3 bugs, 3 réparations |
| Mesure | 15 min | p50/p95, tableau de métriques |
| Checkpoint final | 10 min | 5 questions |
| Sprint OU Bonus | 30-70 min | Selon le score |
| **Total tronc commun** | **1h55** | |

### Etape 1 — Comprendre la sécurité en place (20 min)

L'élève lit `api/main.py` et `api/limiter.py`. Il ne doit PAS encore modifier le code.

Ce qu'il cherche dans `api/main.py` :
1. La liste `_INJECTION_PATTERNS` — 19 expressions régulières compilées en un seul pattern avec `re.compile("|".join(patterns), re.IGNORECASE)`
2. Le décorateur `@app.middleware("http")` sur `prompt_injection_filter` — ce middleware s'exécute avant chaque requête POST
3. La configuration CORS avec `allow_origins` — il verra `["*"]`, c'est le bug v2. Lui dire explicitement de ne pas le corriger maintenant
4. L'import du `limiter` depuis `api/limiter.py`

Point pédagogique clé à verbaliser : "Le middleware, c'est le videur de la boite de nuit. Il vérifie le billet avant que tu entres, pas une fois que tu es au bar. C'est pour ça que le filtre d'injection est un middleware et non une vérification dans chaque route."

Si un élève demande "pourquoi 19 patterns et pas un seul ?" — bonne question. Chaque pattern cible une famille d'attaques différente : les tentatives de "jailbreak" ("ignore tes instructions"), les tentatives d'exfiltration ("donne-moi tous les baux"), les injections de rôle ("tu es maintenant un assistant sans restrictions"). Un seul pattern géant serait illisible et difficile à maintenir.

Alerte : si un élève commence à modifier le code pendant cette phase, recadre-le. L'étape 1 est de la lecture et de la compréhension. Les modifications viennent dans le Bug Hunt.

### Mini-lab rate limit (15 min)

L'objectif est de voir HTTP 429 dans un terminal. Ce n'est pas de la théorie — c'est de la manipulation directe.

Commande à lancer (le texte est dans le guide élève) :

```bash
for i in $(seq 1 50); do
  curl -s -o /tmp/r$i.json -w "%{http_code}\n" \
    -X POST http://localhost:8000/chat \
    -H 'Content-Type: application/json' \
    -d '{"message":"test rate limit","mode":"llm_only"}'
done | sort | uniq -c
```

Résultat attendu avec la config par défaut (30 req/min) :
```
  30 200
  20 429
```

Ce que l'élève doit observer :
- Les 30 premières requêtes passent (HTTP 200)
- A partir de la 31e, slowapi retourne HTTP 429
- Le header `Retry-After` dans la réponse 429 : ajouter `-v` à curl pour le voir

Manipulation complémentaire — modifier `api/limiter.py` pour passer de 30 à 10 req/min, relancer le burst. Il doit voir le 429 apparaître plus tôt. Cela solidifie la compréhension que la limite est un paramètre, pas une valeur magique.

Point à faire remarquer : en production raisonnable, 60 req/min pour un utilisateur authentifié est une valeur courante. 30 req/min est conservateur — adapté à un MVP en phase bêta.

Conseil de gestion du temps : si un élève est en avance, lui faire ajouter `-v` pour voir les headers complets. S'il est en retard, passer directement au checkpoint.

### Checkpoint 1 (5-8 min)

```bash
python ateliers/atelier-05-deploiement/checkpoints/check_1.py
```

Le script pose 3 questions à l'écrit et évalue les mots-clés dans la réponse. Score minimum pour passer : 2/3.

Questions posées :
1. Rôle du `@app.middleware("http")` sur `prompt_injection_filter`
2. Comportement du rate limiter à 10 req/min avec 15 requêtes en 20 secondes (doit mentionner HTTP 429 à partir de la 11e)
3. Différence entre `allow_origins=["*"]` et `allow_origins=["http://localhost:8501"]`

Si un élève échoue : ne pas sauter le checkpoint. Le faire relire les deux fichiers (`api/main.py` et `api/limiter.py`) et refaire le quiz à l'oral. Le checkpoint oral est valide.

### Etape 2 — Langfuse (30 min)

Pré-requis : les 3 variables dans `.env` sont renseignées (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`).

Après modification du `.env`, l'API doit être relancée (Ctrl+C puis `uvicorn api.main:app --port 8000 --reload`).

Envoyer 3 requêtes de test :

```bash
for i in 1 2 3; do
  curl -s -X POST http://localhost:8000/chat \
    -H 'Content-Type: application/json' \
    -d '{"message":"Quelle est la marque de ma chaudière ?","mode":"rag_only"}' > /dev/null
done
```

Attendre 10 à 15 secondes, puis ouvrir `cloud.langfuse.com` > projet > Traces. L'élève doit voir 3 traces avec : modèle utilisé, latence, nombre de tokens en entrée et sortie.

Si les traces n'apparaissent pas après 30 secondes :
1. Vérifier que l'API a bien été relancée après modification du `.env`
2. Vérifier que `LANGFUSE_HOST` est bien `https://cloud.langfuse.com` (sans slash final)
3. Vérifier que les clés sont copiées sans espace avant ou après
4. Regarder les logs de l'API dans Terminal 1 — une erreur Langfuse s'affiche souvent en rouge

Mesure de l'overhead Langfuse : désactiver temporairement les traces en commentant `LANGFUSE_PUBLIC_KEY` dans `.env`, relancer l'API, mesurer la latence sur 5 requêtes, comparer. L'overhead est typiquement 50-150ms (envoi asynchrone des traces en arrière-plan). C'est négligeable en production.

### Bug Hunt (20 min)

Les 3 bugs doivent être appliqués et réparés dans l'ordre. Ne jamais appliquer le suivant sans avoir réparé le précédent.

**Avant de montrer comment appliquer un patch**, demander à l'élève : "Avant de voir le code, imagine quel type de bug pourrait exposer la clé API dans la réponse. Quelle partie du code toucherais-tu ?"

Cette formulation d'hypothèse avant lecture est non-optionnelle — c'est ce qui transforme le Bug Hunt en exercice de raisonnement plutôt qu'en copier-coller.

#### Bug v1 — Clé API dans la réponse JSON

```bash
git apply ateliers/atelier-05-deploiement/bugs/v1.patch
pytest ateliers/atelier-05-deploiement/bugs/test_v1.py -v
```

Le test ECHOUE (le bug est actif). C'est le comportement attendu.

Ce que le patch fait : il ajoute `api_key: str = ""` dans le modèle Pydantic `ChatResponse` et peuple ce champ avec `api_key=os.getenv("ANTHROPIC_API_KEY", "")` dans le constructeur de réponse. Chaque appel `/chat` retourne la clé Anthropic en clair dans le JSON.

Pour voir le bug en action :
```bash
curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"test","mode":"llm_only"}' | python3 -m json.tool
```

La réponse JSON contient un champ `api_key` avec la valeur `sk-ant-...`.

Correction : retirer le champ `api_key` du modèle `ChatResponse` et l'argument correspondant dans le constructeur.

Après correction, relancer le test — il doit passer (PASS).

Point pédagogique à insister : HTTPS ne protège pas contre ce type de fuite. HTTPS chiffre le transport, mais une fois la réponse reçue par le navigateur ou le client, le JSON est en clair. N'importe quel outil (curl, Postman, onglet Network des DevTools) l'affiche en clair.

#### Bug v2 — CORS wildcard

```bash
git apply ateliers/atelier-05-deploiement/bugs/v2.patch
pytest ateliers/atelier-05-deploiement/bugs/test_v2.py -v
```

Ce que le patch fait : il remplace la whitelist d'origines par `allow_origins=["*"]` dans la configuration CORSMiddleware de `api/main.py`.

Correction : restaurer `allow_origins=["http://localhost:8501", "http://localhost:3000"]`.

Point pédagogique essentiel : CORS est une protection des navigateurs, pas des serveurs. Un script `curl` ou Python n'est pas concerné par CORS — l'attaquant peut appeler l'API directement. CORS protège contre les attaques depuis le navigateur d'un utilisateur authentifié (CSRF via CORS). C'est pour ça que `*` est dangereux même sur un endpoint avec authentification par cookie.

Analogie : "La règle CORS, c'est le vigile qui vérifie d'où viennent les visiteurs. Sans règle, n'importe quel site malveillant peut envoyer des requêtes depuis le navigateur de tes utilisateurs, avec leurs cookies de session."

#### Bug v3 — Absence de timeout

```bash
git apply ateliers/atelier-05-deploiement/bugs/v3.patch
pytest ateliers/atelier-05-deploiement/bugs/test_v3.py -v
```

Ce que le patch fait : il remplace `timeout=30.0` par `timeout=None` dans `asyncio.wait_for()` dans la fonction `_call_llm_only`.

Correction : restaurer `timeout=30.0`.

Point pédagogique à bien expliquer : FastAPI utilise un pool de workers. Avec `timeout=None`, si Anthropic est lent ou si le réseau flanche, le worker FastAPI attend indéfiniment. Avec 4 workers et 5 requêtes simultanées qui pendent, le serveur est complètement paralysé — aucune nouvelle requête ne peut être traitée.

La métrique qui révèle ce problème en production : p95 très élevé (ex: p95=45s alors que p50=2s). C'est le signe que 5% des requêtes pendent sans timeout.

Distinction importante à faire comprendre : le timeout côté client (ex: `httpx.AsyncClient(timeout=30)`) protège le client — il abandonne après 30s. Mais le serveur continue d'attendre. Il faut un timeout côté serveur pour libérer le worker.

### Mesure (15 min)

L'élève mesure p50 et p95 par mode de requête. La commande est dans le guide élève. Les valeurs typiques à observer :
- llm_only : p50 ≈ 2s, p95 ≈ 5s
- rag_only : p50 ≈ 3s, p95 ≈ 8s (retrieval + LLM)
- agent : p50 ≈ 10s, p95 ≈ 30s (plusieurs appels LLM en chaîne)

Si un élève obtient des valeurs très différentes de ces estimations, plusieurs causes possibles :
- Réseau lent vers Anthropic (latence variable selon l'heure)
- Modèle Ollama local (plus lent que Claude API pour les machines sans GPU)
- Index FAISS non chargé en cache (premier appel lent, puis normal)

Faire remplir le tableau de métriques dans le guide élève avant de passer au checkpoint final.

### Checkpoint final (10 min)

```bash
python ateliers/atelier-05-deploiement/checkpoints/check_final.py
```

5 questions, minimum 3/5 pour passer. Questions portant sur :
1. Utilités de Langfuse en production (coûts, dérives, alertes, replay de sessions)
2. Avantage du header `X-API-Key` vs clé dans l'URL (les URL sont loggées partout)
3. RGPD et PII dans les logs Langfuse (scrubbing avant envoi)
4. Rate limiting par IP vs par userId authentifié
5. Interprétation de p50=2s / p95=45s

Lecture du score :
- 80% ou plus (4-5/5) : direction le Bonus
- 60-79% (3/5) : choisir entre Sprint et Bonus selon le temps restant
- Moins de 60% (moins de 3/5) : Sprint obligatoire

---

## 4. Bug Hunt — ce qui se passe concrètement

Cette section détaille le comportement observable pour chaque bug, pour que tu puisses guider un élève sans révéler la solution.

### Bug v1 en action

Après application du patch, un `curl` sur `/chat` retourne quelque chose comme :

```json
{
  "response": "Pour votre chaudière, je recommande...",
  "mode": "llm_only",
  "sources": [],
  "api_key": "sk-ant-api03-AbCdEfGh..."
}
```

L'élève voit la clé en clair dans le terminal. Ce moment de "oh merde" est pédagogiquement important — ne le court-circuite pas en donnant la solution immédiatement.

Question socratique si l'élève est bloqué : "Quel fichier définit la structure de la réponse JSON ? Quel modèle Pydantic est utilisé pour l'endpoint `/chat` ?"

### Bug v2 en action

Le test `test_v2.py` vérifie que l'API refuse les requêtes CORS depuis une origine non listée. Avec `allow_origins=["*"]`, toutes les origines sont acceptées et le test échoue.

Pour montrer l'effet visuellement : dans un navigateur, n'importe quelle page web peut appeler l'API avec les cookies de l'utilisateur. En pratique, cela se manifeste surtout avec les erreurs CORS bloquées côté navigateur (onglet Console des DevTools).

Question socratique : "Cherche `CORSMiddleware` dans `api/main.py`. Que voit-on dans le paramètre `allow_origins` ?"

### Bug v3 en action

Le test `test_v3.py` injecte un mock de LLM qui tarde intentionnellement. Sans timeout, le test attend (et finit par déclencher un timeout du test lui-même, ce qui est un signe révélateur). Avec `timeout=30.0`, le test valide que l'API retourne une erreur propre après 30 secondes.

Pour illustrer l'effet en production sans avoir à attendre 30 secondes, explique l'analogie : "Imagine 4 caisses dans un supermarché. Si 4 clients ont des problèmes de carte bancaire et que les caissiers attendent indéfiniment — tous les clients suivants attendent dans la file. C'est exactement ce qui se passe avec les workers FastAPI."

Question socratique : "Cherche `asyncio.wait_for` dans le code. Quel est le paramètre `timeout` ?"

### Après chaque bug

Faire lire le fichier `bugs/v[N]_explanation.md`. Ces fichiers contiennent des affirmations Vrai/Faux. L'élève répond d'abord, puis lit les corrections commentées. Ce format force la réflexion plutôt que la lecture passive.

Ne pas sauter cette étape même si le temps presse. Les affirmations Vrai/Faux contiennent les misconceptions les plus fréquentes (HTTPS protège contre les fuites de données, le timeout client suffit, CORS n'est utile que sans authentification...).

---

## 5. Checkpoints — comment les animer

### check_1.py — 3 questions sur la sécurité API

Le script est interactif : il attend une réponse textuelle et cherche des mots-clés. Un élève qui écrit des réponses très courtes peut passer avec des mots-clés si ses formulations sont précises. A l'inverse, une longue réponse sans les mots-clés attendus échoue.

Comment l'animer : laisse l'élève taper seul, puis discute les explications que le script affiche après chaque question. Ce n'est pas un examen — c'est un point de vérification de compréhension.

Si l'élève échoue à la question sur CORS (question 3) : c'est fréquent. Demande-lui de t'expliquer ce qui se passe quand un navigateur charge `evil-site.com` et que ce site fait une requête vers `localhost:8000`. Cette reformulation concrète débloque généralement la compréhension.

### check_final.py — 5 questions sur sécurité et observabilité

Ce checkpoint est plus difficile. Les questions portent sur des nuances (header vs URL, RGPD, rate limiting par userId).

Question 3 (RGPD + PII) : si l'élève n'a pas fait le défi B2 du Bonus, il peut manquer de vocabulaire sur le scrubbing. Indice acceptable : "Dans le défi Bonus sur Langfuse, il y avait une fonction à implémenter qui remplaçait des données personnelles. Tu te rappelles son nom ?"

Question 5 (p95=45s) : si l'élève ne voit pas le lien avec le bug v3, rappelle-lui ce qui se passe avec `timeout=None` et un LLM lent. La p95 élevée est précisément le signal d'alerte d'un bug de timeout non corrigé.

Gestion du résultat :
- 4-5/5 : félicite franchement et oriente vers le Bonus. Les 60-70 minutes de Bonus sur le streaming SSE ou le scrubbing PII sont très formateurs.
- 3/5 : discute les 2 questions ratées, vérifie que l'élève comprend les corrections, puis laisse-le choisir.
- Moins de 3/5 : Sprint obligatoire. Rassure l'élève — le Sprint n'est pas une punition, c'est une consolidation. Les 3 étapes du Sprint (valider l'injection, valider le rate limit, relire `test_securite.sh`) prennent 30 minutes et couvrent l'essentiel.

---

## 6. Questions fréquentes

### "CORS, c'est vraiment important sur une API interne ?"

Oui. Même sur un réseau interne, si des utilisateurs accèdent à l'API depuis leur navigateur, CORS s'applique. Une page web malveillante (publicité injectée, extension de navigateur compromise) peut appeler l'API en se faisant passer pour l'utilisateur. La règle : une whitelist explicite des origines que tu contrôles, toujours.

### "Comment voir les traces Langfuse ?"

Ouvrir `cloud.langfuse.com`, se connecter, cliquer sur le projet HomeButler, puis "Traces" dans le menu de gauche. Les traces apparaissent avec un délai de 10 à 30 secondes après l'appel API. Chaque trace montre : le prompt envoyé, la réponse, le modèle, la latence, les tokens consommés et le coût estimé.

### "test_securite.sh ne tourne pas"

Deux causes possibles :
1. L'API n'est pas démarrée sur le port 8000. Vérifier avec `curl http://localhost:8000/health`.
2. `curl` n'est pas installé. Sur Mac, c'est préinstallé. Sur certaines VMs Windows, vérifier avec `which curl` ou `curl --version`.

Si les deux points sont OK et que le script échoue encore, regarder le code de retour HTTP de la première requête : `curl -v -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{"message":"test","mode":"llm_only"}'`

### "Pourquoi langfuse<4.0.0 dans les requirements ?"

L'API de Langfuse v4 a changé `update_trace()` de façon incompatible avec les projets LangChain basés sur le `CallbackHandler`. Le changement d'API Langfuse n'est pas documenté dans le guide élève intentionnellement — c'est le genre de contrainte de versionnage qu'on rencontre en production. Si un élève demande "pourquoi on ne met pas à jour ?", c'est une bonne opportunité de parler de la gestion des dépendances et du pinning.

### "Je peux utiliser Ollama à la place d'Anthropic ?"

Oui, c'est le switch prévu par la variable `LLM_PROVIDER=ollama` dans `.env`. L'abstraction est dans `homebutler/llm/provider.py` — `get_llm()` lit la variable à chaque appel. Les latences seront différentes (généralement plus lentes sur Mac sans GPU) et les réponses de qualité variable selon le modèle chargé.

### "Pourquoi `pip install -e .` est obligatoire ?"

Streamlit ne peut pas faire d'imports relatifs. Il a besoin que `homebutler` soit un package installé dans le venv, accessible par son nom depuis n'importe quel répertoire. `pip install -e .` installe le package en mode "editable" — le code source reste dans le répertoire mais Python peut l'importer comme un package normal. Sans ça, `from homebutler.rag.ingestion import ...` échoue avec `ModuleNotFoundError`.

### "Le test du Bug Hunt passe même sans ma correction, c'est normal ?"

Non. Si un test passe alors que le bug est censé être actif, c'est que soit le patch ne s'est pas appliqué correctement (`git status` pour vérifier), soit le test a un problème. Faire vérifier avec `git diff api/main.py` pour confirmer que le patch est bien présent dans le code.

---

## 7. Signaux d'alerte (élève bloqué)

### Bloqué sur l'étape 1 — ne comprend pas le middleware

Signal : l'élève lit le code mais ne peut pas expliquer la différence entre middleware et router.

Intervention : demande-lui de localiser une route (`@router.post("/chat")`) et le middleware (`@app.middleware("http")`), puis de tracer mentalement le chemin d'une requête POST. "La requête arrive. Elle passe d'abord par quoi ?" Cette mise en séquence visuelle débloque généralement.

Si ça ne suffit pas : l'analogie du videur de boite de nuit. "Le middleware vérifie l'injection avant de laisser passer vers la route. Sans middleware, la vérification serait dans chaque route — tu devrais la copier-coller partout."

### Bloqué sur Langfuse — traces invisibles

Signal : l'élève a configuré `.env`, relancé l'API, envoyé des requêtes, mais rien n'apparaît sur le dashboard.

Checklist à parcourir avec lui :
1. `grep LANGFUSE_PUBLIC_KEY .env` — la clé est présente ?
2. Les logs de Terminal 1 montrent-ils une erreur Langfuse au démarrage ?
3. L'API a-t-elle été relancée APRÈS la modification du `.env` ?
4. Le projet Langfuse est-il bien sélectionné sur le dashboard ?

Très souvent, c'est le point 3 (API non relancée). `uvicorn` avec `--reload` recharge le code Python mais pas les variables d'environnement — il faut arrêter et relancer.

### Bloqué sur le Bug Hunt — ne trouve pas la correction

Signal : l'élève a vu le test échouer mais ne sait pas quoi modifier.

Intervention progressive :
1. "Formule une hypothèse : quel comportement as-tu observé ?"
2. "Dans quel fichier ce comportement est-il codé ?"
3. "Cherche le champ qui ne devrait pas exister dans `ChatResponse`." (pour v1)
4. "Cherche `allow_origins` dans `api/main.py`." (pour v2)
5. "Cherche `asyncio.wait_for` et regarde le paramètre `timeout`." (pour v3)

Ne jamais sauter directement à l'étape 5. Le cheminement est l'apprentissage.

### En avance — a tout fini avant la fin du tronc commun

Signal : l'élève a fini les 5 étapes du tronc commun et le checkpoint final en moins de 1h30.

Orientation :
- Défi B1 (streaming SSE) : techniquement exigeant, bon pour les élèves avec une forte base FastAPI
- Défi B2 (scrubbing PII) : bon pour les élèves intéressés par la conformité RGPD
- Si les deux défis sont faits : demander de rédiger les réponses au quiz oral des 10 questions du Wrap-up

### Score final < 60%

Ne pas faire passer l'élève au Bonus. Le Sprint (30 min) couvre les deux points fondamentaux de l'atelier. L'élève qui rate le checkpoint final sur les 5 questions a généralement mal compris soit le rate limiting, soit Langfuse, soit le CORS. Le Sprint remplace la profondeur par la consolidation des bases.

---

## 8. Transition vers l'atelier 06

A la fin de l'atelier 05, l'élève a une API fonctionnelle, sécurisée et observable. C'est le bon moment pour anticiper la question qui va se poser en atelier 06.

Phrase de transition : "On a maintenant une API qui répond, qui est protégée, et dont on voit le comportement dans Langfuse. La prochaine question est : nos réponses sont-elles bonnes ? Et est-ce que le RAG est vraiment meilleur qu'un LLM sans contexte ? C'est ce qu'on mesure dans l'atelier 06."

Ce qu'il ne faut pas faire maintenant :
- Activer `ENABLE_COMPARE_ROUTES=true` dans `.env` (les routes ne sont pas finies pour cet atelier)
- Montrer les routes `/rag/evaluate` ou `/chat/compare` dans Swagger
- Lancer une comparaison llm_only vs rag_only à la main — l'élève n'a pas encore les outils d'évaluation rigoureuse

Ce que tu peux faire pour amorcer l'atelier 06 :
- Demander à l'élève de noter dans son carnet : "En mode llm_only, ma chaudière s'appelle comment ? Et en mode rag_only ?" La réponse llm_only va halluciner une marque. La réponse rag_only va citer Viessmann Vitodens 100-W avec les sources. Cette observation en direct est le meilleur teaser pour l'atelier 06.
- La transition se fait sur la branche `atelier/06-finetune-vs-rag` : `git checkout atelier/06-finetune-vs-rag`
