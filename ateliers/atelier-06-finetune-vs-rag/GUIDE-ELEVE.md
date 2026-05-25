# Atelier 06 — Fine-tuning vs RAG / RAFT (demi-journée, ~3h30)

> **Comment ce guide diffère des autres** : c'est l'atelier de synthèse. Tu ne suis pas
> d'étapes prescrites — tu construis un argumentaire chiffré et tu le défends. Le guide
> t'invite à raisonner, pas à exécuter. Si tu cherches "la bonne réponse", c'est que
> tu n'as pas encore les données pour répondre — mesure d'abord.

---

## 🎯 Atelier 06 en un coup d'œil

### État initial (ce qui est déjà là)
- ✅ **Acquis Ateliers 01-05** : API FastAPI complète (3 modes `chat`, `/rag/retrieve`, `/rag/evaluate`, `/chat/compare`), UI Streamlit, fine-tuning AT04 optionnel.
- ✅ **Plomberie fournie** : dataset Q/R conciergerie (`data/qa_dataset/concierge_qa.jsonl`), endpoints `/rag/evaluate` et `/chat/compare` (à activer via `ENABLE_COMPARE_ROUTES=true`), helper `load_qa()`, fonctions d'affichage `show_latency_summary()` / `todo_grille()`.
- 🛠️ **À toi de coder** (fichiers blancs avec indices) :
  - `ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py` — **TODO 2** `evaluate_strategies()` (boucle 3 stratégies + `POST /rag/evaluate`), **TODO 3** `compare_modes()` (double boucle questions × 3 modes + `POST /chat`), **TODO 5** `show_summary()` (tableau Markdown + benchmarks RAFT 2024).

### Objectif mesurable
- Tableau Markdown comparatif chiffré : LLM seul / RAG fixed / RAG recursive / RAG ensemble.
- Grille décision TCO documentée pour 3 cas d'usage métier.

**Critère de succès** (chiffré, reproductible) :
```bash
ENABLE_COMPARE_ROUTES=true uvicorn api.main:app --port 8000 &
python ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py
# → tableau Markdown imprimé, R@1/R@3/R@5 pour 3 stratégies
# → comparaison latence + benchmarks RAFT (94 % QA factuel, 95 % style, 96 % médical)
# → recommandation argumentée dans grille_decision.md
```

### Récupérer la solution (en dernier recours)
```bash
git diff student/06-finetune-vs-rag atelier/06-finetune-vs-rag \
  -- ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py
```

---

## Pré-vol (avant de commencer)

- [ ] `bash scripts/check_atelier_ready.sh 06` retourne OK
- [ ] `.env` contient `ENABLE_COMPARE_ROUTES=true` — **vérifier maintenant**
  ```bash
  grep ENABLE_COMPARE_ROUTES .env  # doit afficher true
  ```
  Sans ça, les routes `/rag/evaluate`, `/chat/compare` et `/rag/compare-strategies` retournent 404.
- [ ] `uvicorn api.main:app --reload --port 8000` démarre
- [ ] Dans Swagger (`/docs`), les routes `/rag/evaluate` et `/chat/compare` **apparaissent** (contrairement à l'Atelier 05)
- [ ] J'ai lu la section "Périmètre" ci-dessous

---

## La mission

Le CTO de HomeButler te demande :

> "On a un assistant qui tourne en RAG. Les utilisateurs se plaignent que les réponses
> manquent de chaleur — ça ne sonne pas 'Merenza'. Et sur les questions très techniques
> (notices, codes erreur), le RAG hallucine parfois.
> Ma question est simple : est-ce qu'on reste sur RAG, on passe au Fine-Tuning, ou
> on fait les deux ? J'ai besoin d'un comparatif chiffré et d'une reco défendable en 5 min."

**Livrable** :
1. Rapport comparatif : tableau de métriques par mode (llm_only / rag_only / agent)
2. `grille_decision.md` remplie avec tes chiffres mesurés
3. Recommandation écrite 1 page

**Critères de succès auto-vérifiables** :
- [ ] >= 3 modes comparés avec métriques chiffrées
- [ ] `grille_decision.md` complété avec tes données (pas les données exemples)
- [ ] Reco défendable oralement en 5 min (voir section Wrap-up)

**Budget temps** : 1h40 Core + (30 min Sprint OU 60 min Bonus)

---

## Périmètre de cet atelier

- **Dans le scope** : RAFT (théorie), évaluation comparative llm_only/rag_only/agent, TCO break-even, toutes les stratégies RAG, toutes les routes API
- **Hors scope** : aucun — c'est l'atelier de synthèse. Tout ce qu'on a vu aux ateliers 01-05 est mobilisable.
- **Garde-fou activé** : `.claude/CLAUDE.md` local
  Si tu délègues à Claude : ta recommandation finale doit être argumentée par les données que tu as mesurées, pas par opinion. Claude te le rappellera.

---

## Choisis ta piste

| | Piste Build | Piste Vibe |
|---|---|---|
| **Manip** | Tu écris les appels API, tu construis le tableau de métriques manuellement | Tu délègues à Claude — mais tu dois expliquer chaque chiffre |
| **Validation** | Tu peux montrer le code et les données à un pair | Avant validation : "Explique en 3 phrases pourquoi tu recommandes X et pas Y" |
| **Bug Hunt** | Tu appliques le patch, tu analyses le comportement observable | Tu formules une hypothèse AVANT d'inspecter le patch |
| **Soutenance** | Tu défends devant le groupe ou devant le formateur | Tu utilises le rubric LLM-judge (voir Wrap-up) |

**Règle commune** : la recommandation finale doit reposer sur tes chiffres. "J'ai l'impression que RAG est mieux" n'est pas une reco — "RAG atteint Recall@5=0.87 vs agent=0.91, pour un surcoût de latence x4 et un TCO identique sur 12 mois" l'est.

---

## Carnet de bord — Mini-lexique

| Terme | Définition courte | Analogie |
|---|---|---|
| **RAFT** (Retrieval-Augmented Fine-Tuning) | Technique qui combine RAG et Fine-Tuning : le modèle est entraîné avec des documents pertinents ET des documents distracteurs mélangés intentionnellement. | Un médecin qui connaît les livres de médecine (RAG) ET a des années d'expérience clinique avec des cas difficiles (FT). Il sait ignorer les faux indices. |
| **TCO** (Total Cost of Ownership) | Coût total sur 12 mois : setup + infrastructure + maintenance + tokens API. | Comme comparer le coût d'une voiture (achat + assurance + entretien) vs Uber (à la course). À quel kilométrage Uber devient-il plus cher ? |
| **Break-even** | Le point à partir duquel une option devient rentable par rapport à l'autre. | Le kilométrage à partir duquel la voiture (FT auto-hébergé) est moins chère que l'Uber (API Anthropic). |
| **Eval comparative** | Mesurer les mêmes métriques sur les mêmes questions pour plusieurs approches — à l'aveugle si possible. | Test à l'aveugle de 3 chefs cuisiniers sur les mêmes 10 recettes : le jury ne sait pas qui a cuisiné quoi. |
| **Perplexité** | Score de "surprise" du modèle face à la bonne réponse. Plus c'est bas, mieux le modèle a appris. | La note d'incompréhension d'un élève : si la bonne réponse à l'examen "le surprend", c'est qu'il ne l'avait pas bien apprise. |
| **F1 score** | Métrique qui équilibre précision (pas de faux positifs) et rappel (pas de faux négatifs). | Note qui punit autant le fait de répondre faux (faux positif) que le fait de ne pas répondre quand on le devrait (faux négatif). |
| **Hallucination rate** | Pourcentage de réponses contenant des faits inventés non vérifiables dans le corpus. | Le taux d'affabulation d'un journaliste : % d'articles avec des faits invérifiables. |
| **Recall@k** | Parmi les k chunks récupérés, quelle proportion contient la bonne information ? | Sur 5 résultats de recherche Google, combien contiennent vraiment ce que tu cherchais ? |

---

## TRONC COMMUN (1h40)

### Etape 1 — Etat des lieux : mesurer les 3 modes (30 min)

**Objectif** : avoir des chiffres réels sur lesquels baser ta recommandation.

Lance `evaluate_pipeline.py` (déjà fourni) :
```bash
python ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py
```

Le script mesure automatiquement :
- Recall@1/3/5 pour les 3 stratégies de chunking (fixed / recursive / ensemble)
- Latence par mode (llm_only / rag_only / agent)

**Mais ce n'est pas suffisant.** Le script ne mesure pas tout. Complète manuellement :

Pour 5 questions "privées" (sur les notices HomeButler — celles où le LLM seul hallucine) :
```bash
# Question test : "Quelle est la marque de ma chaudière ?"
for mode in llm_only rag_only agent; do
  echo "=== $mode ===" 
  curl -s -X POST http://localhost:8000/chat \
    -H 'Content-Type: application/json' \
    -d "{\"message\":\"Quelle est la marque de ma chaudière ?\",\"mode\":\"$mode\"}" \
    | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('response','')[:200])"
done
```

Pour chaque réponse, note : est-ce que la réponse contient "Viessmann Vitodens 100-W" (la vraie marque) ?
- OUI = pas d'hallucination
- NON ou "je ne sais pas" = hallucination ou refus (dans les deux cas, le LLM ne sert pas l'utilisateur)

**Questions d'investigation** (réponds avant de passer à l'Etape 2) :
- Quel mode a le meilleur Recall@5 ?
- Quel mode est le plus lent ? De combien ?
- llm_only hallucine-t-il sur cette question ? Que dit-il exactement ?

**Checkpoint 1** :
```bash
python ateliers/atelier-06-finetune-vs-rag/checkpoints/check_1.py
```

---

### Mini-lab — Faire varier la stratégie de retrieval (15 min)

**Objectif** : comprendre pourquoi "ensemble" > "recursive" > "fixed" sur certaines questions.

Utilise l'endpoint `/rag/compare-strategies` :
```bash
curl -s -X POST "http://localhost:8000/rag/compare-strategies" \
  -H 'Content-Type: application/json' \
  -d '{"query": "Quelle est la marque de ma chaudière ?", "strategies": ["fixed", "recursive", "ensemble"]}' \
  | python3 -m json.tool
```

**Variables à manipuler** : modifie les poids de l'EnsembleRetriever dans `homebutler/rag/retriever.py` :
- `weights=[0.6, 0.4]` (défaut) vs `[0.5, 0.5]` vs `[0.8, 0.2]`
- Mesure l'impact sur Recall@5 et sur la diversité des chunks retournés

**Ce que tu dois observer** : l'ensemble (FAISS + Chroma avec poids) dépasse-t-il systématiquement FAISS seul ? Sur quelles questions ?

---

### Etape 2 — Remplir la grille de décision (25 min)

**Objectif** : traduire tes mesures en décision métier structurée.

Ouvre `ateliers/atelier-06-finetune-vs-rag/grille_decision.md` et remplis la section "8 critères détaillés" avec tes chiffres.

Pour les lignes que tu ne peux pas mesurer directement (Fine-Tuning, Hybride), utilise les benchmarks RAFT :

| Approche | QA factuel | Style/Ton |
|---|---|---|
| RAG seul | 89% | 65% |
| FT seul | 79% | 94% |
| Hybride (RAFT) | 94% | 95% |

Source : Zhang et al. 2024 (RAFT — Retrieval Augmented Fine-Tuning).

**Pour le TCO** : utilise le calcul simplifié de `grille_decision.md` (section TCO 12 mois).

Pour HomeButler avec ~10k requêtes/mois :
- RAG seul (Claude API) : ~0.01€/req × 10k = 100€/mois tokens → 1200€/an
- FT auto-hébergé (VPS GPU ~50€/mois Ollama) : 600€/an infra + setup 3000€ → 3600€ an 1
- Break-even : FT devient rentable à >50k req/mois (au-delà, 0€/req vs 0.01€/req)

Remplis la dernière colonne avec ta recommandation pour le cas HomeButler.

---

### Bug Hunt — Casse-moi ca (20 min)

3 bugs dans la méthodologie d'évaluation. Applique-les, observe l'anomalie, répare.

```bash
# Bug 1 — eval lancée sur le train set (illusion 100% recall)
git apply ateliers/atelier-06-finetune-vs-rag/bugs/v1.patch
pytest ateliers/atelier-06-finetune-vs-rag/bugs/test_v1.py -v
# Observe : recall = 1.00 pour toutes les stratégies. Trop beau pour être vrai.

# Bug 2 — BLEU score utilisé pour mesurer la qualité du ton
git apply ateliers/atelier-06-finetune-vs-rag/bugs/v2.patch
pytest ateliers/atelier-06-finetune-vs-rag/bugs/test_v2.py -v

# Bug 3 — latence mesurée sur 1 seul appel (biais cold-start)
git apply ateliers/atelier-06-finetune-vs-rag/bugs/v3.patch
pytest ateliers/atelier-06-finetune-vs-rag/bugs/test_v3.py -v
```

Après chaque fix : lis `bugs/v[N]_explanation.md` et réponds aux affirmations Vrai/Faux.

> **Ce que tu dois retenir** : les erreurs de méthodologie d'évaluation sont aussi dangereuses que les bugs de code. Une eval sur le train set donne 100% de recall — et te conduit à une reco catastrophiquement mauvaise.

---

### Mesure-toi (10 min)

**Remplis ce tableau avec TES données mesurées** (pas les benchmarks théoriques) :

| Métrique | llm_only | rag_only | agent |
|---|---|---|---|
| Recall@5 (sur 10 questions test) | | | |
| Latence médiane (s) | | | |
| % hallucination questions privées | | | |
| Coût estimé / 1000 req (€) | | | |

Benchmarks de référence (RAFT 2024 + mesures terrain At.06) :
- Recall@5 : fixed ≈ 0.72, recursive ≈ 0.80, ensemble ≈ 0.87
- Latence : llm_only ≈ 2s, rag_only ≈ 3s, agent ≈ 10-30s
- Hallucination llm_only sur questions privées : ~60-80%

---

**Checkpoint final Core** :
```bash
python ateliers/atelier-06-finetune-vs-rag/checkpoints/check_final.py
```

- Score >= 80% : pars en **Bonus**
- Score < 60% : pars en **Sprint**
- Entre les deux : travaille la reco écrite, puis Bonus

---

## SPRINT (chemin alternatif, 30 min)

Si tu es en retard ou score < 60% : consolide l'essentiel.

**Sprint 1 — Les 4 questions de l'arbre de décision** (de `grille_decision.md`) :

Pour le cas HomeButler, réponds à voix haute à chacune :
- Q1 : les notices changent-elles souvent ? → Implique RAG ou FT ?
- Q2 : le ton "Merenza" est-il critique ? → Implique RAG ou FT ?
- Q3 : est-ce qu'on a un GPU ? → Mac sans GPU → quelle option élimine-t-on ?
- Q4 : est-ce qu'on a > 500 paires Q/R annotées ? → Oui/Non → quelle option ?

**Sprint 2 — Reco minimale** : une phrase par dimension.

```
Recommandation : [RAG / FT / Hybride]
Justification factualité : Recall@5 = [ton chiffre] vs benchmark 0.87 (RAG ensemble)
Justification style : [ton observation sur le ton des réponses]
TCO an 1 : [calcul rapide]
Cas où mon choix serait mauvais : [1 phrase]
```

---

## BONUS (parcours alternatif, 60-70 min)

---

### Défi B1 — RAFT : le médecin qui ignore les pièges

**POURQUOI cette question ?**
RAFT (Zhang et al. 2024) atteint 94% en QA factuel vs 89% pour RAG seul et 79% pour FT seul. Mais pourquoi ? Comprendre le mécanisme permet de décider si c'est pertinent pour HomeButler.

**Contexte**
RAFT entraîne le modèle avec des contextes "pollués" : pour chaque question, on mélange 1 document pertinent et k documents distracteurs. Le modèle apprend à ignorer le bruit plutôt que de lui faire confiance. Résultat : il est robuste aux erreurs du retriever.

**Question**
> Construis un argument en 5 min pour défendre "RAFT vaut l'investissement pour HomeButler" ET un contre-argument de 5 min. Lequel est le plus fort ? Pourquoi ?

Critères à aborder :
- Coût dataset : il faut annoter des questions + documents distracteurs
- Temps GPU : Colab T4 gratuit = quelques heures pour Mistral-7B
- Gain mesuré : +5 points de recall vs RAG seul — suffisant pour HomeButler ?
- Risque : sur un corpus de ~100 documents, l'ensemble RAG est déjà à Recall@5=0.87. Le gain RAFT peut être marginal.

> Format `reflexion-challenge.md` : structure ta réflexion en POURQUOI / Contexte / Question / Pistes.

---

### Défi B2 — Mini-débat en duo : FT, RAG ou hybride ?

**POURQUOI cette question ?**
La recommandation technique la plus rigoureuse échoue si tu ne peux pas la défendre face à un PM non-tech. Ce défi entraîne l'arbitrage sous contrainte de temps.

**Contexte**
Tu as tes chiffres. Ton partenaire a peut-être des chiffres différents ou une recommandation différente.

**Format** :
- 3 min chacun : défendre sa reco avec 3 métriques minimum
- 2 min : identifier le point de désaccord principal
- 1 min : proposer un test pour trancher (ex: "on fait un A/B test sur 100 questions pendant 1 semaine")

> Si pas de partenaire : utilise le LLM-judge de la section Wrap-up pour évaluer ta reco.

---

## Wrap-up — Soutenance (15 min au lieu de 10)

Cet atelier est l'atelier de synthèse. Le checkpoint final = mini-soutenance.

### Reco écrite (1 page)

Avant la soutenance, rédige en 1 page :

```
Ma recommandation : LLM seul / RAG / Agent / FT / Hybride

Justification chiffrée :
- Métrique 1 : [nom] = [valeur] (source : [evaluate_pipeline.py / benchmark RAFT])
- Métrique 2 : ...
- Métrique 3 : ...

TCO estimé sur 1 an :
- Option recommandée : [calcul]
- Alternative : [calcul]
- Break-even : [à partir de X req/mois]

Cas d'usage où mon choix serait mauvais :
- [1-2 phrases : dans quel contexte est-ce que je recommanderais l'autre option ?]
```

### Soutenance 5 min

Présente ta reco à un pair (ou au formateur, ou au LLM-judge ci-dessous).

**Rubric LLM-judge** — colle ce prompt dans Claude :

```
Voici la recommandation de [ton prénom] :

[Colle ton texte de reco ici]

Evalue selon ces 3 critères :
(1) Les chiffres sont-ils cohérents avec les benchmarks RAFT (RAG=89%, FT=79%, Hybride=94% QA factuel) ?
(2) Les limites de la recommandation sont-elles reconnues (cas où elle serait mauvaise) ?
(3) La recommandation est-elle défendable pour un PM non-tech sans formation ML ?

Donne un score 1-5 par critère et une critique constructive en 3 lignes.
Sois sévère : un score 5 signifie "aucune amélioration possible".
```

Score cible : >= 3/5 sur chaque critère.

---

**Checklist finale** :
- [ ] Tableau de métriques rempli avec TES mesures (pas uniquement les benchmarks)
- [ ] `grille_decision.md` complété
- [ ] Reco écrite 1 page rédigée
- [ ] Soutenance 5 min faite (pair, formateur ou LLM-judge)
- [ ] `bash scripts/verify_branch_scope.sh` passe

**Quiz oral 10 questions — chrono 5 min** :

1. Qu'est-ce que RAFT et en quoi diffère-t-il de RAG seul ?
2. Pourquoi FT atteint 94% sur le style/ton mais seulement 79% en QA factuel ?
3. Quelle est la différence entre Recall@1 et Recall@5 ?
4. A quel volume de requêtes mensuelles le FT auto-hébergé devient-il rentable vs API ?
5. Pourquoi mesurer la latence sur 1 seul appel est biaisé ?
6. Qu'est-ce que le hallucination rate et comment le mesure-t-on ?
7. Pourquoi utiliser BLEU pour mesurer la qualité du ton "Merenza" est une mauvaise idée ?
8. L'EnsembleRetriever combine quelles deux bases vectorielles ? Pourquoi cette combinaison ?
9. Dans quel cas recommanderais-tu FT seul sans RAG ?
10. Qu'apporte RAFT par rapport à FT + RAG naïvement combinés ?

**Ce que je retiens de la formation en 5 lignes** (à écrire avant de fermer) :
- ...
- ...
- ...
- ...
- ...

---

## Pour aller plus loin

- RAFT : Zhang et al. 2024 — https://arxiv.org/abs/2403.10131
- RAGAS (métriques RAG) : Es et al. 2024 — https://arxiv.org/abs/2309.15217
- `ateliers/tps.md` lignes 825-870 — notes formateur sur RAFT et la comparaison des modes
- `ateliers/atelier-06-finetune-vs-rag/grille_decision.md` — la grille complète avec exemples métier
- `ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py` — le script de benchmark complet
