"""
═══════════════════════════════════════════════════════════════════════════
Atelier 08 — Optimisation du pipeline RAG (exercice à compléter)
═══════════════════════════════════════════════════════════════════════════

Objectif : ajouter un reranking cross-encoder + multi-query au retrieval d'AT02,
et MESURER le gain (Recall@k, MRR) face à la baseline FAISS.

Tu codes 3 fonctions dans  homebutler/rag/reranking.py :
  1. get_reranked_retriever()   — ContextualCompressionRetriever + FlashrankRerank
  2. get_multiquery_retriever()  — MultiQueryRetriever.from_llm(...)
  3. get_hyde_chain()            — chaîne LCEL (bonus)

Puis tu complètes les TODO ci-dessous pour comparer baseline vs reranked.

Lancer :  python ateliers/atelier-08-optimisation/exercice.py
═══════════════════════════════════════════════════════════════════════════
"""

import os

from homebutler import config
from homebutler.rag.ingestion import load_pdf_with_metadata, chunk_recursive
from homebutler.rag.vectorstore_faiss import build_faiss_index
from homebutler.rag.retriever import get_faiss_retriever

# TODO 1 — importer tes fonctions depuis homebutler/rag/reranking.py
# from homebutler.rag.reranking import get_reranked_retriever, get_multiquery_retriever


# Questions en langage NATUREL/INDIRECT : c'est là que le reranking se voit.
BENCHMARK_QUESTIONS = [
    ("L'eau du chauffage est froide en bas des radiateurs, je fais quoi ?", "notice_chaudiere.pdf"),
    ("Ma machine à laver affiche un truc bizarre",                          "notice_lave_linge.pdf"),
    ("Combien je récupère de caution en partant ?",                         "bail_location.pdf"),
    ("Est-ce que je peux avoir un chien ?",                                 "reglement_copropriete.pdf"),
    ("C'est quoi la lettre énergie de l'appart ?",                          "dpe.pdf"),
    ("L'air est confiné, comment ça s'aère ?",                              "notice_vmc.pdf"),
    ("Jusqu'à quelle heure je peux faire du bruit ?",                       "reglement_copropriete.pdf"),
    ("Combien de temps je reste dans le logement ?",                        "bail_location.pdf"),
    ("Le chauffe-eau met un code à l'écran",                                "notice_chaudiere.pdf"),
    ("Mon linge ressort trempé",                                            "notice_lave_linge.pdf"),
]


def ensure_index() -> None:
    docs_dir = config.DOCUMENTS_DIR
    if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
        print("PDFs absents — lancer : python scripts/generate_documents.py")
        raise SystemExit(1)
    if os.path.exists(config.FAISS_PATH):
        return
    pages = []
    for f in sorted(os.listdir(docs_dir)):
        if f.endswith(".pdf"):
            pages.extend(load_pdf_with_metadata(os.path.join(docs_dir, f)))
    build_faiss_index(chunk_recursive(pages, chunk_size=512, chunk_overlap=50),
                      force_rebuild=True)


def score_retriever(retriever, label: str) -> dict:
    """Calcule Recall@1/3/5 + MRR d'un retriever sur le benchmark."""
    ranks = []
    for q, expected in BENCHMARK_QUESTIONS:
        docs = retriever.invoke(q)
        rank = 0
        for i, d in enumerate(docs, 1):
            if d.metadata.get("source") == expected:
                rank = i
                break
        ranks.append(rank)
    n = len(ranks)
    recall_at = {k: sum(1 for r in ranks if 0 < r <= k) / n for k in (1, 3, 5)}
    mrr = sum(1.0 / r for r in ranks if r > 0) / n
    print(f"\n── {label}")
    for k in (1, 3, 5):
        print(f"   Recall@{k} = {recall_at[k]:.0%}")
    print(f"   MRR      = {mrr:.3f}")
    return {"recall": recall_at, "mrr": mrr}


def main() -> None:
    ensure_index()

    # ─── Baseline fournie : FAISS top-5 (le retrieval d'AT02/AT03) ──────
    baseline = score_retriever(get_faiss_retriever(k=5), "BASELINE FAISS k=5")

    # ─── TODO 2 — construire le retriever reranké et le scorer ──────────
    # reranked_retriever = get_reranked_retriever(base_k=20, top_n=5)
    # reranked = score_retriever(reranked_retriever, "RERANKED flashrank")
    raise NotImplementedError("TODO 2 — get_reranked_retriever + score_retriever")

    # ─── TODO 3 — afficher le gain (ΔRecall@1, ΔMRR) ────────────────────
    # d_r1 = reranked["recall"][1] - baseline["recall"][1]
    # d_mrr = reranked["mrr"] - baseline["mrr"]
    # print(f"\nGAIN : ΔRecall@1={d_r1:+.0%}  ΔMRR={d_mrr:+.3f}")

    # ─── TODO 4 — (bonus) multi-query sur une question à vocabulaire flou ─
    # mq = get_multiquery_retriever(k=4)
    # docs = mq.invoke("Comment entretenir ma ventilation ?")
    # print(f"Multi-query → {len(docs)} documents")


if __name__ == "__main__":
    main()
