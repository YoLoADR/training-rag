# ⚡ Atelier 02 — Quick-Start (1 page)

> **Objectif** : indexer 5 PDFs et obtenir `Recall@5 ≥ 0.80 ET Faithfulness ≥ 0.85`.

## 🚦 Pré-vol (5 min)
```bash
bash scripts/check_atelier_ready.sh 02   # vérifie env + modèles
ls data/raw/*.pdf                        # 5 PDFs attendus
```

## 🍳 Recette de cuisine — 6 étapes

| # | Étape | Fichier | Vulgarisation |
|---|---|---|---|
| **1** | **Charger les PDFs** (déjà fourni) | `homebutler/rag/ingestion.py` → `load_pdf_with_metadata` | _metadata_ = infos associées au texte (nom du fichier, n° de page) |
| **2** | **Découper en chunks** (À CODER) | `homebutler/rag/ingestion.py` → `chunk_recursive` | _chunk_ = morceau (~500 caractères) · _chunking récursif_ = couper aux séparateurs naturels (paragraphe → ligne → phrase) au lieu de trancher brutalement. Params : `chunk_size=512`, `chunk_overlap=50` |
| **3** | **Vectoriser** (À CODER) | `homebutler/rag/vectorstore_faiss.py` → `get_embeddings` | _embedding_ = vecteur de 384 nombres qui résume le sens du texte (un « code-barres sémantique ») |
| **4** | **Indexer avec FAISS** (À CODER) | `homebutler/rag/vectorstore_faiss.py` → `build_faiss_index` | _FAISS_ = bibliothèque qui retrouve les vecteurs les plus proches en quelques ms (au lieu de comparer un par un) |
| **5** | **Interroger l'index** (déjà cadré) | `ateliers/atelier-02-rag-simple/exercice.py` | _similarity search_ = calcule la proximité query↔chunks ; `k=4` = retourne 4 chunks |
| **6** | **Mesurer la qualité** | `python ateliers/atelier-02-rag-simple/evaluate_rag.py` | 🎯 cible : Recall@5 ≥ 0.80 ET Faithfulness ≥ 0.85 |

## 🛟 Bloqué > 15 min ?
1. Relis l'indice **léger** dans la docstring de la fonction concernée.
2. Lis l'indice **fort** (juste en dessous dans la même docstring).
3. Pose la question à voix haute : « quel objet LangChain découpe un texte sur plusieurs séparateurs ? »
4. En dernier recours :
   ```bash
   git diff student/02-rag-simple atelier/02-rag-simple -- <fichier>
   ```

## ✅ Validation
```bash
pytest ateliers/atelier-02-rag-simple/   # vert = tronc commun OK
python ateliers/atelier-02-rag-simple/checkpoints/check_1.py   # QCM
python ateliers/atelier-02-rag-simple/evaluate_rag.py          # métriques cibles
```
