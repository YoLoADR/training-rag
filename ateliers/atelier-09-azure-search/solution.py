"""
═══════════════════════════════════════════════════════════════════════════
Atelier 09 — Azure AI Search (solution corrigée + commentaires)
═══════════════════════════════════════════════════════════════════════════

On passe du vector store LOCAL (FAISS, AT02) à un vector store MANAGÉ en cloud
(Azure AI Search). Concept central : control plane (CLI `az search`) vs data plane
(SDK Python : index, vecteurs, ingestion, requêtes).

Pré-requis :
  - service Azure provisionné : bash ateliers/atelier-09-azure-search/azure_provision.sh
    (écrit AZURE_SEARCH_ENDPOINT / AZURE_SEARCH_KEY dans .env)
  - corpus PDF : python scripts/generate_documents.py
  - embeddings fastembed (384d) — réutilisés d'AT02, 0 coût token

Lancer : python ateliers/atelier-09-azure-search/solution.py
Nettoyer : bash ateliers/atelier-09-azure-search/azure_teardown.sh
═══════════════════════════════════════════════════════════════════════════
"""

import os

from homebutler import config
from homebutler.rag.ingestion import load_pdf_with_metadata, chunk_recursive
from homebutler.rag.vectorstore_faiss import build_faiss_index
from homebutler.rag.retriever import get_faiss_retriever
from homebutler.rag.vectorstore_azure import (
    create_index, ingest_documents, azure_search, AZURE_VECTOR_DIM,
)

QUESTIONS = [
    ("Quelle est la marque de ma chaudière ?",            "notice_chaudiere.pdf"),
    ("Mon linge ressort trempé",                          "notice_lave_linge.pdf"),
    ("Jusqu'à quelle heure je peux faire du bruit ?",     "reglement_copropriete.pdf"),
    ("Quelle est la durée du bail ?",                     "bail_location.pdf"),
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
        print("Service Azure non configuré — lance d'abord :")
        print("  az login && bash ateliers/atelier-09-azure-search/azure_provision.sh")
        raise SystemExit(1)

    print(f"Index cible : {config.AZURE_SEARCH_INDEX}  (dim vectorielle = {AZURE_VECTOR_DIM})")

    # ═══════════════════════════════════════════════════════════════════
    # DATA PLANE 1/3 : créer le SCHÉMA d'index à la main (SDK, pas `az search`)
    # ──────────────────────────────────────────────────────────────────
    # Champs : id, content (searchable BM25), content_vector (384d), metadata.
    # La dimension DOIT matcher l'embedding fastembed (384) — sinon upload rejeté.
    # ═══════════════════════════════════════════════════════════════════
    create_index()
    print("  ✓ Index créé/à jour")

    # ═══════════════════════════════════════════════════════════════════
    # DATA PLANE 2/3 : ingérer (push API). LangChain embedde puis upload.
    # ═══════════════════════════════════════════════════════════════════
    chunks = _load_chunks()
    n = ingest_documents(chunks)
    print(f"  ✓ {n} chunks ingérés dans Azure AI Search")

    # ═══════════════════════════════════════════════════════════════════
    # DATA PLANE 3/3 : requêter en 3 modes et comparer à FAISS local
    # ──────────────────────────────────────────────────────────────────
    # similarity   = vecteur pur
    # hybrid       = vecteur + BM25 (fusion RRF) — rattrape le vocabulaire divergent
    # semantic_hybrid = + semantic ranker (tier Basic+, semantic config requise)
    # ═══════════════════════════════════════════════════════════════════
    faiss_ret = get_faiss_retriever(k=4) if os.path.exists(config.FAISS_PATH) else None

    print("\n" + "═" * 60)
    for q, expected in QUESTIONS:
        print(f"\nQ: {q}   (attendu: {expected})")
        for mode in ("similarity", "hybrid"):
            docs = azure_search(q, k=4, search_type=mode)
            srcs = [d.metadata.get("source") or d.metadata.get("metadata", "?") for d in docs]
            hit = "✓" if any(expected in str(s) for s in srcs) else "✗"
            print(f"   Azure {mode:10} {hit}  → {srcs[:3]}")
        if faiss_ret:
            fdocs = faiss_ret.invoke(q)
            fsrcs = [d.metadata.get("source") for d in fdocs]
            fhit = "✓" if expected in fsrcs else "✗"
            print(f"   FAISS local       {fhit}  → {fsrcs[:3]}")

    print("\n" + "═" * 60)
    print("Comparaison faite. Pense à libérer les ressources :")
    print("  bash ateliers/atelier-09-azure-search/azure_teardown.sh")


if __name__ == "__main__":
    main()
