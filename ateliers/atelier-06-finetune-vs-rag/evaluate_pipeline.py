"""
═══════════════════════════════════════════════════════════════════════════
Atelier 06 — Évaluation comparée des pipelines (RAG vs Hybride)
═══════════════════════════════════════════════════════════════════════════

Compare quantitativement les modes llm_only / rag_only / agent en termes :
  - de Recall@k sur les stratégies de chunking
  - de précision factuelle (mots-clés attendus dans la réponse)
  - de latence
  - de coût (estimation tokens)

Pré-requis : API démarrée sur localhost:8000.

Lancer : python ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py
═══════════════════════════════════════════════════════════════════════════
"""

import json
import statistics
import sys
import time
from pathlib import Path

import requests

API = "http://localhost:8000"
BASE = Path(__file__).resolve().parent.parent.parent
QA_PATH = BASE / "data" / "qa_dataset" / "concierge_qa.jsonl"


def load_qa(n: int = 20) -> list[dict]:
    if not QA_PATH.exists():
        print(f"Dataset absent : {QA_PATH}")
        print("Lance : python scripts/generate_qa_dataset.py")
        sys.exit(1)
    with QA_PATH.open() as f:
        return [json.loads(line) for line in f if line.strip()][:n]


# ─── TODO 1 — Charger 20 paires de test ──────────────────────────────────
# Implémenté ci-dessus dans load_qa().


# ─── TODO 2 — POST /rag/evaluate pour les 3 stratégies ──────────────────
def evaluate_strategies(sample_size: int = 20) -> dict:
    """
    Pour chacune des 3 stratégies de chunking ('fixed', 'recursive', 'ensemble'),
    poste sur {API}/rag/evaluate et collecte Recall@1/@3/@5 + temps écoulé.

    Returns:
        dict {strategy_name: response_json}

    --- Indice léger ---
    Boucle sur les 3 stratégies. À chaque itération :
      - mesure le temps (`time.time()` avant/après),
      - `requests.post(f"{API}/rag/evaluate", json={"strategy": ..., "sample_size": sample_size})`,
      - si `r.status_code == 200`, range `r.json()` dans `out[strategy]` et imprime
        Recall@1/3/5 ; sinon imprime le code HTTP.

    --- Indice fort ---
    ```python
    print("\\n═══ TODO 2 — POST /rag/evaluate pour 3 stratégies ═══")
    out = {}
    for strategy in ("fixed", "recursive", "ensemble"):
        t0 = time.time()
        r = requests.post(f"{API}/rag/evaluate",
                          json={"strategy": strategy, "sample_size": sample_size})
        elapsed = time.time() - t0
        if r.status_code != 200:
            print(f"  {strategy}: HTTP {r.status_code}")
            continue
        data = r.json()
        out[strategy] = data
        print(f"  {strategy:10s}  Recall@1={data['recall_at_1']:.2f}  "
              f"Recall@3={data['recall_at_3']:.2f}  Recall@5={data['recall_at_5']:.2f}  "
              f"({elapsed:.1f}s)")
    return out
    ```
    """
    raise NotImplementedError(
        "Atelier 06 TODO 2 — evaluate_strategies. "
        "Solution : git diff student/06-finetune-vs-rag atelier/06-finetune-vs-rag -- ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py"
    )


# ─── TODO 3 — POST /chat sur 5 questions × 3 modes ──────────────────────
def compare_modes(questions: list[str]) -> dict:
    """
    Compare llm_only / rag_only / agent sur les mêmes questions.
    POST sur {API}/chat avec `{"message": q, "mode": mode}` pour chaque combinaison.

    Returns:
        dict {"answers": {mode: [str]}, "latencies": {mode: [float]}}

    --- Indice léger ---
    Double boucle : pour chaque question, pour chaque des 3 modes (llm_only,
    rag_only, agent), POST sur `{API}/chat` avec `{"message": q, "mode": mode}`,
    timeout=60s. Mesure la latence à chaque appel et stocke réponse + latence.

    --- Indice fort ---
    ```python
    print("\\n═══ TODO 3 — Comparaison 3 modes (llm_only / rag_only / agent) ═══")
    results = {"llm_only": [], "rag_only": [], "agent": []}
    latencies = {"llm_only": [], "rag_only": [], "agent": []}

    for q in questions:
        for mode in ("llm_only", "rag_only", "agent"):
            t0 = time.time()
            r = requests.post(f"{API}/chat",
                              json={"message": q, "mode": mode}, timeout=60)
            elapsed = time.time() - t0
            latencies[mode].append(elapsed)
            if r.status_code == 200:
                results[mode].append(r.json().get("response", ""))
                print(f"  [{mode:10s}] {q[:50]:50s}  → {elapsed:.1f}s")
            else:
                results[mode].append(f"HTTP {r.status_code}")

    return {"answers": results, "latencies": latencies}
    ```
    """
    raise NotImplementedError(
        "Atelier 06 TODO 3 — compare_modes. "
        "Solution : git diff student/06-finetune-vs-rag atelier/06-finetune-vs-rag -- ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py"
    )


# ─── TODO 4 — Latence par mode (already collected) ───────────────────────
def show_latency_summary(latencies: dict) -> None:
    print("\n═══ TODO 4 — Latence moyenne par mode ═══")
    for mode, lats in latencies.items():
        if lats:
            print(f"  {mode:10s}  moy={statistics.mean(lats):.2f}s  "
                  f"med={statistics.median(lats):.2f}s")


# ─── TODO 5 — Tableau récapitulatif + benchmarks ──────────────────────────
def show_summary(strategies_eval: dict, latencies: dict) -> None:
    """
    Imprime un tableau Markdown des Recall@k par stratégie, suivi des
    benchmarks de référence (RAFT Zhang et al. 2024) à comparer.

    --- Indice léger ---
    Header `Stratégie | R@1 | R@3 | R@5` puis une ligne par stratégie.
    Puis 4 lignes de référence : RAG ensemble (~0.87), RAG fixed (~0.72),
    LLM seul (~0.15), Hybride RAFT (94/95/96 %).

    --- Indice fort ---
    ```python
    print("\\n═══ TODO 5 — Tableau récapitulatif ═══")
    print(f"{'Stratégie':<12} {'R@1':>6} {'R@3':>6} {'R@5':>6}")
    for strategy, data in strategies_eval.items():
        print(f"{strategy:<12} {data['recall_at_1']:>6.2f} "
              f"{data['recall_at_3']:>6.2f} {data['recall_at_5']:>6.2f}")
    print("\\nÀ COMPARER aux benchmarks Slide 7 Chapitre 6 (RAFT Zhang et al. 2024) :")
    print("  RAG ensemble    : Recall@5 attendu ~ 0.87")
    print("  RAG fixed-size  : Recall@5 attendu ~ 0.72")
    print("  LLM seul        : Recall@5 ≈ 0.15 (pas de retrieval, invente)")
    print("  Hybride (RAFT)  : 94 % QA factuel, 95 % style, 96 % médical")
    ```
    """
    raise NotImplementedError(
        "Atelier 06 TODO 5 — show_summary. "
        "Solution : git diff student/06-finetune-vs-rag atelier/06-finetune-vs-rag -- ateliers/atelier-06-finetune-vs-rag/evaluate_pipeline.py"
    )


# ─── TODO 6 — Compléter grille_decision.md ──────────────────────────────
def todo_grille() -> None:
    print("\n═══ TODO 6 — Compléter grille_decision.md ═══")
    print("  Ajouter votre recommandation pour 3 cas d'usage métier")
    print("  (ex: chatbot RH, support technique, analyse contrats juridiques).")


def main() -> None:
    qa = load_qa(20)
    print(f"Dataset chargé : {len(qa)} paires")

    try:
        r = requests.get(f"{API}/", timeout=2)
    except requests.exceptions.RequestException:
        print(f"\nAPI non joignable sur {API}.")
        print("Lancez : uvicorn api.main:app --port 8000")
        sys.exit(1)

    strategies_eval = evaluate_strategies(20)
    questions = [p["input"] for p in qa[:5]]
    comparison = compare_modes(questions)
    show_latency_summary(comparison["latencies"])
    show_summary(strategies_eval, comparison["latencies"])
    todo_grille()


if __name__ == "__main__":
    main()
