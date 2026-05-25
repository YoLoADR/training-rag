#!/usr/bin/env python3
"""
Checkpoint 1 — Atelier 06 Fine-tuning vs RAG / RAFT
3 questions sur RAFT / évaluation comparative / TCO.

Usage : python ateliers/atelier-06-finetune-vs-rag/checkpoints/check_1.py
"""

import sys

QUESTIONS = [
    {
        "question": "Explique RAFT en 3 phrases. En quoi est-il différent de RAG seul "
                    "et de Fine-Tuning seul ?",
        "keywords": ["fine-tuning", "rag", "combine", "distracteur", "entraîne", "bruit", "ignore",
                     "documents", "perturb", "zhang"],
        "min_hits": 3,
        "explanation": (
            "RAFT (Retrieval-Augmented Fine-Tuning, Zhang et al. 2024) combine RAG et FT : "
            "on entraîne le modèle avec des questions + le document pertinent + des documents "
            "distracteurs mélangés. Le modèle apprend à ignorer le bruit du retriever. "
            "RAG seul ne modifie pas les poids du modèle. FT seul n'utilise pas de contexte externe. "
            "RAFT atteint 94% QA factuel vs 89% RAG et 79% FT (RAFT 2024)."
        ),
    },
    {
        "question": "Tu as mesuré Recall@5 = 0.87 pour 'ensemble' et 0.72 pour 'fixed-size'. "
                    "Qu'est-ce que cela signifie concrètement pour un utilisateur HomeButler ? "
                    "Et quelle est la limite de cette métrique ?",
        "keywords": ["0.87", "0.72", "5", "chunks", "bonne", "réponse", "limite", "qualité", "hallucination",
                     "question", "top", "retriever"],
        "min_hits": 3,
        "explanation": (
            "Recall@5 = 0.87 signifie : sur 100 questions test, dans 87 cas, le bon chunk "
            "(celui qui contient la réponse) est parmi les 5 premiers récupérés. "
            "Pour l'utilisateur : 13% des questions retourneront une réponse imprécise ou hallucination. "
            "Limite : Recall@5 mesure le retriever, pas la qualité de la réponse générée. "
            "Un bon retriever + un LLM qui hallucine peut donner Recall@5 élevé avec hallucinations."
        ),
    },
    {
        "question": "Le FT auto-hébergé coûte environ 50€/mois de VPS GPU + un setup à 3000€. "
                    "L'API Anthropic coûte ~0.01€ par requête. "
                    "À partir de combien de requêtes par mois le FT devient-il rentable sur 1 an ?",
        "keywords": ["50", "0.01", "1000", "break-even", "mois", "req", "rentable", "calcul"],
        "min_hits": 2,
        "explanation": (
            "Calcul break-even : "
            "FT an 1 = 3000 (setup) + 12×50 (VPS) = 3600€. "
            "API an 1 = 0.01€ × N req/mois × 12 mois = 0.12N€. "
            "Equation : 3600 = 0.12N → N = 30 000 req/mois. "
            "Au-delà de ~30k req/mois sur 1 an, le FT est rentable vs API Anthropic."
        ),
    },
]

SCORE = 0

print("=" * 60)
print("CHECKPOINT 1 — Atelier 06 : RAFT / Eval / TCO")
print("=" * 60)
print("3 questions. Réponds avec tes propres mots et tes données.")
print()

for i, q in enumerate(QUESTIONS, 1):
    print(f"Q{i}. {q['question']}")
    print()
    answer = input("Ta réponse : ").strip().lower()
    print()

    hits = sum(1 for kw in q["keywords"] if kw.lower() in answer)

    if hits >= q["min_hits"]:
        print(f"  OK ({hits}/{len(q['keywords'])} mots-clés)")
        SCORE += 1
    else:
        print(f"  Incomplet ({hits}/{len(q['keywords'])} mots-clés, minimum requis : {q['min_hits']})")

    print(f"  Explication : {q['explanation']}")
    print()

print("=" * 60)
print(f"Score : {SCORE}/{len(QUESTIONS)}")
if SCORE >= 2:
    print("Bien. Continue vers le Mini-lab.")
else:
    print("Relis grille_decision.md et relance evaluate_pipeline.py avant de continuer.")

# ── Explication personnelle (verbalisation anti-skip blank eval) ────────────
print()
print("=" * 60)
print("EXPLICATION PERSONNELLE (verbalisation)")
print("=" * 60)
EXPLAIN_PROMPT = (
    "Avant de checker la solution par git diff, explique en UNE phrase :\n"
    "  Pourquoi évalue-t-on EN PASSANT PAR L'API HTTP\n"
    "  (POST /chat, POST /rag/evaluate) plutôt qu'en important\n"
    "  directement les fonctions Python du retriever ?\n"
)
EXPLAIN_KEYWORDS = ["isol", "production", "intégration", "integration", "client", "latence", "réseau", "reseau", "réaliste", "realiste", "bout-en-bout", "bout en bout", "stack"]
print(EXPLAIN_PROMPT)
explanation = input("Ta réponse en une phrase : ").strip().lower()
found = [kw for kw in EXPLAIN_KEYWORDS if kw in explanation]
if len(found) >= 2:
    print(f"\n✓ Verbalisation OK (mots-clés : {', '.join(found)})")
    print("→ Tu peux consulter `git diff student/06 atelier/06 -- evaluate_pipeline.py` si nécessaire.")
else:
    print(f"\n✗ Verbalisation insuffisante (mots trouvés : {found or 'aucun'} ; min 2).")
    print(f"→ Mots attendus : {', '.join(EXPLAIN_KEYWORDS[:6])}…")
    sys.exit(1)
