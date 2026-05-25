"""
Pipeline d'ingestion des documents PDF.
Expose 3 stratégies de chunking pour la comparaison pédagogique :
  1. chunk_fixed_size  — taille fixe (512 tokens)
  2. chunk_recursive   — récursif par séparateurs (§, \n, .)
  3. chunk_semantic    — rupture sur similarité sémantique (langchain_experimental)

═══════════════════════════════════════════════════════════════════════════
🎓 Atelier 02 — Tu dois compléter les 3 fonctions de chunking ci-dessous.
   Solution finale (en dernier recours) :
   git diff student/02-rag-simple atelier/02-rag-simple -- homebutler/rag/ingestion.py
═══════════════════════════════════════════════════════════════════════════
"""

import os
import fitz  # pymupdf — s'installe `pip install pymupdf` mais s'importe `import fitz`
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from homebutler import config


# ── Chargement PDF (DÉJÀ FOURNI — lecture seule) ─────────────────────────────

def load_pdf(path: str) -> str:
    """Extrait le texte brut d'un PDF (toutes pages)."""
    doc = fitz.open(path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)


def load_pdf_with_metadata(path: str) -> list[Document]:
    """Extrait le texte page par page avec métadonnées (source, page)."""
    doc = fitz.open(path)
    documents = []
    filename = os.path.basename(path)
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": filename, "page": i + 1, "total_pages": len(doc)},
                )
            )
    doc.close()
    return documents


# ── Stratégies de chunking (À COMPLÉTER) ─────────────────────────────────────

def chunk_fixed_size(
    documents: list[Document],
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> list[Document]:
    """
    Stratégie 1 — Taille fixe.
    Simple et rapide, mais peut couper au milieu d'une phrase ou d'un concept.
    Bon pour les documents uniformes (logs, tableaux).

    Args:
        documents: liste de Document (1 par page de PDF).
        chunk_size: taille cible du chunk en caractères.
        chunk_overlap: chevauchement entre chunks consécutifs (préserve continuité).

    Returns:
        Liste de Document chunkés (métadonnées source/page propagées par LangChain).

    --- Indice léger ---
    LangChain expose un text splitter qui découpe sur UN seul séparateur en
    visant `chunk_size` caractères. On veut ici un découpage "bête et naïf"
    qui coupe sur les retours à la ligne `\\n` quand c'est possible.

    --- Indice fort ---
    1. Instancie `CharacterTextSplitter` (déjà importé en haut du fichier) avec :
       - `chunk_size=chunk_size`
       - `chunk_overlap=chunk_overlap`
       - `separator="\\n"`  (un seul caractère — c'est la marque du "fixed")
       - `length_function=len`
    2. Appelle sa méthode `.split_documents(documents)` et renvoie le résultat.
    """
    raise NotImplementedError(
        "Atelier 02 § 2.2 — chunking fixed-size. "
        "Solution finale : git diff student/02-rag-simple atelier/02-rag-simple -- homebutler/rag/ingestion.py"
    )


def chunk_recursive(
    documents: list[Document],
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> list[Document]:
    """
    Stratégie 2 — Récursif par séparateurs (recommandée pour la plupart des docs).
    Essaie de couper sur \\n\\n, puis \\n, puis ., puis espace.
    Préserve mieux la cohérence sémantique des paragraphes.

    Args:
        documents: pages chargées via PyPDFLoader / fitz (1 page = 1 Document).
        chunk_size: taille cible du chunk en caractères.
        chunk_overlap: chevauchement entre chunks consécutifs.

    Returns:
        Liste de Document chunkés, métadonnées préservées.

    --- Indice léger ---
    LangChain expose une classe dont le nom commence par `Recursive…Splitter`
    (déjà importée en haut du fichier). Le découpage « récursif » signifie :
    essayer le séparateur le plus large (paragraphe `\\n\\n`), puis plus fin
    (ligne `\\n`), puis plus fin encore (`.`, `!`, `?`, espace, vide).

    --- Indice fort ---
    1. Instancie le splitter avec `chunk_size`, `chunk_overlap`, et une liste
       `separators` ORDONNÉE du plus large au plus fin :
       `["\\n\\n", "\\n", ".", "!", "?", " ", ""]`
    2. Passe `length_function=len` (mesure en caractères, pas en tokens).
    3. Appelle `.split_documents(documents)`.
    """
    raise NotImplementedError(
        "Atelier 02 § 2.2 — chunking récursif. "
        "Solution finale : git diff student/02-rag-simple atelier/02-rag-simple -- homebutler/rag/ingestion.py"
    )


def chunk_semantic(
    documents: list[Document],
    embeddings=None,
    breakpoint_threshold_type: str = "percentile",
) -> list[Document]:
    """
    Stratégie 3 — Sémantique (rupture sur similarité cosinus).
    Nécessite le modèle d'embeddings chargé.
    Plus lent mais produit des chunks thématiquement cohérents.
    Utilise langchain_experimental.SemanticChunker.

    Args:
        documents: pages chargées.
        embeddings: modèle d'embeddings (si None, charge celui par défaut).
        breakpoint_threshold_type: méthode de détection de rupture
            ("percentile" | "standard_deviation" | "interquartile").

    Returns:
        Liste de Document chunkés selon les ruptures sémantiques détectées.

    --- Indice léger ---
    La classe vient de `langchain_experimental.text_splitter`
    (à importer DANS la fonction, pas en haut, car c'est un package optionnel).
    Si `embeddings` est None, récupère-le via `get_embeddings()` du
    module `homebutler.rag.vectorstore` (déjà câblé sur FastEmbed).
    Le chunker ne prend pas de liste de Document directement : il faut
    extraire `page_content` et `metadata` séparément.

    --- Indice fort ---
    1. `from langchain_experimental.text_splitter import SemanticChunker`
    2. Si `embeddings is None`, importe et appelle
       `from homebutler.rag.vectorstore import get_embeddings; embeddings = get_embeddings()`
    3. Instancie `SemanticChunker(embeddings, breakpoint_threshold_type=breakpoint_threshold_type)`
    4. Construis deux listes parallèles :
       `texts = [d.page_content for d in documents]`
       `metadatas = [d.metadata for d in documents]`
    5. Appelle `.create_documents(texts, metadatas=metadatas)` et renvoie le résultat.
    """
    raise NotImplementedError(
        "Atelier 02 § 2.2 — chunking sémantique. "
        "Solution finale : git diff student/02-rag-simple atelier/02-rag-simple -- homebutler/rag/ingestion.py"
    )


# ── Pipeline d'ingestion complète (DÉJÀ FOURNI — orchestre tes 3 chunkers) ──

def ingest_all_documents(
    docs_dir: str | None = None,
    strategy: str = "recursive",
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> list[Document]:
    """
    Charge tous les PDFs du dossier et les chunke.
    strategy : "fixed" | "recursive" | "semantic"
    """
    docs_dir = docs_dir or config.DOCUMENTS_DIR

    if not os.path.exists(docs_dir):
        raise FileNotFoundError(
            f"Dossier documents introuvable : {docs_dir}\n"
            "Lancez d'abord : python scripts/generate_documents.py"
        )

    all_documents: list[Document] = []
    pdf_files = [f for f in os.listdir(docs_dir) if f.endswith(".pdf")]

    if not pdf_files:
        raise ValueError(f"Aucun PDF trouvé dans {docs_dir}")

    for filename in sorted(pdf_files):
        path = os.path.join(docs_dir, filename)
        pages = load_pdf_with_metadata(path)
        all_documents.extend(pages)

    print(f"  {len(pdf_files)} PDFs chargés → {len(all_documents)} pages")

    if strategy == "fixed":
        chunks = chunk_fixed_size(all_documents, chunk_size, chunk_overlap)
    elif strategy == "semantic":
        chunks = chunk_semantic(all_documents)
    else:  # recursive (défaut)
        chunks = chunk_recursive(all_documents, chunk_size, chunk_overlap)

    print(f"  Stratégie '{strategy}' → {len(chunks)} chunks")
    return chunks
