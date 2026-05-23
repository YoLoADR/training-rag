# Atelier 01 — LLM Baseline (demi-journée, ~3h30)

> **Comment ce guide diffère de l'ancien GUIDE-ELEVE.md** : ici tu ne suis pas un step-by-step.
> Tu reçois une mission, des contraintes, des indices ; tu construis. Si tu cherches le tuto,
> ouvre `homebutler/llm/provider.py` et lis le code — mais alors tu n'apprends pas.

---

## 🚦 Pré-vol (avant de commencer) — 20 min

- [ ] `bash scripts/check_atelier_ready.sh 01` retourne OK
- [ ] `.env` configuré : `ANTHROPIC_API_KEY` présente OU `LLM_PROVIDER=ollama` + Ollama tourne (`ollama list`)
- [ ] J'ai lu la section "Périmètre" ci-dessous
- [ ] Je sais ce que signifient "LLM", "temperature" et "hallucination" (cf. Carnet de bord)

---

## 🎯 La mission

Le PM HomeButler te demande : **"On a un budget limité — avant d'investir dans le RAG, prouve-moi qu'un LLM seul ne peut PAS servir d'assistant maison, et chiffre l'échec."**

Tu as les 10 questions suivantes à lui poser :

**Questions privées (données inconnues du LLM) :**
1. Quelle est la marque de ma chaudière ?
2. À quelle température dois-je régler ma chaudière la nuit ?
3. Quelle est la classe énergétique (DPE) de mon logement ?
4. Quel est le numéro à appeler en cas de fuite d'eau dans mon bail ?
5. Quels sont les producteurs locaux disponibles près de chez moi ?

**Questions générales (le LLM devrait savoir) :**
6. Qu'est-ce qu'une chaudière à condensation ?
7. Comment purger un radiateur en 3 étapes ?
8. Quelle est la réglementation DPE en France en 2024 ?
9. Qu'est-ce que le tiers-payant pour les réparations locatives ?
10. Quels sont les légumes de saison en automne ?

**Livrable** : une démo CLI (`python exercice.py`) qui teste les 10 questions et affiche un **hallucination rate** calculé.

**Critères de succès auto-vérifiables** :
- Hallucination rate ≥ 80 % sur les 5 questions privées
- Le script tourne en < 5 s par question (ou < 60 s total)
- `bash scripts/verify_branch_scope.sh` passe

**Budget temps** : 1h40 Core (+30 min Sprint OU 60 min Bonus)

---

## 🚧 Périmètre de cet atelier

- ✅ **Dans le scope** : LLM, prompt, temperature, top_p, seed, system vs user prompt, few-shot prompting, max_tokens, knowledge cutoff, LLM_PROVIDER (anthropic/ollama), ANTHROPIC_MODEL (sonnet/haiku)
- ❌ **Hors scope** (ateliers suivants) : RAG, embeddings, vectorstore, FAISS, agents, ReAct, fine-tuning, LoRA
- 🛡️ **Garde-fou activé** : `.claude/CLAUDE.md` local + hook `UserPromptSubmit`
  (si tu utilises Claude/Cursor : ne désactive pas ces fichiers — ils bloquent intentionnellement les concepts hors-scope)

---

## 🛠️ vs 🎮 — Choisis ta piste

**Déclare ta piste maintenant** (mets une croix dans ton carnet de bord ou dis-le à voix haute) :

| Critère | 🛠️ Piste Build | 🎮 Piste Vibe |
|---|---|---|
| **Outil** | Code à la main ; Claude Code en mode `plan` ou fermé | Délégation OK à Claude/Cursor |
| **Liberté** | Tu décides tout | Tu valides ce que l'IA produit |
| **Obligation** | Lire les indices fournis | Expliquer en 3 phrases ce que fait le code généré |
| **Bug Hunt** | Tu cherches le bug toi-même | Tu prédis l'effet du bug avant de regarder le test |
| **Checkpoint** | Tu réponds de mémoire | Tu expliques à voix haute — pas en lisant le guide |

> **Piste Vibe : obligation contractuelle** — Pour chaque étape validée, tu dois :
> (a) Expliquer la décision en 3 phrases à ton voisin (ou dans ton carnet de bord)
> (b) Modifier 1 paramètre clé et prédire l'impact avant de lancer
> (c) Débugger le Bug Hunt sans demander à l'IA "trouve le bug"

---

## 🧠 Carnet de bord (concepts à mobiliser)

> Ces définitions te serviront pendant l'atelier ET à l'oral du Wrap-up. Lis-les avant de coder.

### LLM (Large Language Model)
Un LLM est un modèle entraîné sur des milliards de textes du web pour prédire statistiquement le token suivant dans une séquence.

**Analogie** : une encyclopédie figée au moment de son impression. Elle sait tout ce qui était sur internet jusqu'à sa date de clôture, mais elle ne connaît pas l'actu d'aujourd'hui, ni les documents privés que tu n'as jamais publiés.

### Prompt
Le texte que tu envoies au LLM pour déclencher une réponse. Il peut être structuré en deux parties : le **system prompt** (instructions générales = fiche de poste) et le **user prompt** (la question concrète).

**Analogie** : la question posée à l'encyclopédie. La qualité de ta question détermine la qualité de la réponse — mais l'encyclopédie ne peut répondre qu'avec ce qu'elle contient.

### Temperature
Paramètre entre 0.0 et 1.0 qui contrôle le degré d'aléatoire dans la sélection des tokens.
- `T=0` → toujours le token le plus probable → réponse déterministe, répétable
- `T=1` → sampling sur la distribution brute → réponse variable, créative
- `T>1` → distribution aplatie → très aléatoire, risque de hors-sujet

**Analogie** : un dé à 6 faces. À T=0, le dé est pipé pour toujours tomber sur 6. À T=1, le dé est normal. À T=1.5, les faces rares (2, 3) ont autant de chance que le 6.

### Knowledge cutoff
Date à partir de laquelle le LLM n'a plus reçu de données d'entraînement. Tout événement, document, ou information postérieure à cette date est inconnu du modèle.

**Analogie** : le journal de bord d'un marin arrêté à une date. Le marin peut parler de tout ce qu'il a vécu avant, mais il ignore ce qui s'est passé dans le port après son départ.

### Hallucination
Quand un LLM produit une affirmation fausse avec une confiance apparente. Cela arrive parce que le modèle optimise la vraisemblance statistique du texte — pas la vérité.

**Analogie** : le consultant qui invente une réponse pour ne pas dire "je ne sais pas". Il répond avec assurance, le chiffre semble plausible, mais il l'a inventé. Sur les données privées de ton logement, le LLM hallucine systématiquement.

### Token
Unité minimale de traitement pour un LLM. Environ 1 token ≈ 4 caractères en anglais, ≈ 3-4 caractères en français. Le coût API est calculé en tokens (input + output).

**Analogie** : la syllabe pour le modèle. "Cha-u-diè-re" = ~4 tokens. `max_tokens` = nombre maximum de syllabes que le modèle peut produire en réponse.

### System prompt
La partie du prompt qui donne au LLM son rôle, ses contraintes, et son comportement général — avant toute question utilisateur. Il est invisible pour l'utilisateur final.

**Analogie** : la fiche de poste d'un employé. "Tu es un assistant maison poli, tu réponds uniquement sur le logement de l'utilisateur, tu ne fournis pas d'informations que tu ne peux pas vérifier." Sans fiche de poste, l'employé improvise — souvent mal.

### Few-shot prompting
Technique qui consiste à donner au LLM 2-3 exemples de question/réponse dans le prompt pour "calibrer" son style et son comportement avant la vraie question.

**Analogie** : montrer à un stagiaire 3 exemples d'emails bien rédigés avant de lui demander d'en écrire un. Il s'aligne naturellement sur le style des exemples.

---

## 🎯 TRONC COMMUN (1h40)

### Étape 1 — Instancier le LLM et poser les 5 questions privées (25 min)

**Objectif** : voir de ses propres yeux que le LLM invente des réponses sur des données privées.

**Indices (Build)** :
- Fichier à compléter : `ateliers/atelier-01-llm-baseline/exercice.py`
- Fonction clé : `get_llm(temperature=0.1)` dans `homebutler/llm/provider.py`
- Import : `from homebutler.llm.provider import get_llm`
- Appel LLM : `llm.invoke([HumanMessage(content=question)])` — retourne un objet dont `.content` est la réponse

**Garde-fou (Vibe)** :
- Avant de regarder la réponse générée, **prédis** : va-t-il répondre "je ne sais pas" ou inventer ?
- Consigne à donner à ton agent : "Implémente uniquement le TODO 1 et 2 de exercice.py — temperature=0.1, pas de RAG, pas d'embeddings"

> **Observation attendue** : le LLM répond à toutes les questions privées avec une réponse plausible mais inventée. Il ne dit pas "je ne sais pas" — il hallucine avec confiance.

✋ **Checkpoint 1** — Valide avant de continuer

Lance `python ateliers/atelier-01-llm-baseline/checkpoints/check_1.py`

→ Score ≥ 2/3 : continue en Étape 2
→ Score < 2/3 : relis le Carnet de bord (LLM, hallucination, temperature), re-tente le quiz

**LLM-judge rubric** (si tu veux une validation plus poussée) : colle dans Claude/Cursor le prompt suivant :
```
Évalue mon explication en 3 critères stricts (pass/fail) :
1. Est-ce que j'ai expliqué correctement pourquoi un LLM hallucine sur des données privées ?
2. Est-ce que j'ai cité la différence entre temperature=0 et temperature=0.9 ?
3. Est-ce que j'ai relié "knowledge cutoff" à l'impossibilité de connaître le logement ?
Mon explication : [colle ton explication ici]
```

---

### 🔬 Mini-lab — Fais varier la temperature (15 min)

**Variable** : `temperature` dans `get_llm(temperature=...)`
**Plage** : tester T=0.0 puis T=0.9

**Protocole** :
1. Pose la même question (`"Quelle est la marque de ma chaudière ?"`) 3 fois à T=0.0
2. Pose la même question 3 fois à T=0.9
3. Note les réponses dans un tableau :

| Run | T=0.0 | T=0.9 |
|-----|-------|-------|
| 1 | ? | ? |
| 2 | ? | ? |
| 3 | ? | ? |

**Mesure attendue** :
- T=0.0 → 3 réponses identiques (ou quasi) = **determinism rate ≈ 100%**
- T=0.9 → réponses différentes = **variance observable**

**Question à te poser** : si T=0.9 produit des réponses différentes à chaque fois, est-ce qu'un LLM à T=0.9 est fiable pour un assistant maison ? Pourquoi ?

---

### Étape 2 — Ajouter les 5 questions générales et calculer le hallucination rate (30 min)

**Objectif** : comparer le comportement du LLM sur données privées vs données générales.

**Indices (Build)** :
- Les 5 questions générales sont déjà listées dans la section Mission ci-dessus
- Ajoute-les dans ton script comme `QUESTIONS_GENERALES = [...]`
- Pour mesurer le hallucination rate manuellement : tu lis les réponses et tu évalues — la réponse est-elle vérifiablement juste ? (tu peux chercher sur Wikipedia pour les questions générales)
- Pour les questions privées : toute réponse autre que "je ne sais pas" est une hallucination (tu es le seul à savoir la vraie réponse)

**Formule** :
```
hallucination_rate = nombre_hallucinations / nombre_questions_privées
```

**Garde-fou (Vibe)** : Consigne à ton agent : "Ajoute une liste QUESTIONS_GENERALES et une fonction qui calcule le hallucination rate manuellement — température 0.1, aucun RAG"

> **Observation attendue** : hallucination rate ≈ 80-100% sur questions privées (le LLM ne peut pas savoir). Sur questions générales, le LLM répond souvent correctement (données dans son dataset d'entraînement).

---

### 🐛 Casse-moi ça — Bug Hunt (20 min)

**3 bugs à débusquer, un par un.** Chaque bug est livré sous forme de patch git. Tu l'appliques, tu constates l'effet, tu répares, tu valides avec le test.

**Bug v1 — Temperature trop haute (T=0.9 sur question critique)**

```bash
# Applique le patch
git apply ateliers/atelier-01-llm-baseline/bugs/v1.patch

# Lance le test — il doit ECHOUER (le bug est actif)
pytest ateliers/atelier-01-llm-baseline/bugs/test_v1.py -v

# Observe : que se passe-t-il sur "Quelle est la marque de ma chaudière ?"
python ateliers/atelier-01-llm-baseline/exercice.py

# Répare le bug dans exercice.py (sans regarder la solution)

# Valide : le test doit maintenant PASSER
pytest ateliers/atelier-01-llm-baseline/bugs/test_v1.py -v
```

Lis ensuite `bugs/v1_explanation.md` et réponds aux questions vrai/faux.

**Bug v2 — max_tokens=50 (réponse tronquée)**

```bash
git apply ateliers/atelier-01-llm-baseline/bugs/v2.patch
pytest ateliers/atelier-01-llm-baseline/bugs/test_v2.py -v
# Répare, re-valide
```

Lis `bugs/v2_explanation.md`.

**Bug v3 — Pas de system prompt (modèle off-topic)**

```bash
git apply ateliers/atelier-01-llm-baseline/bugs/v3.patch
pytest ateliers/atelier-01-llm-baseline/bugs/test_v3.py -v
# Répare, re-valide
```

Lis `bugs/v3_explanation.md`.

> **Règle anti-cheat** : tu peux demander à l'IA de t'aider à comprendre le comportement observé, mais pas de lui demander "trouve le bug dans le patch". La valeur est dans le raisonnement, pas dans la réponse.

---

### 📊 Mesure-toi (15 min)

Remplis ce tableau avec tes résultats réels (pas des valeurs inventées) :

| Métrique | Valeur observée | Cible |
|---|---|---|
| **(a) Hallucination rate sur 5 questions privées** | ___% | ≥ 80% |
| **(b) Determinism rate à T=0** (3 runs, même question) | ___% | ≈ 100% |
| **(c) Latence Anthropic** (moyenne sur 5 questions) | ___s | < 5s |
| **(d) Latence Ollama** (si disponible) | ___s | — |
| **(e) Tokens consommés** (lecture sur le terminal ou Langfuse) | ~___ | < 50k total |

**Comment mesurer les tokens** : si tu utilises Anthropic, le retour de `llm.invoke()` contient `response.usage_metadata` (input_tokens + output_tokens). Affiche-les.

**Baseline de référence** : hallucination rate ≥ 80% est normal et attendu — c'est le résultat pédagogique. L'objectif de l'atelier 02 sera de ramener ce taux à 0% sur les mêmes questions, grâce au RAG.

✋ **Checkpoint final Core** — lance `python ateliers/atelier-01-llm-baseline/checkpoints/check_final.py`

→ Score ≥ 80% (4/5) : pars en **Bonus** 🏆
→ Score < 60% (< 3/5) : pars en **Sprint** ⚡
→ Entre 60% et 80% : prends 5 min, relis le Carnet de bord du concept raté, puis Bonus

---

## ⚡ SPRINT (chemin alternatif, 30 min)

> Tu es ici parce que le score checkpoint < 60%, ou parce que tu as pris du retard. Pas de problème — rattrape les 2 concepts clés.

**Sprint 1 — Temperature et déterminisme (15 min)**

Ouvre `homebutler/llm/provider.py`. Lis comment `temperature` est passée à `ChatAnthropic`.

Exercice : modifie `exercice.py` pour poser la même question 5 fois avec T=0 et 5 fois avec T=0.9. Affiche la liste des réponses. Constate la différence.

Question à répondre par écrit (1 phrase) : "Pourquoi un assistant maison doit-il utiliser T ≤ 0.3 ?"

**Sprint 2 — System prompt (15 min)**

Ouvre `homebutler/llm/prompts.py`. Observe comment les prompts sont construits.

Exercice : ajoute un system prompt à ton script : `"Tu es un assistant maison. Tu ne peux répondre qu'à des questions sur le logement de l'utilisateur. Si tu ne disposes pas des informations privées, dis 'Je n'ai pas accès à ces informations dans mes données.'"`. Repose les 5 questions privées. La formulation des refus change-t-elle ?

---

## 🏆 BONUS (parcours alternatif, 60-70 min)

> Tu es ici parce que score ≥ 80%. Bienvenue dans la zone d'approfondissement. Chaque défi est au format `reflexion-challenge.md`.

### Défi Bonus 1 — Sonnet vs Haiku : coût, latence, qualité

**POURQUOI cette question ?**
En production, choisir le bon modèle Anthropic est un arbitrage coût/qualité/latence. Sur des réponses factuelles simples, Haiku peut suffire. Sur des raisonnements complexes, Sonnet s'impose. Savoir mesurer cette différence est une compétence pro.

**Contexte**
- Claude claude-haiku-4-5 ≈ 10-20× moins cher que Sonnet (coût input/output)
- Latence Haiku ≈ 2× plus rapide que Sonnet
- Sur les mêmes questions privées (données inconnues), les deux hallucinent — mais peut-être différemment

**Question**
> Pose les 5 questions privées à Haiku (modèle = `claude-haiku-4-5`) et à Sonnet (`claude-sonnet-4-5`). Pour chaque question : note la latence, le nombre de tokens, et évalue la qualité de la réponse (hallucination utile vs refus poli). Quel modèle recommandes-tu pour un assistant maison en prod — et pourquoi ?

**Variable à manipuler** : `ANTHROPIC_MODEL` dans `config.py` ou via `.env`
```python
# Haiku
llm_haiku = ChatAnthropic(model="claude-haiku-4-5", ...)
# Sonnet
llm_sonnet = ChatAnthropic(model="claude-sonnet-4-5", ...)
```

**Mesure attendue** : tableau latence × tokens × qualité perçue × coût estimé pour 1000 requêtes/mois.

**Pistes de réflexion** :
- Sur les données privées, la qualité de l'hallucination est-elle différente ? (Le refus poli de Haiku est-il aussi "propre" que celui de Sonnet ?)
- À quel volume mensuel de requêtes la différence de coût devient-elle significative ?
- Pour un MVP : Haiku ou Sonnet ? Pour la prod à maturité ?

---

### Défi Bonus 2 — Few-shot prompting : réduire l'hallucination sans RAG

**POURQUOI cette question ?**
Avant d'investir dans le RAG, il existe une technique légère : le few-shot prompting. En donnant 3 exemples de réponses correctes dans le prompt, le LLM peut apprendre le format et le ton attendu. Est-ce que ça réduit l'hallucination ? Dans quelle mesure ?

**Contexte**
Le few-shot prompting consiste à ajouter des exemples `question → réponse` dans le system prompt ou en début de conversation. Le LLM s'aligne sur le style observé.

**Question**
> Crée un prompt few-shot avec 3 exemples : question sur chaudière → réponse "Je n'ai pas accès à la marque de votre chaudière dans mes données". Repose les 5 questions privées. Est-ce que le taux de refus poli augmente ? Est-ce que l'hallucination rate diminue ?

**Exemples few-shot à insérer dans le system prompt** :
```
Exemples de comportement attendu :
Q: Quelle est la marque de mon four ?
R: Je n'ai pas accès aux informations sur les appareils de votre logement dans mes données. Pour cette information, consultez votre bail ou votre livret d'accueil.

Q: Quel est mon numéro de contrat d'électricité ?
R: Je n'ai pas accès aux contrats de votre logement. Retrouvez cette information sur votre espace client EDF/Enedis.
```

**Mesure** : recalcule le hallucination rate après few-shot. La différence est-elle significative ?

**Pistes de réflexion** :
- Le few-shot réduit-il vraiment l'hallucination, ou reformule-t-il juste le refus ?
- Combien d'exemples sont nécessaires pour un effet notable (1, 3, 10) ?
- Le few-shot est-il une alternative au RAG ou un complément ?

---

## 🎓 Wrap-up (10 min)

**Checklist de fin** :
- [ ] Hallucination rate calculé et affiché dans le script
- [ ] Mini-lab temperature T=0 vs T=0.9 réalisé et noté
- [ ] 3 bugs du Bug Hunt réparés et testés (`pytest` vert)
- [ ] `bash scripts/verify_branch_scope.sh` passe
- [ ] Checkpoint final ≥ 60%

**Quiz oral chronométré (5 min, 10 questions)** — Réponds sans relire le guide :

1. Qu'est-ce qu'une hallucination LLM ?
2. Quel paramètre rend le LLM déterministe ?
3. Pourquoi T=0.9 est dangereux pour un assistant factuel ?
4. Qu'est-ce qu'un knowledge cutoff ?
5. À quoi sert le system prompt ?
6. Quelle est la différence entre system prompt et user prompt ?
7. Qu'est-ce qu'un token ?
8. Pourquoi `max_tokens=50` pose un problème sur des réponses longues ?
9. Qu'est-ce que le few-shot prompting ?
10. Pourquoi un LLM seul ne peut pas connaître les données privées d'un logement ?

→ Score ≥ 8/10 : excellent — tu es prêt pour l'atelier 02.
→ Score 5-7/10 : relis le Carnet de bord des concepts ratés avant l'atelier 02.
→ Score < 5/10 : recommence le Sprint avant de passer à la suite.

**Ce que je retiens en 3 lignes** (à écrire dans ton carnet de bord — utile pour l'atelier 02) :
```
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________
```

---

## 🔗 Pour aller plus loin (hors TP, lecture)

**Pont avec ton projet** : dans tout projet qui expose un LLM à des utilisateurs, les données privées (documents internes, données client, contrats) ne doivent jamais être supposées connues du modèle. Le pattern RAG (atelier 02) est la solution standard. Le few-shot est un palliatif insuffisant pour des données volumineuses ou changeantes.

**Lectures complémentaires** :
- Kapur 2008 — *Productive Failure* : pourquoi commencer par l'échec (LLM sans RAG) ancre mieux l'apprentissage que de donner la solution directement
- Documentation Anthropic — *System prompts best practices* : https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts
- LangChain docs — `ChatAnthropic` : température, max_tokens, streaming
