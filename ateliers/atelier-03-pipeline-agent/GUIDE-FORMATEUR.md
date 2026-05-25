# GUIDE FORMATEUR — Atelier 03 : Pipeline Agent ReAct (3h)

> Document interne formateur. Ne pas distribuer aux élèves.
> Branche : `atelier/03-pipeline-agent`
> Positionnement : Jour 2, matin — après l'atelier 02 (RAG FAISS seul) et avant l'atelier 04 (évaluation RAG).

---

## 1. Ce que l'élève doit comprendre à la fin

L'atelier 03 est le pivot technique de la formation. L'élève passe d'un RAG passif (on interroge un index, on récupère des chunks, on génère) à un agent actif (le LLM décide lui-même quels outils appeler, dans quel ordre, combien de fois).

À la fin, l'élève doit pouvoir expliquer sans hésiter :

**Sur l'EnsembleRetriever :** pourquoi combiner FAISS et ChromaDB plutôt que choisir l'un ou l'autre. FAISS cherche par similarité sémantique (vectors denses) ; ChromaDB complète avec la capacité de filtrer par métadonnées (type de document, pièce, date). L'ensemble améliore le recall sur des questions qui croisent plusieurs sources. Les poids `[0.6, 0.4]` signifient que FAISS pèse 60% dans le score de fusion final — ce n'est pas un quota de documents, c'est une pondération de pertinence.

**Sur la boucle ReAct :** un agent ne répond pas directement. Il raisonne (Thought), choisit un outil (Action), lit le résultat (Observation), puis recommence jusqu'à avoir assez d'informations pour produire une réponse finale. C'est une boucle, pas un pipeline linéaire.

**Sur les descriptions d'outils :** la description n'est pas un commentaire de code pour le développeur — c'est le contrat que le LLM lit à chaque tour pour décider quel outil appeler. Une description vague entraîne un outil ignoré ou mal utilisé.

**Sur `max_iterations` :** c'est le disjoncteur. Sans lui, un agent qui hallucine ses observations peut boucler indéfiniment et coûter cher en appels API. La valeur 8 est un compromis : suffisante pour orchestrer 3 à 4 outils avec quelques retries, assez basse pour couper une boucle pathologique rapidement.

**Sur la mémoire :** `ConversationBufferWindowMemory(k=6)` garde les 6 derniers tours de dialogue (6 messages utilisateur + 6 réponses agent). Avec `k=0`, chaque question est traitée sans contexte. Avec `k=6`, l'agent retrouve une information donnée deux échanges plus tôt.

---

## 2. Setup formateur — avant l'atelier

### Vérifier la branche

```bash
git checkout atelier/03-pipeline-agent
git status
```

S'assurer qu'aucun patch n'est appliqué (les fichiers `bugs/` doivent être intacts). Si l'état est incertain après une session précédente :

```bash
git checkout -- .
```

### Vérifier l'environnement Python

```bash
source .venv/bin/activate
python -c "import langchain; import chromadb; import faiss; print('OK')"
```

Si une des importations échoue, lancer :

```bash
pip install -r requirements_atelier03.txt
pip install -e .
```

Le package `chromadb` doit être en version >= 1.0.15. Les versions antérieures génèrent des warnings de télémétrie qui parasitent la lisibilité en formation. Vérifier également que `.env` contient `ANONYMIZED_TELEMETRY=false` et `ANTHROPIC_API_KEY` valide.

### Vérifier les index vectoriels

Les deux index doivent être construits avant que les élèves arrivent. C'est l'opération la plus longue du setup (2 à 5 minutes selon la machine).

```bash
# Index FAISS
python -c "from homebutler.rag.ingestion import ingest_all_documents; \
           from homebutler.rag.vectorstore_faiss import build_faiss_index; \
           build_faiss_index(ingest_all_documents(), force_rebuild=True)"

# Index ChromaDB
python -c "from homebutler.rag.ingestion import ingest_all_documents; \
           from homebutler.rag.vectorstore_chroma import build_chroma_db; \
           build_chroma_db(ingest_all_documents())"
```

Vérifier ensuite que les répertoires `data/faiss_index/` et `data/chroma_db/` existent et ne sont pas vides. Si les données sources n'ont pas encore été générées :

```bash
python scripts/generate_documents.py
python scripts/generate_energy_data.py
python scripts/generate_producers.py
python scripts/preload_models.py
```

Puis reconstruire les index.

### Test de smoke avant la session

```bash
python ateliers/atelier-03-pipeline-agent/exercice.py
```

Ce script doit lever `NotImplementedError: TODO 1 — construire l'EnsembleRetriever`. C'est le comportement attendu pour un élève en début d'atelier. Si une autre erreur apparaît (ImportError, FileNotFoundError), investiguer avant de démarrer.

### Lancer la solution pour vérifier que tout tourne

```bash
python ateliers/atelier-03-pipeline-agent/solution.py
```

Cette exécution doit afficher la trace ReAct avec au moins 3 outils distincts appelés et une réponse finale cohérente. Si des erreurs `429` (rate limit Anthropic) apparaissent, configurer `LLM_PROVIDER=ollama` dans `.env` comme fallback.

---

## 3. Déroulé détaillé

### Budget temps

| Phase | Durée | Contenu |
|---|---|---|
| Tronc commun | 1h40 | EnsembleRetriever + mini-lab + Tools + ReAct + Bug Hunt + Mesure |
| Sprint | 30 min | Rattrapage pour les élèves < 60% au checkpoint final |
| Bonus | 60-70 min | Défis avancés pour les élèves >= 80% |

Sprint et Bonus sont mutuellement exclusifs. Si un élève est en retard sur le tronc commun à 1h45, l'orienter directement vers le Sprint sans culpabilité — c'est prévu.

### Etape 1 — EnsembleRetriever (25 min)

**Ce que l'élève fait :** il ouvre `exercice.py`, décommente le TODO 1, importe `get_ensemble_retriever` depuis `homebutler.rag.retriever`, construit le retriever avec `faiss_k=4, chroma_k=3`, et vérifie qu'il retourne des chunks fusionnés.

**Ce que vous surveillez :** la confusion fréquente entre `faiss_k` (nombre de chunks demandés à FAISS) et `ensemble_weights` (poids dans la fusion). Ce ne sont pas la même chose. `faiss_k=4` dit "récupère 4 chunks de FAISS avant de fusionner" ; `ensemble_weights=[0.6, 0.4]` dit "quand tu fusionnes, FAISS pèse 60%".

**Message à passer :** ChromaDB n'est pas "meilleur" que FAISS, il est complémentaire. FAISS est excellent pour trouver des documents sémantiquement proches. ChromaDB permet en plus de filtrer par métadonnées — par exemple "cherche uniquement dans les documents de type chaudière". L'ensemble améliore le recall sur des questions qui croisent plusieurs sources.

**Commandes de référence :**

```bash
git checkout atelier/03-pipeline-agent
source .venv/bin/activate
python ateliers/atelier-03-pipeline-agent/exercice.py
```

### Checkpoint 1 (5 min max)

```bash
python ateliers/atelier-03-pipeline-agent/checkpoints/check_1.py
```

3 questions QCM sur EnsembleRetriever, les poids et l'apport de ChromaDB. Le seuil de passage est 2/3. Si l'élève est à 1/3, lui demander de relire la section "EnsembleRetriever" du carnet de bord dans `GUIDE-ELEVE.md` avant de continuer. Ne pas passer à l'étape 2 sans ce minimum.

### Mini-lab EnsembleRetriever vs FAISS seul (15 min)

L'élève fait varier `ensemble_weights` et mesure le Recall@5 sur la question test multi-source. Le but n'est pas d'obtenir le meilleur score absolu — c'est de comprendre que les poids ont un impact concret et mesurable.

La configuration `[1.0, 0.0]` est utile comme baseline : avec ce réglage, l'EnsembleRetriever se comporte exactement comme FAISS seul. C'est le point de comparaison.

Si des élèves finissent tôt, les inviter à explorer `faiss_k` et `chroma_k` selon le tableau du guide élève.

### Etape 2 — Tools et agent ReAct (30 min)

**Ce que l'élève fait :** il décommente les TODO 2, 3 et 4 dans `exercice.py`. Il importe les 4 outils, les passe à `create_react_agent`, configure `AgentExecutor` avec `max_iterations=8` et `return_intermediate_steps=True`, puis lance la question multi-outils.

**Commandes de référence :**

```bash
python ateliers/atelier-03-pipeline-agent/exercice.py
# Interface Gradio (optionnel, pour visualiser la trace)
python ateliers/atelier-03-pipeline-agent/gradio_demo.py
```

La demo Gradio affiche la trace Thought/Action/Observation dans une colonne séparée. Utile pour les élèves visuels ou ceux qui ont du mal à lire les logs CLI. L'interface est accessible à `http://127.0.0.1:7860`.

**Ce que vous surveillez :** l'élève doit voir la trace s'afficher dans le terminal avec `verbose=True`. Si rien ne s'affiche, vérifier que `verbose=True` est bien passé à `AgentExecutor` et non à `create_react_agent`.

**Message clé sur `return_intermediate_steps` :** sans ce paramètre, la clé `intermediate_steps` n'est pas dans le résultat. L'élève peut construire un agent fonctionnel sans l'activer, mais il ne pourra pas inspecter la trace. C'est intentionnel dans le TODO 4 — forcer l'élève à activer explicitement la transparence.

### Bug Hunt (20 min)

Les 3 bugs sont appliqués et réparés un par un. L'ordre est imposé : v1, v2, v3. Ne pas sauter.

**Règle anti-cheat à rappeler avant de commencer :** l'élève formule une hypothèse sur le comportement observé AVANT de lire le patch. Cette étape est pédagogiquement essentielle — c'est le moment où l'élève construit un modèle mental du système. Si l'élève saute directement à la lecture du patch, il apprend la réponse, pas le raisonnement.

Voir la section 4 pour le détail complet de chaque bug.

### Mesure (15 min)

L'élève remplit le tableau de métriques dans son carnet de bord. Le test mémoire mérite une attention particulière : l'élève doit poser "Ma chaudière est une Viessmann, note ça." au tour 1, deux autres questions au tour 2 et 3, puis "Et tu m'as dit quoi sur ma chaudière ?" au tour 4. Avec `k=0`, l'agent ne retrouve pas. Avec `k=6`, il retrouve. Si le résultat ne correspond pas à cette prédiction, c'est un point de discussion utile sur la configuration réelle.

### Checkpoint final (5 min max)

```bash
python ateliers/atelier-03-pipeline-agent/checkpoints/check_final.py
```

5 questions QCM sur ReAct, les descriptions d'outils, `max_iterations`, la mémoire. Le seuil Bonus est 4/5. Le seuil Sprint est 3/5 (ou moins). Entre 3 et 4, l'élève peut aller en Bonus "avec prudence" — lui conseiller de relire les explications des questions ratées avant.

---

## 4. Bug Hunt — ce qui se passe concrètement

### Bug v1 — Description d'outil trop vague

**Ce qui a changé :** la description de `search_docs_tool` a été remplacée par "cherche des documents" (5 mots sans contexte).

**Comportement observable :** l'agent ReAct construit son prompt de raisonnement en incluant la liste complète des outils avec leurs descriptions. Avec une description aussi vague, le LLM ne sait pas quand appeler cet outil plutôt qu'un autre. Résultat : l'outil est ignoré même pour des questions directement liées aux documents du logement (notices, bail, DPE). L'agent peut aussi l'appeler avec des inputs mal formés car il ne sait pas quel format est attendu.

**Comment appliquer et tester :**

```bash
git apply ateliers/atelier-03-pipeline-agent/bugs/v1.patch
pytest ateliers/atelier-03-pipeline-agent/bugs/test_v1.py -v
```

Le test vérifie que `search_docs_tool` est absent des `tools_used` sur une question qui devrait le déclencher.

**Comment corriger :** restaurer la description complète qui mentionne (a) le domaine couvert (bail, notices, équipements, DPE), (b) quand utiliser l'outil ("pour toute question sur le fonctionnement d'un équipement, les règles du bail, les caractéristiques du logement"), (c) le format de l'input ("Input : question ou mots-clés en français").

**Nettoyer après correction :**

```bash
git checkout -- .
```

**Message pédagogique :** 80% des cas où un agent ignore un outil viennent d'une description insuffisante. La description est le seul canal de communication entre le développeur et le LLM sur la sémantique de l'outil. Ce n'est pas de la documentation — c'est du code fonctionnel.

### Bug v2 — Trop d'outils (> 7)

**Ce qui a changé :** 10 outils fictifs ont été ajoutés à la liste `ALL_TOOLS`, portant le total à 14.

**Comportement observable :** à chaque tour de la boucle ReAct, le LLM reçoit dans son prompt la liste complète des outils avec leurs descriptions. Avec 14 outils, le prompt d'agent devient très long. Le LLM commence à halluciner des noms d'outils qui n'existent pas, produit plus de steps inutiles, et dépasse plus facilement `max_iterations`. La latence augmente mécaniquement car chaque description supplémentaire alourdit le prompt.

**Comment appliquer et tester :**

```bash
git apply ateliers/atelier-03-pipeline-agent/bugs/v2.patch
pytest ateliers/atelier-03-pipeline-agent/bugs/test_v2.py -v
```

**Comment corriger :** supprimer les 10 outils fictifs. Garder uniquement les 4 outils métier : `search_docs_tool`, `analyze_energy_tool`, `find_products_tool`, `get_weather_tool`.

**Nettoyer après correction :**

```bash
git checkout -- .
```

**Message pédagogique :** un agent n'est pas plus capable parce qu'il a plus d'outils. Le nombre optimal pour un agent ReAct est entre 1 et 7. Au-delà, la confusion augmente. Si le besoin réel dépasse 7 fonctionnalités, la solution est de créer plusieurs agents spécialisés avec un routeur, pas d'empiler des outils dans un seul agent.

### Bug v3 — `max_iterations` absent

**Ce qui a changé :** le paramètre `max_iterations=8` a été retiré de l'appel à `AgentExecutor(...)`.

**Comportement observable :** LangChain 0.3.x a une valeur par défaut de 15 itérations. Mais si le LLM produit des observations hallucingées ou des formats de réponse incorrects en boucle, l'agent peut dépasser même cette limite. Chaque itération est un appel API supplémentaire — sur des questions où l'agent ne converge pas, le coût peut exploser. L'utilisateur attend sans réponse ou reçoit une réponse partielle après un long délai.

**Comment appliquer et tester :**

```bash
git apply ateliers/atelier-03-pipeline-agent/bugs/v3.patch
pytest ateliers/atelier-03-pipeline-agent/bugs/test_v3.py -v
```

**Comment corriger :** restaurer `max_iterations=8` dans `AgentExecutor(...)`.

**Nettoyer après correction :**

```bash
git checkout -- .
```

**Message pédagogique :** `max_iterations` et `handle_parsing_errors=True` sont deux mécanismes complémentaires, pas redondants. `handle_parsing_errors` gère les erreurs de format LLM sur une itération en évitant le crash. `max_iterations` plafonne le nombre total de tours quelle que soit la cause. Supprimer l'un n'est pas compensé par l'autre.

---

## 5. Checkpoints — comment les animer

### Checkpoint 1 — EnsembleRetriever / ChromaDB / Hybrid Search

3 questions QCM, seuil de passage 2/3. Le script est interactif : l'élève tape sa réponse dans le terminal.

**Comment animer :** lancer le script ensemble, lire chaque question à voix haute, laisser 30 secondes de réflexion avant que chaque élève tape sa réponse. Ne pas commenter les réponses avant que tout le groupe ait répondu. Après la correction automatique, reprendre les questions ratées par le plus grand nombre en posant des questions socratiques plutôt qu'en donnant la réponse directe.

Questions de recadrage utiles :
- Sur la question des poids : "Si tu mets `[1.0, 0.0]`, qu'est-ce qui se passe avec la partie ChromaDB ?" (réponse attendue : elle est ignorée, c'est FAISS seul)
- Sur l'apport de ChromaDB : "Imagine que tu cherches 'tous les documents sur la chaudière' — lequel des deux retrievers te permet de filtrer par type de document ?" (réponse attendue : ChromaDB, via les métadonnées)

### Checkpoint final — ReAct / Tools / Mémoire / max_iterations

5 questions QCM, seuil Bonus 4/5, seuil Sprint inférieur à 3/5. Même mode d'animation que le checkpoint 1.

**Aiguillage :**
- 4 ou 5 bonnes réponses : orienter vers le Bonus sans attendre. L'élève est prêt.
- 3 bonnes réponses : lui proposer 5 minutes pour relire les explications des questions ratées, puis le laisser choisir. Les deux chemins sont viables.
- 2 bonnes réponses ou moins : Sprint obligatoire. Le cadrer positivement — le Sprint est conçu pour consolider les fondamentaux avant l'atelier 04, pas pour rattraper un retard honteux.

**Questions de recadrage si l'élève rate la question sur les descriptions d'outils :** "Quand tu appelles une API externe, tu lis la documentation pour savoir quoi lui envoyer. Pour un outil LangChain, c'est pareil — mais le lecteur de la doc, c'est le LLM, pas toi."

**Questions de recadrage si l'élève rate la question sur `max_iterations` :** "Qu'est-ce qui se passe si un agent pose une question à un outil, l'outil répond n'importe quoi, et l'agent re-pose la même question ? Sans garde-fou, combien de fois ça peut se répéter ?"

---

## 6. Questions fréquentes

**"Pourquoi l'agent n'utilise pas le bon outil ?"**

La cause la plus fréquente est une description d'outil insuffisante ou ambiguë. Le LLM lit ces descriptions à chaque tour pour prendre sa décision. Une description vague ("cherche des documents") ne lui permet pas de distinguer cet outil d'un autre. La deuxième cause est un trop grand nombre d'outils — le LLM se perd dans le choix. Commencer par vérifier les descriptions des outils non utilisés.

**"C'est quoi `intermediate_steps` exactement ?"**

C'est la trace complète du raisonnement de l'agent : une liste de tuples `(AgentAction, observation)`. Chaque `AgentAction` contient le nom de l'outil appelé (`action.tool`) et l'input passé (`action.tool_input`). L'observation est le retour de l'outil. En activant `return_intermediate_steps=True` dans `AgentExecutor`, cette information est accessible dans le dictionnaire retourné par `executor.invoke(...)`. Sans ce paramètre, la clé n'est pas présente dans le résultat.

**"Comment voir la trace ReAct en live ?"**

Deux façons. La première : `verbose=True` dans `AgentExecutor` affiche la trace dans le terminal à mesure que l'agent tourne. La deuxième : `return_intermediate_steps=True` expose la trace après exécution, que l'on peut afficher comme on veut. La démo Gradio (`gradio_demo.py`) utilise la deuxième approche et formate la trace en Markdown dans une colonne séparée.

**"Pourquoi on ne met pas `temperature=0` pour l'agent ?"**

Avec `temperature=0`, l'agent est déterministe mais rigide. Si la première stratégie de raisonnement échoue, il risque de ne pas explorer d'alternatives. Une température basse (0.1) donne un peu de flexibilité tout en restant cohérent. La valeur exacte n'est pas critique — c'est l'ordre de grandeur qui compte.

**"Est-ce que `handle_parsing_errors=True` remplace `max_iterations` ?"**

Non. Ce sont deux mécanismes complémentaires. `handle_parsing_errors=True` intercepte les erreurs de format de réponse du LLM (quand l'agent produit un texte qui ne respecte pas le format Thought/Action/Observation attendu) et continue l'itération plutôt que de crasher. `max_iterations=8` plafonne le nombre total de tours, quelle que soit la cause de la boucle. Les deux doivent être présents.

**"Qu'est-ce qui se passe quand `max_iterations` est atteint ?"**

L'`AgentExecutor` s'arrête et retourne ce qu'il a trouvé jusqu'ici — une réponse partielle accompagnée d'un warning. Il ne lève pas d'exception par défaut. En production, ce comportement doit être surveillé (via Langfuse ou équivalent) car une réponse partielle peut être présentée à l'utilisateur sans signal visuel d'incomplétude.

**"Pourquoi la mémoire disparaît si on redémarre le script ?"**

`ConversationBufferWindowMemory` est en RAM. C'est une instance Python. Elle n'est pas persistée sur disque par défaut. Si on arrête et relance `exercice.py`, c'est une nouvelle instance — l'historique repart de zéro. En production, la mémoire doit être persistée en base de données (Redis, PostgreSQL) en la sérialisant par `session_id`.

**"L'agent fait des appels à l'API à chaque step — est-ce normal ?"**

Oui. C'est inhérent à ReAct : chaque Thought est un appel LLM. Sur une question qui déclenche 4 outils avec 1 retry, l'agent peut faire 5 à 8 appels API. C'est le coût du raisonnement dynamique. Si les erreurs 429 (rate limit Anthropic) sont fréquentes, configurer `LLM_PROVIDER=ollama` dans `.env` pour basculer sur un modèle local sans limite de rate.

---

## 7. Signaux d'alerte (élève bloqué)

### Blocage technique avant l'étape 1

**Signal :** `ImportError` au lancement d'`exercice.py` ou index manquant.

**Action :** vérifier que `pip install -e .` a bien été exécuté et que les index FAISS et ChromaDB sont construits. Les commandes de construction des index sont dans la section "Setup formateur" de ce guide. En cas de blocage persistant sur ChromaDB, vérifier la version (`pip show chromadb`) et s'assurer qu'elle est >= 1.0.15.

### L'élève décommente tout d'un coup sans comprendre

**Signal :** l'élève copie-colle tous les TODO décommentés en une fois, le script tourne, mais il ne peut pas expliquer ce qui se passe.

**Action :** lui demander de commenter à nouveau la moitié du code et de repartir du TODO 1 seul. Le forcer à lancer le script après chaque TODO pour voir l'état intermédiaire. L'objectif n'est pas d'avoir un script qui tourne — c'est de comprendre ce que fait chaque bloc.

### L'élève est bloqué sur la trace ReAct (ne voit rien)

**Signal :** l'agent tourne et retourne une réponse mais pas de trace Thought/Action/Observation.

**Causes probables :** `verbose=False` dans `AgentExecutor` (ou absent), ou `return_intermediate_steps` non activé. Vérifier l'instanciation de `AgentExecutor` :

```python
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,                     # <-- doit être True
    max_iterations=8,
    handle_parsing_errors=True,
    return_intermediate_steps=True,   # <-- doit être True
)
```

### L'élève est bloqué sur le Bug Hunt (ne voit pas le comportement anormal)

**Signal :** l'élève applique le patch mais dit "ça marche pareil pour moi".

**Action :** lui demander de comparer les `tools_used` pour le bug v1, le nombre d'outils dans la liste pour le bug v2, et le comportement sur une question complexe pour le bug v3. Sur le bug v1, une question directe aide : "Quand tu poses une question sur la chaudière, est-ce que `search_docs_tool` apparaît dans les outils appelés ?" Sinon, afficher `tools_used = [step[0].tool for step in steps]` et compter.

### L'élève est en retard au checkpoint final (< 3/5, plus d'1h45 de tronc commun)

**Signal :** score < 60% et temps dépassé.

**Action :** Sprint obligatoire. Lui proposer l'Option A (lire la solution commentée ligne par ligne en verbose) ou l'Option B (comparer la mémoire avec k=0 vs k=6 sur 3 tours). Les deux options durent 30 minutes et sont calibrées pour consolider les fondamentaux sans nécessiter de nouveau code.

### L'élève pose des questions hors scope (fine-tuning, déploiement API, Streamlit)

**Signal :** questions sur LoRA, FastAPI, RAFT, Streamlit.

**Action :** répondre simplement "C'est couvert dans l'atelier 04 ou 06, concentre-toi ici sur l'agent ReAct et l'EnsembleRetriever." Donner une tâche concrète immédiate pour recadrer l'attention : "Lance le mini-lab avec `ensemble_weights=[0.2, 0.8]` et note le Recall@5."

### L'élève voit des erreurs 429 Anthropic

**Signal :** `anthropic.RateLimitError` dans les logs.

**Action :** l'agent ReAct fait 5 à 10 appels API par question. Sur une VM de formation avec plusieurs élèves qui tournent en même temps, les limites de rate peuvent être atteintes. Solution immédiate : attendre 60 secondes. Solution durable pour la session : ajouter `LLM_PROVIDER=ollama` dans `.env` et vérifier qu'Ollama est lancé.

---

## 8. Transition vers l'atelier 04

L'atelier 03 se termine sur un agent qui fonctionne mais dont la qualité de réponse n'a pas encore été mesurée rigoureusement. L'élève a observé des métriques empiriques (Recall@5 approximatif, nombre de steps, latence) mais sans cadre formel d'évaluation.

L'atelier 04 introduit RAGAS et les métriques d'évaluation RAG : faithfulness, answer relevancy, context recall. C'est le passage de "ça marche" à "comment on sait que ça marche bien".

**Ce que vous pouvez dire en clôture de l'atelier 03 :**

"Vous avez un agent qui orchestre plusieurs sources. Il produit des réponses. Mais comment vous sauriez si sa réponse est fiable ? Comment vous compareriez deux configurations d'agent sans les tester manuellement sur 50 questions ? C'est ce qu'on va construire demain après-midi."

**Points de continuité concrets :**
- L'`EnsembleRetriever` construit ici sera réutilisé tel quel dans les ateliers suivants.
- La trace `intermediate_steps` sera exploitée dans l'atelier 04 pour construire des datasets d'évaluation.
- La question multi-outils ("Il va faire -5°C demain...") est le fil rouge — elle revient dans les ateliers 04, 05 et 06 avec des niveaux de rigueur croissants.

**Remarque sur le timing :** si des élèves ont terminé le Bonus, les inviter à noter dans leur carnet de bord les cas d'usage Merenza identifiés (concierge guest, assistant host admin, onboarding flow) et à prédire quels outils seraient nécessaires dans chaque cas. Ce travail alimente directement la réflexion de l'atelier 06.
