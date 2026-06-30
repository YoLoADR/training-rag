"""
═══════════════════════════════════════════════════════════════════════════
Atelier 08 — Optimisation du pipeline RAG (solution corrigée + commentaires)
═══════════════════════════════════════════════════════════════════════════

On reprend EXACTEMENT là où AT02 s'arrête (cf. la note "Reranking" en bas de
evaluate_rag.py) : le retrieval brut récupère parfois le bon chunk au rang 6-8,
hors du top-5. On ajoute un reclassement cross-encoder (flashrank) + multi-query
et on MESURE le gain (Recall@k et MRR) face à la baseline FAISS.

Lancer : python ateliers/atelier-08-optimisation/solution.py
═══════════════════════════════════════════════════════════════════════════
"""

import os

from homebutler import config
from homebutler.rag.ingestion import load_pdf_with_metadata, chunk_recursive
from homebutler.rag.vectorstore_faiss import build_faiss_index
from homebutler.rag.retriever import get_faiss_retriever
from homebutler.rag.reranking import (
    get_reranked_retriever,
    get_multiquery_retriever,
    get_hyde_chain,
)

# ─── 10 questions étalons en langage NATUREL / INDIRECT ───────────────────
# Volontairement formulées comme un vrai usager (pas le vocabulaire des notices) :
# c'est là que le bi-encodeur (embeddings) se trompe d'ordre et que le
# cross-encoder (reranking) fait la différence. Sur des questions "mot pour mot"
# du document, la baseline est déjà parfaite et le gain serait invisible.
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
    """Construit l'index FAISS sur le corpus si nécessaire (réutilise AT02)."""
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


# ═══════════════════════════════════════════════════════════════════════════
# CONCEPT RAG : Recall@k et MRR (Mean Reciprocal Rank)
# ───────────────────────────────────────────────────────────────────────────
# Recall@k = sur N questions, combien ont le bon document dans les k premiers.
# MRR      = moyenne de 1/rang du premier bon document (1.0 si toujours en tête,
#            0.5 si en moyenne au 2e rang...). Le reranking AMÉLIORE surtout le
#            MRR et le Recall@1 : il remonte le bon chunk vers le sommet.
# ═══════════════════════════════════════════════════════════════════════════
def score_retriever(retriever, label: str) -> dict:
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

    print("═" * 60)
    print("  BASELINE — FAISS seul (top-5)")
    print("═" * 60)
    baseline = score_retriever(get_faiss_retriever(k=5), "FAISS k=5 (baseline AT02/03)")

    # ═══════════════════════════════════════════════════════════════════
    # CONCEPT RAG : Reranking cross-encoder (entonnoir base_k ≫ top_n)
    # ──────────────────────────────────────────────────────────────────
    # On récupère LARGE (20 candidats) puis le cross-encoder re-score chaque
    # paire (question, chunk) et ne garde que les 5 meilleurs. Le bi-encodeur
    # (embeddings) est rapide mais grossier ; le cross-encoder est lent mais
    # précis — on l'applique seulement aux 20 candidats, pas à tout le corpus.
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "═" * 60)
    print("  RERANKED — FAISS base_k=20 → flashrank top_n=5")
    print("═" * 60)
    reranked = score_retriever(get_reranked_retriever(base_k=20, top_n=5),
                               "FAISS+flashrank")

    # ─── Verdict du gain ────────────────────────────────────────────────
    # Le reranking remonte le bon chunk vers le SOMMET : c'est Recall@1 et MRR
    # qui bougent (Recall@5 sature vite sur un petit corpus).
    print("\n" + "═" * 60)
    d_r1 = reranked["recall"][1] - baseline["recall"][1]
    d_mrr = reranked["mrr"] - baseline["mrr"]
    print(f"  GAIN reranking : ΔRecall@1 = {d_r1:+.0%}   ΔMRR = {d_mrr:+.3f}")
    print("  (sur questions en langage naturel, le cross-encoder corrige l'ordre)")
    print("═" * 60)

    # ═══════════════════════════════════════════════════════════════════
    # CONCEPT RAG : Multi-query — couvrir les variantes de vocabulaire
    # ──────────────────────────────────────────────────────────────────
    # Le LLM reformule la question en 3 variantes (cf. MULTIQUERY_PROMPT),
    # on récupère pour chacune, puis union des documents. La diversité vient
    # du PROMPT (on demande 3 versions), pas de la température.
    # ═══════════════════════════════════════════════════════════════════
    try:
        mq = get_multiquery_retriever(k=4)
        docs = mq.invoke("Comment entretenir ma ventilation ?")
        print(f"\n  Multi-query → {len(docs)} documents (union des reformulations)")
        for d in docs[:3]:
            print(f"    • {d.metadata.get('source')} p.{d.metadata.get('page')}")
    except Exception as e:  # pragma: no cover - dépend d'un LLM joignable
        print(f"\n  (Multi-query non exécuté — LLM indisponible : {e})")

    # ─── HyDE (bonus) : embed une réponse hypothétique ──────────────────
    try:
        hypo = get_hyde_chain().invoke({"question": "Que faire si la chaudière affiche F4 ?"})
        print(f"\n  HyDE — paragraphe hypothétique généré ({len(hypo)} chars) :")
        print("   ", hypo[:160].replace("\n", " "), "…")
    except Exception as e:  # pragma: no cover
        print(f"\n  (HyDE non exécuté — LLM indisponible : {e})")


if __name__ == "__main__":
    main()
