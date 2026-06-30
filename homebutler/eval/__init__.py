"""
homebutler.eval — observabilité & évaluation (Atelier 07).

Bibliothèque fournie (lecture seule) que l'élève câble depuis
ateliers/atelier-07-observabilite/evaluate_observability.py :

- tracing  : handler Langfuse + scoring des traces
- ragas_eval : construction du dataset + métriques RAGAS
- judge    : LLM-as-judge déterministe (temperature=0)
"""

from homebutler.eval.tracing import (
    get_langfuse_handler,
    get_langfuse_client,
    flush_traces,
    score_trace,
)
from homebutler.eval.ragas_eval import build_eval_dataset, run_ragas_eval
from homebutler.eval.judge import llm_as_judge

__all__ = [
    "get_langfuse_handler",
    "get_langfuse_client",
    "flush_traces",
    "score_trace",
    "build_eval_dataset",
    "run_ragas_eval",
    "llm_as_judge",
]
