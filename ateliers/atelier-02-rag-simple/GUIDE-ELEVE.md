# Atelier 02 — RAG Simple FAISS (demi-journée, ~3h30)

> **Comment ce guide diffère de l'ancien GUIDE-ELEVE.md** : ici tu ne suis pas un step-by-step.
> Tu reçois une mission, des contraintes, des indices ; tu construis. Si tu cherches le tuto,
> ouvre `homebutler/rag/ingestion.py` et lis les modules — mais alors tu n'apprends pas.

---

## 🚦 Pré-vol (avant de commencer) — 20 min

- [ ] `bash scripts/check_atelier_ready.sh 02` retourne OK
- [ ] Les PDFs sont présents dans `data/documents/` (sinon : `python scripts/generate_documents.py`)
- [ ] Le modèle d'embeddings est téléchargé :
  ```bash
  python -c "from langchain_community.embeddings import FastEmbedEmbeddings; FastEmbedEmbeddings(model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"
  ```
  Si tu vois `UserWarning: The model ... now uses mean pooling instead of CLS embedding` → **normal, ignore ce warning** (comportement attendu de fastembed >= 0.5.2)
- [ ] `ANTHROPIC_API_KEY` présente dans `.env` OU `LLM_PROVIDER=ollama` fonctionnel
- [ ] J'ai lu la section "Périmètre" ci-dessous
- [ ] **Si Mac ARM (M1/M2/M3) et erreur FAISS à l'installation** :
  ```bash
  pip install faiss-cpu --upgrade
  ```

> **Note Mac ARM** : si `pip install faiss-cpu` échoue avec une erreur de compilation, utilise `pip install faiss-cpu --upgrade` qui télécharge le binaire pré-compilé ARM.

---

## 🎯 La mission

Le PM HomeButler te demande : **"On a prouvé en atelier 01 que le LLM seul hallucine. Maintenant construis un assistant qui indexe les PDFs du logement et cite la bonne notice en réponse. Je veux des métriques chiffrées."**

**Livrable** : une démo CLI (`python exercice.py`) qui :
1. Charge les PDFs HomeButler, les chunke, construit un index FAISS
2. Répond à une question en citant la source (`notice_chaudiere.pdf, p.2`)
3. Calcule et affiche le **Recall@5** sur les 5 questions étalons

**Critères de succès auto-vérifiables** :
- Recall@5 ≥ 0.80 (4 questions sur 5 trouvent leur source dans les 5 premiers chunks)
- Réponse < 5 s (retrieval + génération)
- 0 hallucination sur questions privées (la réponse s'appuie sur les docs)
- `bash scripts/verify_branch_scope.sh` passe

**Budget temps** : 1h40 Core (+30 min Sprint OU 60-70 min Bonus)

---

## 🚧 Périmètre de cet atelier

- ✅ **Dans le scope** : Chunking (fixed/recursive/semantic), embeddings, FAISS, similarity search vs MMR, `k`, `fetch_k`, metadata sur chunks (`source`, `page`), Recall@k, faithfulness, answer relevance
- ❌ **Hors scope** (ateliers suivants) : EnsembleRetriever, ChromaDB, agents ReAct, fine-tuning, déploiement API
- 🛡️ **Garde-fou activé** : `.claude/CLAUDE.md` local + hook `UserPromptSubmit`
  (si tu utilises Claude/Cursor : demander "ajoute un agent ReAct" ou "utilise ChromaDB" déclenchera un refus automatique — c'est intentionnel)

---

## 🛠️ vs 🎮 — Choisis ta piste

**Déclare ta piste maintenant** :

| Critère | 🛠️ Piste Build | 🎮 Piste Vibe |
|---|---|---|
| **Outil** | Code à la main ; Claude Code en mode `plan` ou fermé | Délégation OK à Claude/Cursor |
| **Liberté** | Tu décides tout | Tu valides ce que l'IA produit |
| **Obligation Build** | Lire `homebutler/rag/ingestion.py` avant de coder | — |
| **Obligation Vibe** | (a) Expliquer chunk_size et chunk_overlap en 3 phrases | (b) Modifier `chunk_size` de 512 à 200, prédire l'effet sur Recall@5 avant de lancer |
| **Bug Hunt** | Tu trouves le bug toi-même (observe le comportement avant de lire le patch) | Tu prédis l'effet du bug avant de regarder le test |

> **Piste Vibe — obligation contractuelle pour chaque étape** :
> Avant de valider une étape générée par l'IA, tu dois être capable de répondre :
> "Qu'est-ce que `chunk_overlap` ? Quel effet a `chunk_overlap=0` sur la qualité ?"
> Si tu ne sais pas → retour au Carnet de bord avant de continuer.

---

## 🧠 Carnet de bord (concepts à mobiliser)

> Lis ce lexique avant de commencer à coder. Il sera testé dans les checkpoints.

### Embedding
Un embedding transforme un texte en vecteur de nombres (ici : 384 dimensions). Deux textes au sens proche → vecteurs proches dans l'espace géométrique.

**Analogie** : des coordonnées GPS dans un espace à 384 dimensions. "Chaudière" et "chauffage central" sont voisins (coordonnées proches). "Chaudière" et "tarte aux pommes" sont à l'opposé. La similarité cosinus entre deux vecteurs = mesure de proximité sémantique.

**Dans le projet** : `FastEmbedEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")` — modèle multilingue FR/EN, ~120 MB, téléchargé une fois dans `~/.cache/fastembed/`, pas besoin de GPU.

### Chunking
Découper un document en morceaux (chunks) pour l'indexation. Un PDF entier est trop volumineux pour être traité comme un seul vecteur.

**Analogie** : découper un livre en fiches de révision. Chaque fiche = 1 concept = 1 chunk. Si les fiches sont trop grandes (1 chapitre entier), tu noies l'information. Si elles sont trop petites (1 mot), tu perds le contexte.

**Sweet spot** : 400-800 caractères + overlap 50-100.

### Fixed-size chunking
Coupe le document tous les `chunk_size` caractères, sans tenir compte des séparateurs naturels.

**Analogie** : couper un livre en feuillets de 10 cm au ciseaux, sans regarder où finissent les phrases. Une phrase peut se retrouver coupée en plein milieu entre deux fiches.

**Code** : `chunk_fixed_size(pages, chunk_size=512, chunk_overlap=50)` dans `homebutler/rag/ingestion.py`

### Recursive chunking (recommandé)
Essaie de couper aux séparateurs naturels dans l'ordre : `\n\n` (paragraphe) → `\n` (saut de ligne) → `.` (fin de phrase) → ` ` (espace). Ne coupe "brutalement" que si aucun séparateur n'est trouvé.

**Analogie** : couper un livre aux séparateurs naturels — d'abord les chapitres, puis les paragraphes, puis les phrases, puis les mots. Résultat : des fiches qui préservent le sens.

**Code** : `chunk_recursive(pages, chunk_size=512, chunk_overlap=50)` dans `homebutler/rag/ingestion.py`

### FAISS (Facebook AI Similarity Search)
Bibliothèque qui indexe des millions de vecteurs et trouve les plus proches en quelques millisecondes via l'algorithme ANN (Approximate Nearest Neighbors).

**Analogie** : un index alphabétique ultra-rapide vs feuilleter toutes les pages d'un dictionnaire. Sans FAISS = comparer ta requête à chaque chunk un par un (O(n)). Avec FAISS = index ANN qui saute directement aux voisins proches (O(log n)).

**Dans le projet** : `build_faiss_index(chunks, force_rebuild=True)` dans `homebutler/rag/vectorstore_faiss.py`. L'index est sauvegardé dans `data/faiss_index/` et rechargé sans recalcul au prochain run.

### MMR (Maximal Marginal Relevance)
Algorithme de retrieval qui sélectionne `k` chunks à la fois pertinents ET diversifiés. `similarity_search` retourne souvent les `k` chunks les plus proches — qui peuvent être des doublons (même info répétée dans le PDF). MMR pénalise la redondance.

**Analogie** : aller à la bibliothèque chercher 4 magazines sur la "chaudière". `similarity_search` peut ramener 4 fois le même magazine (le plus populaire). MMR préfère 4 magazines différents qui couvrent le sujet sous des angles variés.

**Paramètres** : `search_type="mmr"`, `k=4` (résultats finaux), `fetch_k=20` (candidats pré-filtrés avant MMR).

### Recall@k
Sur N questions étalons pour lesquelles tu connais la bonne source, combien de fois le bon document se trouve-t-il dans les k premiers résultats du retriever ?

**Analogie** : le score de la bibliothécaire. Si tu cherches un livre sur la chaudière et qu'elle te propose 5 livres au hasard, Recall@5 = 80% signifie que dans 8 cas sur 10, le bon livre est dans ses 5 propositions.

**Formule** : `hits / total_questions` où `hits` = nombre de questions où le bon doc est dans le top-k.

**Dans le projet** : `evaluate_rag.py` calcule Recall@1/3/5 automatiquement.

### Faithfulness (fidélité)
Mesure si la réponse du LLM s'appuie réellement sur les documents récupérés (le contexte RAG), ou si elle invente. Score entre 0 et 1.

**Analogie** : noter si l'étudiant s'appuie vraiment sur ses fiches de révision dans sa réponse, ou s'il invente des passages entiers. Un étudiant fidèle = faithfulness élevée.

**Dans le projet** : `evaluate_rag.py` contient un LLM-judge de faithfulness.

---

## 🎯 TRONC COMMUN (1h40)

### Étape 1 — Charger les PDFs et comprendre le chunking (25 min)

**Objectif** : charger les PDFs HomeButler et comparer les deux stratégies de chunking.

**Indices (Build)** :
- Fichier à compléter : `ateliers/atelier-02-rag-simple/exercice.py`
- Fonction de chargement : `load_pdf_with_metadata(path)` dans `homebutler/rag/ingestion.py`
  - Retourne une liste de `Document` (1 par page PDF) avec metadata `{source, page, total_pages}`
- Boucle sur les PDFs du dossier `config.DOCUMENTS_DIR`
- Chunkers : `chunk_fixed_size(pages, chunk_size=512, chunk_overlap=50)` et `chunk_recursive(pages, ...)`

**Garde-fou (Vibe)** :
- Consigne à donner à ton agent : "Implémente les TODO 1, 2 et 3 de exercice.py. N'utilise que `homebutler/rag/ingestion.py` et `homebutler/rag/vectorstore_faiss.py`. Pas d'agent, pas de ChromaDB."
- Après génération : explique à voix haute ce que fait `chunk_overlap` (si tu ne sais pas → Carnet de bord)

**Observation attendue** :
```
Pages chargées : ~15-20 pages
chunks_fixed     : ~40-60 chunks
chunks_recursive : ~35-55 chunks (peut différer)
```

✋ **Checkpoint 1** — Lance `python ateliers/atelier-02-rag-simple/checkpoints/check_1.py`

→ Score ≥ 2/3 : continue vers Étape 2
→ Score < 2/3 : relis le Carnet de bord (Embedding, Chunking, Fixed vs Recursive), retente

---

### 🔬 Mini-lab — Fixed-size vs Recursive sur les 5 questions étalons (15 min)

**Variable** : stratégie de chunking (`chunk_fixed_size` vs `chunk_recursive`)
**Plage** : les deux stratégies avec `chunk_size=512, chunk_overlap=50`

**Protocole** :
1. Construis 2 index FAISS : un sur `chunks_fixed`, un sur `chunks_rec`
2. Pour chaque index, lance `similarity_search(question, k=5)` sur les 5 questions étalons
3. Note le Recall@5 de chaque stratégie :

| Stratégie | Recall@5 | Nombre de chunks |
|---|---|---|
| fixed-size | ? | ? |
| recursive | ? | ? |

**Questions à te poser** :
- Quelle stratégie donne le meilleur Recall@5 sur ces PDFs ?
- Pourquoi le nombre de chunks diffère entre les deux stratégies ?
- Un Recall@5 plus élevé correspond-il toujours à plus de chunks ?

---

### Étape 2 — Construire l'index FAISS et le retriever (30 min)

**Objectif** : construire un index FAISS persistant et configurer le retriever MMR.

**Indices (Build)** :
- `build_faiss_index(chunks, force_rebuild=True)` → construit ET sauvegarde l'index
- Rechargement sans recalcul : `build_faiss_index(chunks, force_rebuild=False)` (si index existe)
- Retriever MMR :
  ```python
  retriever = faiss_store.as_retriever(
      search_type="mmr",
      search_kwargs={"k": 4, "fetch_k": 20},
  )
  ```
- Chaîne LCEL :
  ```python
  rag_chain = (
      {"context": retriever | format_docs, "question": RunnablePassthrough()}
      | RAG_QA_TEMPLATE | llm | StrOutputParser()
  )
  ```

**Garde-fou (Vibe)** :
- Avant de valider le code généré : change `k=4` en `k=1` et prédit l'effet sur Recall@5
- Consigne : "Ne reconstruit pas l'index à chaque requête — sauvegarde-le et recharge-le si déjà présent"

**Observation attendue** :
```
Construction de l'index FAISS (N chunks)...
Index FAISS sauvegardé dans data/faiss_index/

Question : Quelle est la marque de ma chaudière ?
→ [notice_chaudiere.pdf p.1]
  La chaudière Viessmann Vitodens 100-W...
```

---

### 🐛 Casse-moi ça — Bug Hunt (20 min)

**3 bugs à débusquer.** Applique chaque patch, observe le comportement, répare, valide avec pytest.

**Bug v1 — chunk_size=2000 (trop grand → bruit)**

```bash
git apply ateliers/atelier-02-rag-simple/bugs/v1.patch
pytest ateliers/atelier-02-rag-simple/bugs/test_v1.py -v   # doit ECHOUER
# Observe : le Recall@5 chute. Pourquoi ?
# Répare : change chunk_size dans les appels chunk_recursive/chunk_fixed_size
pytest ateliers/atelier-02-rag-simple/bugs/test_v1.py -v   # doit PASSER
```

Lis `bugs/v1_explanation.md`.

**Bug v2 — chunk_overlap=0 (coupure phrase → info perdue)**

```bash
git apply ateliers/atelier-02-rag-simple/bugs/v2.patch
pytest ateliers/atelier-02-rag-simple/bugs/test_v2.py -v
# Observe : certaines questions perdent des informations à la frontière des chunks
# Répare : restaure chunk_overlap=50
pytest ateliers/atelier-02-rag-simple/bugs/test_v2.py -v
```

Lis `bugs/v2_explanation.md`.

**Bug v3 — reconstruction index à chaque query (latence catastrophique)**

```bash
git apply ateliers/atelier-02-rag-simple/bugs/v3.patch
pytest ateliers/atelier-02-rag-simple/bugs/test_v3.py -v
# Observe : la latence passe de < 1s à > 5s par requête
# Répare : construire l'index une fois, le réutiliser pour toutes les requêtes
pytest ateliers/atelier-02-rag-simple/bugs/test_v3.py -v
```

Lis `bugs/v3_explanation.md`.

> **Règle anti-cheat** : tu peux demander à l'IA de t'expliquer le comportement observé, mais pas "trouve le bug dans le patch". La déduction depuis le symptôme est le coeur de l'apprentissage.

---

### 📊 Mesure-toi (15 min)

Utilise `evaluate_rag.py` pour mesurer tes métriques réelles :

```bash
python ateliers/atelier-02-rag-simple/evaluate_rag.py
```

Remplis ce tableau avec tes résultats :

| Métrique | Valeur observée | Cible |
|---|---|---|
| **Recall@1** | ___% | — |
| **Recall@3** | ___% | ≥ 60% |
| **Recall@5** | ___% | ≥ 80% |
| **Latence retrieval** (moyenne) | ___s | < 1s |
| **Contexte size** (chars injectés dans le prompt) | ~___ chars | < 4000 |
| **Faithfulness** (via LLM-judge) | ___/1.0 | ≥ 0.85 |

**Interprétation** :
- Si Recall@5 < 80% → essaie de réduire `chunk_size` (de 512 à 400) ou augmenter `k` (de 4 à 6)
- Si latence > 1s → vérifie que l'index n'est pas reconstruit à chaque requête (`force_rebuild=False`)
- Si faithfulness < 0.85 → le LLM "invente" au-delà du contexte ; vérifie le prompt template `RAG_QA_TEMPLATE`

**Baseline de référence** : Recall@5 ≈ 80% est atteignable sur les PDFs HomeButler avec chunking récursif, chunk_size=512, k=4, MMR.

✋ **Checkpoint final Core** — lance `python ateliers/atelier-02-rag-simple/checkpoints/check_final.py`

→ Score ≥ 4/5 (80%) : pars en **Bonus** 🏆
→ Score < 3/5 (< 60%) : pars en **Sprint** ⚡
→ Entre 60% et 80% : relis le concept raté (Carnet de bord), puis Bonus

---

## ⚡ SPRINT (chemin alternatif, 30 min)

> Tu es ici parce que le score checkpoint < 60%, ou parce que tu as pris du retard.

**Sprint 1 — Chunking et chunk_overlap (15 min)**

Ouvre `homebutler/rag/ingestion.py`. Lis les fonctions `chunk_fixed_size` et `chunk_recursive`.

Exercice : chunke manuellement cette phrase en 2 chunks de 30 caractères avec overlap=10 :
```
"La chaudière Viessmann est une chaudière à condensation gaz."
```
Chunk 1 : ? (caractères 0-30)
Chunk 2 : ? (caractères 20-50 — overlap de 10 caractères avec le chunk 1)

Question à répondre par écrit : "Pourquoi un overlap=0 peut faire perdre des informations importantes ?"

**Sprint 2 — FAISS et sauvegarde (15 min)**

Ouvre `homebutler/rag/vectorstore_faiss.py`. Lis les fonctions `build_faiss_index` et `load_faiss_index`.

Exercice : écris 2 lignes de code qui :
1. Construisent l'index si `data/faiss_index/` n'existe pas (`force_rebuild=True`)
2. Rechargent l'index si `data/faiss_index/` existe (`force_rebuild=False`)

Teste que ta 2ème requête est plus rapide que la 1ère (l'index est rechargé depuis le disque).

---

## 🏆 BONUS (parcours alternatif, 60-70 min)

> Tu es ici parce que score ≥ 80%. Bienvenue dans les défis avancés.
> Tous les défis restent dans le scope At.02 — pas d'EnsembleRetriever, pas de ChromaDB.

### Défi Bonus 1 — Faire varier chunk_size : trouver le sweet spot

**POURQUOI cette question ?**
`chunk_size` est le paramètre le plus influent sur Recall@k dans un pipeline RAG simple. Trop grand = bruit dans le contexte. Trop petit = contexte mutilé, informations perdues. Il n'existe pas de valeur universelle — ça dépend du corpus.

**Contexte**
Le projet HomeButler utilise des PDFs de notices techniques et de documents juridiques (bail). Ces deux types de documents ont des structures différentes : notices = données structurées courtes (tableaux de codes erreur) ; bail = prose légale longue.

**Question**
> Pour les 5 questions étalons, teste `chunk_size` ∈ {200, 600, 1500} avec `chunk_overlap=50` et `chunk_recursive`. Pour chaque valeur : Recall@5, nombre de chunks, latence d'ingestion. Quelle valeur maximise Recall@5 × contexte size raisonnable ?

**Protocole** :
```python
for chunk_size in [200, 600, 1500]:
    chunks = chunk_recursive(pages, chunk_size=chunk_size, chunk_overlap=50)
    store = build_faiss_index(chunks, force_rebuild=True)
    # mesure Recall@5...
    print(f"chunk_size={chunk_size} → {len(chunks)} chunks, Recall@5={...}")
```

**Mesure** : remplis un tableau `chunk_size × (Recall@5, nb_chunks, latence_ingestion)`.

**Pistes de réflexion** :
- À quel moment le Recall@5 commence-t-il à baisser si `chunk_size` est trop petit ?
- La notice chaudière (données structurées) et le bail (prose) réagissent-ils différemment à la variation de `chunk_size` ?
- Quel est le coût en tokens (taille du contexte injecté dans le LLM) pour `chunk_size=200` vs `chunk_size=1500` ?

---

### Défi Bonus 2 — MMR vs similarity : diversité et couverture

**POURQUOI cette question ?**
MMR (Maximal Marginal Relevance) est présenté comme "meilleur" que la similarity brute pour la diversité. Mais est-ce toujours vrai sur le corpus HomeButler ? Sur certaines questions, on veut 4 chunks du même document (ex: "purger un radiateur" = toutes les étapes sont dans la même notice). Sur d'autres, on veut de la diversité.

**Contexte**
- `search_type="similarity"` : retourne les 4 chunks les plus proches, sans pénaliser les doublons
- `search_type="mmr"` avec `fetch_k=20` : pré-filtre 20 candidats, puis sélectionne les 4 les plus pertinents ET diversifiés

**Question**
> Pour les 5 questions étalons, compare `similarity` vs `MMR` (fetch_k=20) sur Recall@5 et sur la diversité des sources (combien de PDFs différents dans le top-5). Y a-t-il des questions pour lesquelles similarity est meilleur que MMR ?

**Pistes de réflexion** :
- Sur "Comment purger les radiateurs ?" (réponse = plusieurs étapes dans la même notice) : similarity ou MMR donne un meilleur contexte pour le LLM ?
- Sur "Quelle est la durée du bail et quelle est la marque de la chaudière ?" (question multi-source) : lequel des deux couvre mieux ?
- `fetch_k` influence-t-il le Recall@5 ? Teste `fetch_k ∈ {10, 20, 50}`.

---

## 🎓 Wrap-up (10 min)

**Checklist de fin** :
- [ ] `python evaluate_rag.py` affiche Recall@5 ≥ 0.80
- [ ] La réponse à "Quelle est la marque de ma chaudière ?" cite `notice_chaudiere.pdf`
- [ ] Les 3 bugs du Bug Hunt réparés et testés (3× `pytest` vert)
- [ ] `bash scripts/verify_branch_scope.sh` passe
- [ ] Checkpoint final ≥ 60%

**Quiz oral chronométré (5 min, 10 questions)** — Réponds sans relire le guide :

1. Qu'est-ce qu'un embedding ?
2. Pourquoi découper en chunks plutôt que d'envoyer le PDF entier ?
3. Quelle est la différence entre fixed-size et recursive chunking ?
4. Qu'est-ce que FAISS ?
5. Pourquoi MMR évite-t-il les doublons dans le top-k ?
6. Que mesure Recall@5 ?
7. Qu'est-ce que la faithfulness ?
8. Pourquoi ne faut-il pas reconstruire l'index FAISS à chaque requête ?
9. Que signifie "chunk_overlap=50" ?
10. Quelle valeur de chunk_size recommandes-tu pour les PDFs HomeButler, et pourquoi ?

→ Score ≥ 8/10 : prêt pour l'atelier 03 (Pipeline Agent).
→ Score 5-7/10 : relis le Carnet de bord des concepts ratés.
→ Score < 5/10 : refais le Sprint avant l'atelier 03.

**Ce que je retiens en 3 lignes** (à écrire — utile pour l'atelier 03) :
```
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________
```

---

## 🔗 Pour aller plus loin (hors TP, lecture)

**Pont avec ton projet** : dans tout projet qui expose un RAG à des utilisateurs, le Recall@k est le plafond de qualité. Si le retriever rate 20% des questions (Recall@5=80%), le LLM ne peut pas répondre correctement dans ces cas — même avec le meilleur modèle. Investir dans le chunking et le retrieval avant d'investir dans le modèle.

**Avertissements communautaires à retenir** :
- Warning fastembed "mean pooling instead of CLS embedding" → normal depuis fastembed >= 0.5.2, ignorer
- FAISS sur ARM Mac : si `pip install faiss-cpu` échoue → `pip install faiss-cpu --upgrade`
- Ne jamais mélanger des embeddings de langues différentes sans modèle multilingue

**Lectures complémentaires** :
- RAGAS (Es et al. 2024, EACL) — framework d'évaluation RAG : https://arxiv.org/abs/2309.15217
- Anthropic Cookbook — Contextual Retrieval : https://platform.claude.com/cookbook/capabilities-contextual-embeddings-guide
- LangChain docs — RecursiveCharacterTextSplitter et FAISS retriever
