"""
═══════════════════════════════════════════════════════════════════════════
Atelier 07 — Observabilité & Évaluation (harnais — version corrigée)
═══════════════════════════════════════════════════════════════════════════

On reprend le pipeline RAG (AT02/03) et on le rend MESURABLE en continu :
  1. TRACER chaque appel avec Langfuse (handler en callback)
  2. NOTER chaque réponse via un LLM-as-judge → score poussé dans la trace
  3. ÉVALUER en batch avec RAGAS (faithfulness, answer_relevancy,
     context_precision, context_recall)

La bibliothèque réutilisable est `homebutler/eval/` (fournie). Ce fichier l'ORCHESTRE.

Pré-requis :
  - index FAISS construit (AT02)
  - pour RAGAS / le judge : un LLM joignable (ANTHROPIC_API_KEY ou LLM_PROVIDER=ollama)
  - pour les traces : LANGFUSE_* dans .env (Cloud) — sinon le tracing est un no-op

Lancer : python ateliers/atelier-07-observabilite/evaluate_observability.py
═══════════════════════════════════════════════════════════════════════════
"""

import json
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from homebutler import config
from homebutler.llm.provider import get_llm
from homebutler.llm.prompts import RAG_QA_TEMPLATE
from homebutler.rag.ingestion import load_pdf_with_metadata, chunk_recursive
from homebutler.rag.vectorstore_faiss import build_faiss_index
from homebutler.rag.retriever import get_faiss_retriever
from homebutler.eval import (
    get_langfuse_handler, flush_traces, score_trace,
    build_eval_dataset, run_ragas_eval, llm_as_judge,
)

QA_PATH = os.path.join(config.DATA_DIR, "qa_dataset", "concierge_qa.jsonl")
N_EVAL = 6   # petit échantillon en Core (garde-fou rate-limit) ; augmente en Bonus


def _llm_available() -> bool:
    """RAGAS et le LLM-as-judge font des appels LLM : on vérifie qu'un LLM est joignable."""
    if config.LLM_PROVIDER == "anthropic":
        return bool(config.ANTHROPIC_API_KEY)
    return True  # ollama : supposé démarré localement


def ensure_index() -> None:
    docs_dir = config.DOCUMENTS_DIR
    if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
        print("PDFs absents — lancer : python scripts/generate_documents.py")
        raise SystemExit(1)
    if not os.path.exists(config.FAISS_PATH):
        pages = []
        for f in sorted(os.listdir(docs_dir)):
            if f.endswith(".pdf"):
                pages.extend(load_pdf_with_metadata(os.path.join(docs_dir, f)))
        build_faiss_index(chunk_recursive(pages, chunk_size=512, chunk_overlap=50),
                          force_rebuild=True)


def load_eval_samples(n: int = N_EVAL) -> list:
    """Charge n paires du dataset. input -> user_input, output -> reference."""
    if not os.path.exists(QA_PATH):
        print(f"Dataset absent : {QA_PATH} — lancer python scripts/generate_qa_dataset.py")
        raise SystemExit(1)
    rows = []
    with open(QA_PATH, encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            rows.append({"question": d["input"], "reference": d["output"]})
            if len(rows) >= n:
                break
    return rows


def format_docs(docs) -> str:
    return "\n\n".join(
        f"[{d.metadata.get('source')} p.{d.metadata.get('page')}]\n{d.page_content}"
        for d in docs
    )


def build_rag_chain(retriever):
    llm = get_llm(temperature=0.1)
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_QA_TEMPLATE | llm | StrOutputParser()
    )


def run_and_collect(rows: list) -> list:
    """Exécute le RAG tracé + judge, retourne les échantillons pour RAGAS."""
    retriever = get_faiss_retriever(k=4)
    rag_chain = build_rag_chain(retriever)
    handler = get_langfuse_handler()         # None si pas de clés → tracing no-op
    cfg = {"callbacks": [handler]} if handler else {}

    samples = []
    for row in rows:
        q, ref = row["question"], row["reference"]
        docs = retriever.invoke(q)
        contexts = [d.page_content for d in docs]
        answer = rag_chain.invoke(q, config=cfg)          # ← tracé dans Langfuse

        # LLM-as-judge déterministe → score [0,1], poussé dans la trace
        score = llm_as_judge(q, answer, contexts)
        trace_id = handler.get_trace_id() if handler and hasattr(handler, "get_trace_id") else None
        if trace_id:
            score_trace(trace_id, name="llm_judge", value=score,
                        comment="qualité globale (1-5 normalisé)")

        print(f"  • {q[:50]:50}  judge={score:.2f}")
        samples.append({
            "user_input": q,
            "response": answer,
            "retrieved_contexts": contexts,
            "reference": ref,            # ← indispensable pour context_recall/precision
        })
    flush_traces(handler)
    return samples


def main() -> None:
    if not _llm_available():
        print("LLM non configuré — RAGAS et le LLM-as-judge nécessitent un LLM joignable.")
        print("  → renseigne ANTHROPIC_API_KEY dans .env, ou passe LLM_PROVIDER=ollama.")
        raise SystemExit(1)
    ensure_index()
    rows = load_eval_samples(N_EVAL)
    print(f"═══ Observabilité + judge sur {len(rows)} questions ═══")
    samples = run_and_collect(rows)

    print("\n═══ Évaluation RAGAS ═══")
    dataset = build_eval_dataset(samples)
    metrics = run_ragas_eval(dataset)
    print("─" * 50)
    for name, value in metrics.items():
        print(f"  {name:24} : {value:.3f}")
    print("─" * 50)
    print("Traces + scores visibles dans Langfuse (si LANGFUSE_* configuré).")


if __name__ == "__main__":
    main()
