"""
Vectorstore FAISS — documents statiques (notices, bail, DPE).

Concept RAG : FAISS est une bibliothèque de recherche de voisins approximatifs
(ANN — Approximate Nearest Neighbors) développée par Meta. Elle indexe des
vecteurs (embeddings) et retrouve les plus proches en O(log n) au lieu de O(n).
Pour ~10k documents, FAISS répond en quelques millisecondes au lieu de secondes.

Index FAISS = fichier binaire sauvegardé sur disque (data/faiss_index/).

═══════════════════════════════════════════════════════════════════════════
🎓 Atelier 02 — Tu dois compléter les 3 fonctions ci-dessous.
   Solution finale (en dernier recours) :
   git diff student/02-rag-simple atelier/02-rag-simple -- homebutler/rag/vectorstore_faiss.py
═══════════════════════════════════════════════════════════════════════════
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.documents import Document
from homebutler import config

# ═══════════════════════════════════════════════════════════════════════════
# CONCEPT RAG : Modèle d'embeddings
# ───────────────────────────────────────────────────────────────────────────
# Un embedding transforme un texte en vecteur de 384 nombres (dimensions).
# Deux textes proches sémantiquement → vecteurs proches géométriquement.
# Analogie : un "code-barres sémantique" du sens de la phrase.
# Ce modèle multilingue (FR/EN/...) est quantisé ONNX → léger, pas besoin
# de torch ni GPU. Téléchargé une fois dans ~/.cache/fastembed/ (~300 MB).
# ═══════════════════════════════════════════════════════════════════════════
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def get_embeddings() -> FastEmbedEmbeddings:
    """
    Retourne le modèle d'embeddings (mis en cache localement).

    Returns:
        Une instance de `FastEmbedEmbeddings` prête à encoder du texte.

    --- Indice léger ---
    LangChain expose une classe `FastEmbedEmbeddings` (déjà importée en haut)
    qui prend simplement un `model_name`. La constante `EMBEDDING_MODEL`
    définie ci-dessus contient le nom exact à utiliser.

    --- Indice fort ---
    Une seule ligne : `return FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)`
    """
    raise NotImplementedError(
        "Atelier 02 § 2.3 — modèle d'embeddings. "
        "Solution finale : git diff student/02-rag-simple atelier/02-rag-simple -- homebutler/rag/vectorstore_faiss.py"
    )


def build_faiss_index(
    documents: list[Document],
    save_path: str | None = None,
    force_rebuild: bool = False,
) -> FAISS:
    """
    Construit (ou recharge) un index FAISS depuis une liste de chunks.

    Concept : `FAISS.from_documents` calcule l'embedding de chaque chunk
    puis l'insère dans l'index. La similarité par défaut = cosinus normalisé.

    Args:
        documents: chunks à indexer (output d'un splitter).
        save_path: chemin sur disque (défaut = config.FAISS_PATH).
        force_rebuild: True = rebuild même si index existant.

    Returns:
        Une instance FAISS prête pour `.similarity_search(query, k=...)`.

    --- Indice léger ---
    Si un index existe déjà sur disque (`os.path.exists(path)`) et
    qu'on ne force pas le rebuild, on RECHARGE — la fonction
    `load_faiss_index(path)` est ton amie ici.
    Sinon, on construit : il faut un modèle d'embeddings (ta fonction
    `get_embeddings()` ci-dessus) puis la méthode statique de FAISS
    qui prend `(documents, embeddings)` et renvoie un vectorstore.
    Penser à sauver sur disque avec `vectorstore.save_local(path)`.

    --- Indice fort ---
    1. `path = save_path or config.FAISS_PATH`
    2. Si `os.path.exists(path) and not force_rebuild` :
       `print(f"  Index FAISS existant chargé depuis {path}")`
       `return load_faiss_index(path)`
    3. Sinon :
       `print(f"  Construction de l'index FAISS ({len(documents)} chunks)...")`
       `embeddings = get_embeddings()`
       `vectorstore = FAISS.from_documents(documents, embeddings)`
       `vectorstore.save_local(path)`
       `print(f"  ✓ Index FAISS sauvegardé dans {path}")`
       `return vectorstore`
    """
    raise NotImplementedError(
        "Atelier 02 § 2.4 — construction index FAISS. "
        "Solution finale : git diff student/02-rag-simple atelier/02-rag-simple -- homebutler/rag/vectorstore_faiss.py"
    )


def load_faiss_index(path: str | None = None) -> FAISS:
    """
    Charge un index FAISS depuis le disque.

    Args:
        path: chemin de l'index (défaut = config.FAISS_PATH).

    Returns:
        Une instance FAISS rechargée.

    --- Indice léger ---
    FAISS expose une méthode de classe `FAISS.load_local(path, embeddings, ...)`.
    Attention : depuis LangChain 0.1.x, il faut explicitement passer
    `allow_dangerous_deserialization=True` car FAISS utilise pickle
    (qui peut exécuter du code à la lecture — OK ici car c'est NOTRE fichier).

    --- Indice fort ---
    1. `path = path or config.FAISS_PATH`
    2. `embeddings = get_embeddings()`
    3. `return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)`
    """
    raise NotImplementedError(
        "Atelier 02 § 2.5 — rechargement index FAISS. "
        "Solution finale : git diff student/02-rag-simple atelier/02-rag-simple -- homebutler/rag/vectorstore_faiss.py"
    )
