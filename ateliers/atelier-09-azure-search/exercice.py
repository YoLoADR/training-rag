"""
═══════════════════════════════════════════════════════════════════════════
Atelier 09 — Azure AI Search (exercice à compléter)
═══════════════════════════════════════════════════════════════════════════

Tu passes du vector store LOCAL (FAISS) à Azure AI Search (managé, cloud).
Concept clé : control plane (CLI `az search`) vs data plane (SDK Python).

Tu codes 3 fonctions dans  homebutler/rag/vectorstore_azure.py :
  1. build_index_schema()  — schéma d'index vectoriel (dim 384, content searchable)
  2. get_azure_store()     — AzureSearch (search_type "hybrid" par défaut)
  3. azure_search()        — requête en 3 modes

Puis complète les TODO ci-dessous.

Pré-requis : az login + bash ateliers/atelier-09-azure-search/azure_provision.sh
Lancer :  python ateliers/atelier-09-azure-search/exercice.py
═══════════════════════════════════════════════════════════════════════════
"""

import os

from homebutler import config
from homebutler.rag.ingestion import load_pdf_with_metadata, chunk_recursive
from homebutler.rag.retriever import get_faiss_retriever

# TODO 1 — importer tes fonctions depuis homebutler/rag/vectorstore_azure.py
# from homebutler.rag.vectorstore_azure import create_index, ingest_documents, azure_search

QUESTIONS = [
    ("Quelle est la marque de ma chaudière ?",         "notice_chaudiere.pdf"),
    ("Mon linge ressort trempé",                       "notice_lave_linge.pdf"),
    ("Jusqu'à quelle heure je peux faire du bruit ?",  "reglement_copropriete.pdf"),
    ("Quelle est la durée du bail ?",                  "bail_location.pdf"),
]


def _load_chunks() -> list:
    docs_dir = config.DOCUMENTS_DIR
    if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
        print("PDFs absents — lancer : python scripts/generate_documents.py")
        raise SystemExit(1)
    pages = []
    for f in sorted(os.listdir(docs_dir)):
        if f.endswith(".pdf"):
            pages.extend(load_pdf_with_metadata(os.path.join(docs_dir, f)))
    return chunk_recursive(pages, chunk_size=512, chunk_overlap=50)


def main() -> None:
    if not config.AZURE_SEARCH_ENDPOINT or not config.AZURE_SEARCH_KEY:
        print("Service Azure non configuré — lance : az login && bash .../azure_provision.sh")
        raise SystemExit(1)

    # ─── TODO 2 — créer l'index (schéma manuel) puis ingérer le corpus ──────
    # create_index()
    # n = ingest_documents(_load_chunks())
    # print(f"{n} chunks ingérés")
    raise NotImplementedError("TODO 2 — create_index + ingest_documents")

    # ─── TODO 3 — requêter en 'similarity' puis 'hybrid' et comparer à FAISS ─
    # for q, expected in QUESTIONS:
    #     for mode in ("similarity", "hybrid"):
    #         docs = azure_search(q, k=4, search_type=mode)
    #         ...
    # → quelle différence similarity vs hybrid sur le vocabulaire divergent ?


if __name__ == "__main__":
    main()
