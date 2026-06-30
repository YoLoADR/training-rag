# GUIDE FORMATEUR — Atelier 08 : Optimisation du pipeline RAG (~3h30)

> Guide destiné au formateur. Il suppose que tu connais le retrieval d'AT02/AT03 et que tu as
> fait tourner l'atelier au moins une fois. L'élève n'a pas accès à ce fichier.
> **Module avancé optionnel** (parcours industrialisation) — se joue après AT03.

---

## 1. Ce que l'élève doit comprendre à la fin

À la fin, l'élève doit pouvoir répondre sans aide :

- Pourquoi un **cross-encoder** est plus précis qu'un **bi-encodeur**, et pourquoi on ne
  l'applique qu'à un petit pool de candidats (coût) ?
- Qu'est-ce que l'**entonnoir** `base_k ≫ top_n` et que se passe-t-il si `base_k == top_n` ?
- Pourquoi, sur un petit corpus, le gain du reranking se voit sur **Recall@1 et MRR**, pas sur Recall@5 ?
- D'où vient la diversité du **multi-query** (le prompt, pas la température) ?
- Qu'est-ce que **HyDE** et quand l'utiliser ?

L'élève doit avoir VU le gain de ses yeux : Recall@1 40%→70%, MRR 0.617→0.833 sur les
questions en langage naturel. C'est la différence entre un atelier compris et un atelier subi.

**Hors scope** (à rappeler si un élève anticipe) : observabilité Langfuse/RAGAS (AT07),
Azure AI Search (AT09). Le hook `.claude/settings.json` bloque ces mots-clés.

---

## 1.bis Carte des blancs — navigation rapide formateur

> `git checkout student/08-optimisation` puis ouvre `homebutler/rag/reranking.py`.
> Les `raise NotImplementedError` sont dans CE fichier (nouveau, propre à AT08). On NE
> touche PAS `homebutler/rag/retriever.py` (code AT03 réutilisé).

### `homebutler/rag/reranking.py`

| Fonction | Ce que l'élève écrit | Pourquoi ce choix |
|---|---|---|
| `get_reranked_retriever(base_k, top_n)` | `base = get_faiss_retriever(k=base_k, fetch_k=max(base_k,20))` ; `compressor = FlashrankRerank(model=RERANK_MODEL, top_n=top_n)` ; `return ContextualCompressionRetriever(base_compressor=compressor, base_retriever=base)` | L'entonnoir : récupère large (base_k) puis reranke à top_n. Réutilise le retriever AT03 sans le modifier. |
| `get_multiquery_retriever(k)` | `MultiQueryRetriever.from_llm(retriever=get_faiss_retriever(k=k), llm=get_llm(temperature=0), prompt=MULTIQUERY_PROMPT)` | Diversité par le prompt, reproductibilité par temperature=0. |
| `get_hyde_chain()` | `hyde_prompt | get_llm(temperature=0) | StrOutputParser()` | Réponse hypothétique → embedding plus proche des chunks. Bonus. |

### Vérifier l'état des blancs en 30 s
```bash
git checkout student/08-optimisation
grep -n "raise NotImplementedError" homebutler/rag/reranking.py
```

---

## 2. Setup formateur — avant l'atelier

```bash
git checkout atelier/08-optimisation
git status                                    # clean
source .venv/bin/activate
pip install -r requirements_atelier08.txt
pip install -e .
python scripts/generate_documents.py          # corpus (si absent)
python scripts/preload_models.py              # fastembed + flashrank (~34 Mo)
```

> `flashrank` télécharge `ms-marco-MiniLM-L-12-v2` (~34 Mo) au 1er run. **Pré-télécharge-le
> la veille** (`preload_models.py`) sinon 15 téléchargements simultanés en salle.

### Test de fumée
```bash
python ateliers/atelier-08-optimisation/solution.py
# Attendu : baseline Recall@1=40% MRR=0.617 → reranké Recall@1=70% MRR=0.833
pytest ateliers/atelier-08-optimisation/bugs/ -v      # 3 passed sur la version corrigée
bash scripts/check_atelier_ready.sh 08
```

Si la baseline est déjà à Recall@1 ≈ 100%, c'est que tu as remplacé les questions naturelles
par des questions "mot pour mot" — remets le `BENCHMARK_QUESTIONS` d'origine (langage naturel).

---

## 3. Déroulé détaillé

| Bloc | Durée | Contenu |
|---|---|---|
| Slides | 30 min | bi/cross-encoder, entonnoir, multi-query, HyDE |
| Démo live | 20 min | montrer solution.py : baseline vs reranké |
| Passage de relais | 5 min | commandes student/08 + QUICK rappel |
| Core élève | 1h40 | coder reranking.py + mesurer |
| Bug Hunt | 20 min | 3 bugs |
| Mesure + Checkpoint | 15 min | tableau + check_final |
| Sprint OU Bonus | 30-70 min | selon score |

### Démo live (T+30)
```bash
git checkout atelier/08-optimisation
python ateliers/atelier-08-optimisation/solution.py
```
- Ouvre `homebutler/rag/reranking.py` → montre `get_reranked_retriever()`. Pointe l'entonnoir
  `base_k=20` (FAISS) → `FlashrankRerank(top_n=5)`. Insiste : "le bi-encodeur ratisse, le
  cross-encoder tranche".
- Quand la solution tourne, pointe **Recall@1 40%→70%** et **MRR 0.617→0.833**. Dis : "Recall@5
  ne bouge presque pas — il sature. Le reranking agit sur l'ORDRE, donc Recall@1 et MRR."
- Montre 1 question concrète ("mon linge ressort trempé") : le bon chunk passe du rang 2 au rang 1.

### Passage de relais (T+50)
Écris au tableau :
```bash
git checkout student/08-optimisation
cat ateliers/atelier-08-optimisation/QUICK-START.md   # si présent, sinon GUIDE-ELEVE.md
python ateliers/atelier-08-optimisation/exercice.py   # crash NotImplementedError → normal
```
Annonce : **« 1h40 Core. Critère : ΔRecall@1 ≥ +20 pts. Bloqué 15 min → main levée. »**

---

## 4. Bug Hunt — ce qui se passe concrètement

> Reset après chaque bug : `git checkout -- homebutler/rag/reranking.py`

### Bug v1 — base_k == top_n
Le patch met `RERANK_BASE_K=5` (== top_n). `test_v1` vérifie que le pool de candidats est
plus grand que la sortie : avec le bug, base (5) == final (5) → `5 > 5` est faux → FAIL.
Question socratique : "Si tu présélectionnes 5 CV et que tu en gardes 5 après entretien,
à quoi sert l'entretien ?"

### Bug v2 — multi-query → 1 reformulation
Le patch réécrit `MULTIQUERY_PROMPT` pour demander 1 reformulation. `test_v2` est une analyse
statique du prompt (pas d'appel LLM, donc déterministe) : il échoue si le prompt ne demande
pas plusieurs reformulations. Question : "La diversité vient-elle de la température ou de la
consigne ?" (réponse : la consigne).

### Bug v3 — top_n non passé
Le patch instancie `FlashrankRerank(model=...)` sans `top_n`. flashrank applique son défaut (3).
`test_v3` vérifie que la sortie a exactement `RERANK_TOP_N` (5) docs → FAIL (3≠5). Question :
"Un paramètre oublié plante-t-il toujours ? Ici non — il prend une valeur par défaut silencieuse."

Après chaque bug, faire lire `bugs/vN_explanation.md` (QCM vrai/faux).

---

## 5. Checkpoints

- `checkpoints/check_1.py` — 3 QCM (bi/cross-encoder, entonnoir, multi-query). Seuil 2/3.
- `checkpoints/check_final.py` — 5 QCM. ≥4/5 → Bonus, <3/5 → Sprint.

Si l'élève rate la question Recall@1-vs-Recall@5 : lui faire relancer solution.py et observer
que Recall@5 ne bouge pas alors que Recall@1 fait +30 pts.

---

## 6. Questions fréquentes

**"Pourquoi mon ΔRecall@1 est nul ?"** → soit `base_k == top_n` (pas d'entonnoir), soit
les questions sont "mot pour mot" du document (baseline déjà parfaite). Vérifie les deux.

**"flashrank ne se télécharge pas"** → réseau requis au 1er run. Sinon `preload_models.py`.

**"Le reranking est-il toujours gagnant ?"** → non, sur certaines questions il peut dégrader
(ex. ici "combien je récupère de caution" passe du rang 1 au rang 3). Il gagne EN MOYENNE.
Bon point de discussion sur l'évaluation agrégée vs cas par cas.

**"Peut-on mettre le cross-encoder en étage 1 ?"** → non : scorer tout le corpus à chaque
requête est trop lent. C'est tout l'intérêt de l'architecture en 2 étages.

**"Différence avec MMR (AT02) ?"** → MMR diversifie (évite les doublons) mais reste un
bi-encodeur. Le reranking re-score la pertinence avec un modèle dédié (cross-encoder).

---

## 7. Signaux d'alerte (élève bloqué)

- **Confond base_k et top_n** → analogie présélection/entretien.
- **Veut augmenter la température pour diversifier le multi-query** → rappeler que la diversité
  vient du prompt ; un seul appel génère les N variantes.
- **Modifie retriever.py** → STOP : on code dans reranking.py, on réutilise retriever.py.
- **Déçu que Recall@5 ne bouge pas** → c'est attendu ; regarder Recall@1 et MRR.

---

## 8. Transition

À la fin d'AT08, l'élève sait améliorer ET mesurer la précision du retrieval. Deux suites :
- **AT07** : "tu as mesuré une fois en CLI — comment mesurer EN CONTINU en production, tracer
  chaque requête et noter la qualité ?" → observabilité Langfuse + RAGAS.
- **AT09** : "ton index FAISS est local — comment passer à un vector store managé en cloud ?"
  → Azure AI Search.
