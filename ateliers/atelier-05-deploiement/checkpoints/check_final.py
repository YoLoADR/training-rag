#!/usr/bin/env python3
"""
Checkpoint Final — Atelier 05 Deploiement
5 questions sur sécurité API, Langfuse, CORS, auth, métriques.

Usage : python ateliers/atelier-05-deploiement/checkpoints/check_final.py
"""

import sys

QUESTIONS = [
    {
        "question": "Cite 3 raisons concrètes pour lesquelles Langfuse est utile "
                    "EN PRODUCTION (pas juste pour le debug en dev).",
        "keywords": ["latence", "coût", "token", "erreur", "alerte", "trace", "dérive", "prod", "monitoring"],
        "min_hits": 3,
        "explanation": (
            "En prod, Langfuse permet : (1) détecter les dérives de qualité (recall baisse, "
            "hallucinations augmentent), (2) mesurer le coût réel par requête et par utilisateur, "
            "(3) alerter sur les erreurs LLM (rate limit Anthropic, timeouts), "
            "(4) rejouer une conversation pour déboguer un incident utilisateur."
        ),
    },
    {
        "question": "Pourquoi une clé API dans le header X-API-Key est préférable à "
                    "une clé dans l'URL (?api_key=...) ?",
        "keywords": ["log", "url", "header", "cache", "history", "historique", "visible", "navigateur"],
        "min_hits": 2,
        "explanation": (
            "Les URL sont loggées partout : serveur web, reverse proxy, CDN, historique navigateur. "
            "Un header HTTP est transmis dans le corps de la requête TLS — non loggé par défaut. "
            "La clé dans l'URL finit souvent dans des logs de monitoring en clair."
        ),
    },
    {
        "question": "Qu'est-ce que le RGPD exige concernant le logging des prompts utilisateurs "
                    "dans Langfuse ? Quelle technique de mitigation as-tu vue dans l'atelier ?",
        "keywords": ["pii", "anonymi", "hash", "scrub", "données personnelles", "email", "nom", "rgpd"],
        "min_hits": 2,
        "explanation": (
            "Le RGPD interdit de stocker des données personnelles identifiables sans consentement explicite. "
            "Le logging de prompts bruts peut capturer noms, emails, numéros de téléphone. "
            "La technique de mitigation : scrubbing PII avant envoi à Langfuse (remplacer "
            "les PII par [NOM], [EMAIL], [TEL])."
        ),
    },
    {
        "question": "Quelle est la différence entre rate limiting 'par IP' et 'par utilisateur authentifié' ? "
                    "Lequel est préférable en production et pourquoi ?",
        "keywords": ["ip", "userId", "authentifié", "contourner", "proxy", "nat", "partagé"],
        "min_hits": 2,
        "explanation": (
            "Rate limit par IP est contournable (VPN, proxy, NAT partagé — plusieurs utilisateurs "
            "derrière la même IP). Rate limit par userId authentifié est plus précis et équitable. "
            "La combinaison idéale : IP pour les endpoints non-auth, userId pour les endpoints auth."
        ),
    },
    {
        "question": "Explique la latence p95. Si p50=2s et p95=45s, que t'indique cet écart "
                    "sur le comportement de l'API ?",
        "keywords": ["lent", "timeout", "cas", "5%", "pire", "queue", "file", "cold", "biais"],
        "min_hits": 2,
        "explanation": (
            "p95=45s signifie que 5% des requêtes prennent plus de 45 secondes. "
            "Un écart p50=2s / p95=45s est le signe classique d'appels sans timeout qui pendent, "
            "d'un cold start (initialisation de l'agent au premier appel), ou d'une queue qui s'accumule "
            "sous charge. À investiguer immédiatement — les utilisateurs concernés quittent l'UI."
        ),
    },
]

SCORE = 0
TOTAL = len(QUESTIONS)

print("=" * 60)
print("CHECKPOINT FINAL — Atelier 05 : Sécurité + Observabilité")
print("=" * 60)
print("5 questions. Réponds avec tes propres mots — pas de code.")
print()

for i, q in enumerate(QUESTIONS, 1):
    print(f"Q{i}. {q['question']}")
    print()
    answer = input("Ta réponse : ").strip().lower()
    print()

    hits = sum(1 for kw in q["keywords"] if kw.lower() in answer)

    if hits >= q["min_hits"]:
        print(f"  OK ({hits}/{len(q['keywords'])} mots-clés trouvés)")
        SCORE += 1
    else:
        print(f"  Incomplet ({hits}/{len(q['keywords'])} mots-clés, minimum={q['min_hits']})")

    print(f"  Explication : {q['explanation']}")
    print()

PCT = round(100 * SCORE / TOTAL)
print("=" * 60)
print(f"Score final : {SCORE}/{TOTAL} ({PCT}%)")
print()

if PCT >= 80:
    print("Excellent ! Direction le BONUS.")
elif PCT >= 60:
    print("Bien. Prends une pause, relis les points faibles, puis choisis Bonus.")
else:
    print("Score < 60% → pars en SPRINT pour consolider les bases.")
    print("Relis api/main.py, api/limiter.py et la doc Langfuse.")
    sys.exit(1)
