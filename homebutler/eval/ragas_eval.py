"""
Évaluation RAGAS (Atelier 07) — métriques automatiques de qualité RAG.

RAGAS 0.2.x (API 2026). Schéma des échantillons (≠ ancien 0.1.x) :
  - user_input         : la question
  - response           : la réponse produite par le pipeline
  - retrieved_contexts : liste des chunks récupérés (list[str])
  - reference          : la réponse de référence (ground truth)

4 métriques :
  - faithfulness        : la réponse est-elle ancrée dans les contextes (vs inventée) ?
  - answer_relevancy    : la réponse répond-elle à la question ?
  - context_precision   : les contextes récupérés sont-ils pertinents ?   (exige `reference`)
  - context_recall      : les contextes couvrent-ils la réponse de référence ? (exige `reference`)

⚠️ context_precision et context_recall (variantes "with reference") nécessitent `reference`.
   Sans `reference`, elles renvoient NaN — c'est exactement le Bug v2 de l'atelier.

Le juge RAGAS et ses embeddings sont injectés EXPLICITEMENT (get_llm / fastembed) : sinon
RAGAS tente d'utiliser OpenAI par défaut et réclame une clé OPENAI_API_KEY absente.
"""


def build_eval_dataset(samples):
    """Construit un EvaluationDataset RAGAS depuis une liste de dicts.

    Chaque dict : {user_input, response, retrieved_contexts, reference}.
    """
    from ragas import EvaluationDataset, SingleTurnSample
    return EvaluationDataset(samples=[SingleTurnSample(**s) for s in samples])


def run_ragas_eval(dataset, metrics=None) -> dict:
    """Lance l'évaluation RAGAS et retourne un dict {metric_name: score}.

    `dataset` : EvaluationDataset (via build_eval_dataset).
    Le LLM juge (déterministe) et les embeddings sont ceux du projet (local-first).
    """
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness, answer_relevancy, context_precision, context_recall,
    )
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from homebutler.llm.provider import get_llm
    from homebutler.rag.vectorstore_faiss import get_embeddings

    judge = LangchainLLMWrapper(get_llm(temperature=0))     # déterministe
    emb = LangchainEmbeddingsWrapper(get_embeddings())       # fastembed 384d (local)
    metrics = metrics or [faithfulness, answer_relevancy, context_precision, context_recall]

    result = evaluate(dataset, metrics=metrics, llm=judge, embeddings=emb)
    # result se convertit en dict de moyennes (selon version : .to_pandas() ou cast direct)
    try:
        df = result.to_pandas()
        numeric = df.select_dtypes("number")
        return {col: float(numeric[col].mean()) for col in numeric.columns}
    except Exception:
        return dict(result)
