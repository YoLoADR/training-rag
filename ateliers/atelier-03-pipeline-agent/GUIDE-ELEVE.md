# Atelier 03 — Pipeline Agent ReAct (demi-journée, ~3h30)

> **Comment ce guide differe de l'ancien GUIDE-ELEVE.md** : ici tu ne suis pas un step-by-step.
> Tu recois une mission, des contraintes, des indices ; tu construis. Si tu cherches le tuto,
> ouvre `homebutler/` et lis les modules -- mais alors tu n'apprends pas.

---

## 🚦 Pré-vol (avant de commencer)

- [ ] `bash scripts/check_atelier_ready.sh 03` retourne OK
- [ ] Index FAISS construit (`data/faiss_index/` existe)
- [ ] Index ChromaDB construit (`data/chroma_db/` existe)
- [ ] Variable `ANONYMIZED_TELEMETRY=false` ajoutee dans ton `.env`
- [ ] `pip install "chromadb>=1.0.15"` effectue
- [ ] J'ai lu la section "Perimetre" ci-dessous

> **Avertissement ChromaDB** : si tu vois des messages "Failed to send telemetry event"
> au demarrage, c'est inoffensif mais perturbant. Fix rapide :
> ajouter `ANONYMIZED_TELEMETRY=false` dans ton `.env` ou lancer
> `export ANONYMIZED_TELEMETRY=false` dans le terminal avant chaque session.

---

## La mission

Le PM HomeButler te demande :

> "Notre assistant doit pouvoir repondre a des questions complexes qui croisent plusieurs sources.
> Par exemple : 'Il fait -5 degres demain, comment je prepare ma maison et que puis-je commander
> a un producteur local pour me rechauffer ?' -- une question qui necessite de consulter la meteo,
> les notices d'equipement ET le catalogue producteurs en meme temps. Construis-moi ca."

**Livrable** : un agent CLI qui orchestre au moins 3 outils distincts et produit une reponse
synthetisant les 3 sources.

**Criteres de succes auto-verificables** :
- [ ] `tools_used` contient >= 3 outils distincts dans les intermediate_steps
- [ ] Recall@5 EnsembleRetriever > Recall@5 FAISS seul (mini-lab)
- [ ] Reponse finale produite en < 30 secondes
- [ ] Test memoire reussi : info donnée au tour 1 retrouvee au tour 3

**Budget temps** : 1h40 Core (+30 min Sprint OU 60-70 min Bonus)

> **Note temps** : cet atelier est le plus dense de la formation.
> Si tu es encore dans les etapes Core apres 1h45, passe directement au Sprint -- pas de honte,
> c'est prevu. Sprint et Bonus sont **mutuellement exclusifs**.

> **Rate limits Anthropic** : l'agent ReAct fait 5-10 appels API par question.
> Si tu vois des erreurs 429, attends 60 secondes ou configure `LLM_PROVIDER=ollama` dans `.env`.

---

## Périmètre de cet atelier

**Dans le scope :**
- EnsembleRetriever (combinaison FAISS + ChromaDB avec poids configurables)
- ChromaDB (construction et interrogation d'index)
- Pattern ReAct (Reasoning + Acting)
- Tools/outils LangChain : definition, description, integration dans l'agent
- Memoire conversationnelle (`memory_k`)
- Parametres : `faiss_k`, `chroma_k`, `ensemble_weights`, `max_iterations`, `temperature` agent
- Metriques : Recall@5 ensemble vs FAISS seul, latence agent, step count, contextual correctness

**Hors scope (ateliers suivants) :**
- Fine-tuning, LoRA, QLoRA
- Deploiement API (FastAPI, endpoints REST)
- Interface Streamlit
- RAFT (Retrieval-Augmented Fine-Tuning)
- Evaluation comparative multi-strategies (reservee a At.06)

**Garde-fou active** : `.claude/CLAUDE.md` local + hook UserPromptSubmit
(si tu utilises Claude/Cursor : ne desactive pas ces fichiers)

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

## Carnet de bord (concepts à mobiliser)

### Mini-lexique obligatoire

| Terme | Ce que c'est | Analogie quotidienne |
|---|---|---|
| **Hybrid Search / EnsembleRetriever** | Combine la recherche par mots-cles (FAISS dense) ET la comprehension semantique (Chroma) pour retrouver les meilleurs documents | Google combine les resultats exacts ("code WiFi") ET les resultats de sens ("acces internet appartement") pour toi |
| **ChromaDB** | Base de données vectorielle qui stocke les embeddings avec un index par metadonnées (type de doc, piece, etc.) | Un classeur avec des onglets etiquetes : tu peux filtrer "tous les docs chaudiere" en un clin d'oeil |
| **ReAct = Reason + Act** | Schema de prompt qui force le LLM a raisonner en boucle : Thought -> Action -> Observation -> Thought -> ... jusqu'a la reponse finale | Sherlock Holmes : il ne repond pas directement. Il se pose une question, inspecte, constate, reformule -- jusqu'a avoir toutes les pieces |
| **Tool / outil** | Fonction Python decrite pour le LLM. Le LLM lit la description et decide de l'appeler ou non. Description bacle = outil ignore | Le livre de recettes, le telephone et le calendrier que l'assistant consulte avant de repondre. S'ils ne sont pas etiquetes, il ne sait pas lequel prendre |
| **Memoire conversationnelle** | `ConversationBufferWindowMemory(k=6)` : on garde les 6 derniers echanges. L'agent se souvient de ce qui a ete dit | Le concierge qui se souvient que tu avais commande une pizza mardi -- il ne te fait pas tout re-expliquer |
| **max_iterations** | Nombre maximum de tours Thought/Action/Observation avant que l'agent s'arrete de force | Un minuteur de cuisine : si le chef n'a pas fini apres 8 tentatives, on passe au service -- on n'attend pas indefiniment |

### EnsembleRetriever — comment ça fonctionne

```
Question
   |
   +---> FAISS (dense vectors)  --+
   |                               |--> Reciprocal Rank Fusion --> Top-K fusionne
   +---> ChromaDB (filtres meta) --+
```

Les `ensemble_weights = [0.6, 0.4]` disent : "je fais confiance a FAISS a 60% et a Chroma a 40%".
Si tu mets `[1.0, 0.0]`, c'est FAISS seul -- c'est le baseline du mini-lab.

**Fichier cle** : `homebutler/rag/retriever.py` -- fonction `get_ensemble_retriever()`

### Architecture de l'agent ReAct

```
                    +------------------+
  Question   --->   |    LLM (ReAct)   |
                    +--------+---------+
                             |  Thought: "je dois d'abord la meteo"
                             v
                    +------------------+
                    |  get_weather()   |  <-- Tool 1
                    +--------+---------+
                             |  Observation: "-5°C, neige"
                             v
                    +------------------+
                    |  LLM (ReAct)     |  Thought: "maintenant la notice chaudiere"
                    +--------+---------+
                             |
                    +------------------+
                    |  search_docs()   |  <-- Tool 2
                    +------------------+
                             |
                    [...]                  Tool 3, etc.
                             |
                    Final Answer
```

**Fichiers cles** :
- `homebutler/agent/react_agent.py` -- assemblage de l'agent
- `homebutler/agent/tools.py` -- les 4 outils disponibles
- `homebutler/rag/retriever.py` -- `get_ensemble_retriever()`

---

## TRONC COMMUN (1h40)

### Étape 1 — EnsembleRetriever (25 min)

**Objectif** : construire le retriever hybride FAISS+Chroma et verifier qu'il retourne des chunks fusionnes.

**Indices Build** :
- Import : `from homebutler.rag.retriever import get_ensemble_retriever`
- La fonction prend `faiss_k`, `chroma_k` et retourne un retriever LangChain standard
- Teste avec : `retriever.invoke("Quelle est la marque de ma chaudiere ?")`
- Compte les chunks retournes -- tu devrais en voir plus qu'avec FAISS seul

**Garde-fou Vibe** : avant de valider, ton agent doit te demander :
"Explique en 3 phrases : (1) ce que fait EnsembleRetriever, (2) pourquoi tu as choisi ces poids,
(3) ce qui se passe si tu mets `ensemble_weights=[1.0, 0.0]`."

**Ouverture exercice.py** : c'est le fichier squelette. Le TODO 1 concerne cette etape.
Lance `python ateliers/atelier-03-pipeline-agent/exercice.py` pour voir l'etat d'avancement.

---

**Checkpoint 1** -- lance `python ateliers/atelier-03-pipeline-agent/checkpoints/check_1.py`

*Sans validation du checkpoint -> on ne passe pas a l'etape suivante.*

---

### Mini-lab — EnsembleRetriever vs FAISS seul (15 min)

**Variable a faire varier** : `ensemble_weights`

| Configuration | Poids FAISS | Poids Chroma | A mesurer |
|---|---|---|---|
| FAISS seul (baseline) | 1.0 | 0.0 | Recall@5 |
| Equilibre | 0.5 | 0.5 | Recall@5 |
| FAISS dominant | 0.6 | 0.4 | Recall@5 |
| Chroma dominant | 0.2 | 0.8 | Recall@5 |

**Question test multi-source** : "Quelle est la marque de la chaudiere et quel artisan peut intervenir rapidement ?"
(cette question croise notices maison ET annuaire producteurs -- FAISS seul rate souvent l'un des deux)

**Mesure** : compte combien de chunks sur les 5 premiers retournes concernent CHAQUE source.
Note tes resultats dans ton carnet.

**Autres variables a explorer** :

| Parametre | Valeurs a tester | Metrique |
|---|---|---|
| `faiss_k` | 2 / 4 / 8 | Recall@5, latence |
| `chroma_k` | 2 / 3 / 6 | Recall@5, diversite |
| `ensemble_weights` | [0.6,0.4] / [0.5,0.5] / [0.8,0.2] | Recall@5 |

---

### Étape 2 — Tools et agent ReAct (30 min)

**Objectif** : assembler l'AgentExecutor avec les 4 outils et le faire tourner sur la question multi-outils.

**Indices Build** :
```python
# Imports cles (decommente dans exercice.py)
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from homebutler.agent.tools import (search_docs_tool, analyze_energy_tool,
                                     find_products_tool, get_weather_tool)
from homebutler.llm.provider import get_llm

# Assemblage (TODO 3 dans exercice.py)
llm = get_llm(temperature=0.1, max_tokens=2048)
prompt = hub.pull("hwchase17/react-chat")  # supporte chat_history
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=8,       # <-- ne jamais omettre !
    handle_parsing_errors=True,
    return_intermediate_steps=True,  # TODO 4
)
```

**Parametres a connaitre** :

| Parametre | Valeurs | Effet |
|---|---|---|
| `temperature` | 0.1 / 0.2 / 0.3 | Variabilite du raisonnement |
| `max_iterations` | 4 / 8 / 12 | Profondeur de la recherche vs risque de boucle |
| `memory_k` | 0 / 6 / 20 | Longueur de l'historique memorise |

**Garde-fou Vibe** : tu dois predire combien de steps l'agent va faire sur la question test AVANT de lancer.
Ecris ta prédiction. Ensuite mesure.

---

#### 🐛 Casse-moi ça — Bug Hunt (20 min)

Trois bugs a diagnostiquer. Applique-les un par un, observe le comportement, repare.

```bash
# Bug 1 -- description d'outil bacle
git apply ateliers/atelier-03-pipeline-agent/bugs/v1.patch
pytest ateliers/atelier-03-pipeline-agent/bugs/test_v1.py -v
# repare, puis :
git checkout -- .

# Bug 2 -- trop d'outils
git apply ateliers/atelier-03-pipeline-agent/bugs/v2.patch
pytest ateliers/atelier-03-pipeline-agent/bugs/test_v2.py -v
# repare, puis :
git checkout -- .

# Bug 3 -- sans max_iterations
git apply ateliers/atelier-03-pipeline-agent/bugs/v3.patch
pytest ateliers/atelier-03-pipeline-agent/bugs/test_v3.py -v
# repare, puis :
git checkout -- .
```

**Regle anti-cheat** : formule une hypothese sur ce qui se passe (comportement observe)
AVANT de lire le patch. Ecris-la dans ton carnet.

Lis ensuite les explications dans `bugs/v1_explanation.md`, `bugs/v2_explanation.md`, `bugs/v3_explanation.md`.

---

### Mesure-toi (15 min)

Remplis ce tableau dans ton carnet de bord :

| Metrique | Cible | Mon resultat |
|---|---|---|
| Nombre d'outils orchestres | >= 3 | ? |
| Recall@5 EnsembleRetriever | > Recall@5 FAISS | ? |
| Latence agent (question multi-outils) | < 30 secondes | ? |
| Step count (intermediate_steps) | observable | ? |
| Test memoire (info tour 1 retrouvee tour 3) | OK / KO | ? |

**Test memoire** : pose d'abord "Ma chaudiere est une Viessmann, note ca." Puis pose 2 autres questions.
Puis demande : "Et tu m'as dit quoi sur ma chaudiere tout a l'heure ?" -- l'agent doit retrouver l'info.

---

**Checkpoint final Core** -- lance `python ateliers/atelier-03-pipeline-agent/checkpoints/check_final.py`

- Score >= 80% : pars en Bonus
- Score < 60% : pars en Sprint
- Sinon : prends une pause (5 min), refais le checkpoint le plus faible, puis Bonus

---

## SPRINT (chemin alternatif, 30 min)

Si tu arrives ici avec moins de 60% au checkpoint final ou si tu es en retard, choisis l'une des deux options :

**Option A -- Rattrapage ReAct** : decommente entierement exercice.py (les TODO), lance la solution,
lis chaque etape en verbose=True et note ce que fait chaque Thought/Action/Observation.
Objectif : etre capable de decrire la boucle ReAct en 5 lignes a quelqu'un qui ne la connait pas.

**Option B -- Rattrapage memoire** : compare les reponses de l'agent avec `memory_k=0` vs `memory_k=6`
sur un dialogue de 3 tours. Note les differences. Conclus : quand la memoire aide, quand elle gene.

Dans les deux cas, remplis la section "Mesure-toi" avec au moins 3 metriques reelles.

---

## BONUS (parcours alternatif, 60-70 min)

Format obligatoire : `examples-supports/reflexion-challenge.md` pour chaque defi.

### 🏆 Défi Bonus 1 — Ajouter un outil scope-safe

**POURQUOI cette question ?**
Un bon agent n'est pas celui qui a le plus d'outils -- c'est celui dont les outils sont bien delimited.
Tu vas en ajouter un nouveau et observer l'impact sur le comportement global.

**Contexte**
Le guide `tps.md` (lignes 325-338) liste 7 erreurs communes sur les outils. La plus frequente :
des descriptions trop vagues qui font que le LLM ignore l'outil ou l'appelle a mauvais escient.

**Question**
Ajoute un outil `get_indoor_temperature` qui retourne une valeur fictive (ex: 19.5°C dans le salon).
Ecris deux descriptions : une vague ("retourne la temperature") et une precise
("retourne la temperature actuelle d'une piece de la maison [salon, chambre, cuisine].
A utiliser quand l'utilisateur demande s'il fait chaud ou froid DANS le logement, pas dehors.").
Lance l'agent sur la question "Est-ce qu'il fait chaud dans mon salon ?" avec chaque version.

**Pistes**
- L'agent appelle-t-il l'outil avec la description vague ? Avec la description precise ?
- Le nombre de steps change-t-il ?
- Comment changes-tu la description pour etre certain que le LLM l'utilise ?

Note tes resultats : outil appele (oui/non) x description (vague/precise) = tableau 2x2.

---

### 🏆 Défi Bonus 2 — Mémoire ON vs OFF sur dialogue 3 tours

**POURQUOI cette question ?**
La memoire conversationnelle a un cout (tokens supplementaires a chaque tour) et un benefice
(coherence du dialogue). Savoir quand l'activer et avec quel `k` est un choix d'ingenierie.

**Contexte**
`gradio_demo.py` (deja fourni dans ce dossier) propose une interface pour dialoguer avec l'agent.
Tu peux l'utiliser sans modification.

**Question**
Lance `python ateliers/atelier-03-pipeline-agent/gradio_demo.py`.
Dialogue 3 tours avec `memory_k=0` puis avec `memory_k=6` :
- Tour 1 : "Ma chaudiere s'appelle Viessmann."
- Tour 2 : "Quelle est la temperature ideale pour cette chaudiere en hiver ?"
- Tour 3 : "Et tu m'as dit quoi sur ma chaudiere tout a l'heure ?"

**Pistes**
- Avec `memory_k=0` : l'agent repond-il correctement au tour 3 ?
- Avec `memory_k=6` : idem.
- A quel moment augmenter `k` devient contre-productif (trop de tokens) ?
- En production sur Merenza, quel `k` choisirais-tu et pourquoi ?

---

## Wrap-up (10 min)

**Checklist finale** :
- [ ] Criteres de succes atteints (section "La mission")
- [ ] Tous les checkpoints valides
- [ ] `bash scripts/verify_branch_scope.sh` passe

**Quiz oral 10 questions (5 min chrono)** :

1. Qu'est-ce qu'un EnsembleRetriever ? Cite les deux composantes.
2. Que font les `ensemble_weights` ? Que se passe-t-il si tu mets [1.0, 0.0] ?
3. ReAct : que signifie chaque etape de la boucle Thought/Action/Observation ?
4. Pourquoi la description d'un outil est-elle critique pour l'agent ?
5. Que se passe-t-il si tu omets `max_iterations` ?
6. `ConversationBufferWindowMemory(k=6)` : que garde-t-il exactement ?
7. Pourquoi limiter a 5-7 outils maximum par agent ?
8. Recall@5 EnsembleRetriever vs FAISS seul : lequel a gagne dans ton mini-lab ? Pourquoi ?
9. Cite 1 limite des agents ReAct que tu as observee (latence, impredictibilite, cout...).
10. Dans Merenza, quel cas d'usage beneficierait le plus d'un agent multi-outils ?

Si score < 6/10 : refais le Sprint avant de passer a l'atelier suivant.

**Ce que je retiens en 3 lignes** (ecris-le maintenant -- ce sera utile pour At.04) :

```
1.
2.
3.
```

---

## Pour aller plus loin (hors TP, lecture)

**Pont avec ton projet Merenza** (source : `tps.md` lignes 343-372) :

| Use case | Outils necessaires |
|---|---|
| Concierge IA guest | `get_property_info` (RAG livret), `check_wifi_code` (DB), `request_late_checkout` (Stripe + DB), `weather_forecast` |
| Assistant host admin | `get_reservation_stats`, `draft_review_response`, `check_cleaning_schedule` |
| Onboarding flow | `validate_id`, `send_welcome_email`, `generate_access_code` |

**Avantages des agents dans ton contexte** :
- Une seule interface pour des actions heterogenes (DB + API externes + RAG)
- Adaptation contextuelle : l'agent decide selon la question, pas selon des if/else rigides
- Trace auditable : `intermediate_steps` = log lisible pour debug et conformite

**Limites a garder en tete** :
- Cout : chaque step ReAct = 1 appel LLM. 5 outils = latence 10-30s + cout x5
- Impredictibilite : l'agent peut boucler ou choisir le mauvais outil
- Memoire en serverless : `ConversationBufferWindowMemory` en RAM disparait a chaque cold start

**Lectures complementaires** :
- LangChain ReAct agents : https://python.langchain.com/docs/modules/agents/agent_types/react
- Anthropic Tool Use (plus robuste que ReAct texte) : https://docs.anthropic.com/claude/docs/tool-use
- RAGAS (metriques RAG) : https://arxiv.org/abs/2309.15217
