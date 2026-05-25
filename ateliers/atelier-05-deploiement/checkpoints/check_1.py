#!/usr/bin/env python3
"""
Checkpoint 1 — Atelier 05 Deploiement
3 questions sur FastAPI / rate limiting / CORS.

Usage : python ateliers/atelier-05-deploiement/checkpoints/check_1.py
"""

import sys

QUESTIONS = [
    {
        "question": "Dans api/main.py, quel est le rôle du décorateur @app.middleware('http') "
                    "sur la fonction prompt_injection_filter ?",
        "keywords": ["toutes", "requêtes", "avant", "router", "POST", "intercepte", "filtre"],
        "explanation": (
            "Le middleware @app.middleware('http') intercepte TOUTES les requêtes HTTP "
            "avant qu'elles atteignent les routers. Pour les requêtes POST, il lit le body "
            "et applique les 19 patterns regex. Si un pattern matche → HTTP 400 sans appeler le LLM."
        ),
    },
    {
        "question": "Si tu configures le rate limiter à 10 req/min et qu'un utilisateur envoie "
                    "15 requêtes en 20 secondes, que va-t-il recevoir ? Quel code HTTP et "
                    "à partir de quelle requête ?",
        "keywords": ["429", "11", "onzième", "10", "limite"],
        "explanation": (
            "Les 10 premières requêtes passent (HTTP 200). À partir de la 11e, slowapi "
            "retourne HTTP 429 Too Many Requests avec un header Retry-After indiquant "
            "combien de secondes attendre avant de réessayer."
        ),
    },
    {
        "question": "Quelle est la différence entre allow_origins=['*'] et "
                    "allow_origins=['http://localhost:8501'] dans la config CORS ?",
        "keywords": ["tout", "site", "whitelist", "liste", "origines", "danger", "navigateur"],
        "explanation": (
            "allow_origins=['*'] autorise n'importe quel site web à appeler l'API depuis "
            "le navigateur d'un utilisateur. allow_origins=['http://localhost:8501'] "
            "n'autorise que le Streamlit local — les autres domaines reçoivent une erreur CORS."
        ),
    },
]

SCORE = 0

print("=" * 60)
print("CHECKPOINT 1 — Atelier 05 : Sécurité API")
print("=" * 60)
print("Réponds à chaque question. Pas de code — explique avec tes mots.")
print()

for i, q in enumerate(QUESTIONS, 1):
    print(f"Q{i}. {q['question']}")
    print()
    answer = input("Ta réponse : ").strip().lower()
    print()

    hits = sum(1 for kw in q["keywords"] if kw.lower() in answer)
    threshold = max(2, len(q["keywords"]) // 2)

    if hits >= threshold:
        print(f"  OK ({hits}/{len(q['keywords'])} mots-clés trouvés)")
        SCORE += 1
    else:
        print(f"  Incomplet ({hits}/{len(q['keywords'])} mots-clés trouvés)")

    print(f"  Explication : {q['explanation']}")
    print()

print("=" * 60)
print(f"Score : {SCORE}/{len(QUESTIONS)}")
if SCORE == len(QUESTIONS):
    print("Parfait ! Continue vers l'Etape 2.")
elif SCORE >= 2:
    print("Bien. Relis les points manquants, puis continue.")
else:
    print("Revois api/main.py et api/limiter.py avant de continuer.")

# ── Explication personnelle (verbalisation anti-skip blank API) ─────────────
print()
print("=" * 60)
print("EXPLICATION PERSONNELLE (verbalisation)")
print("=" * 60)
EXPLAIN_PROMPT = (
    "Avant de checker la solution par git diff, explique en UNE phrase :\n"
    "  Pourquoi enveloppe-t-on `chain.invoke(...)` dans\n"
    "  `await loop.run_in_executor(None, chain.invoke, payload)` ?\n"
)
EXPLAIN_KEYWORDS = ["sync", "synchrone", "async", "bloque", "bloquer", "thread", "executor", "fastapi", "event", "loop", "worker"]
print(EXPLAIN_PROMPT)
explanation = input("Ta réponse en une phrase : ").strip().lower()
found = [kw for kw in EXPLAIN_KEYWORDS if kw in explanation]
if len(found) >= 2:
    print(f"\n✓ Verbalisation OK (mots-clés : {', '.join(found)})")
    print("→ Tu peux consulter `git diff student/05 atelier/05 -- <fichier>` si nécessaire.")
else:
    print(f"\n✗ Verbalisation insuffisante (mots trouvés : {found or 'aucun'} ; min 2).")
    print(f"→ Mots attendus : {', '.join(EXPLAIN_KEYWORDS[:5])}…")
    sys.exit(1)
