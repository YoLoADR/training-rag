# Bug v3 — Pas de timeout backend (appel qui pend indéfiniment)

## Contexte

Sans `timeout` dans `asyncio.wait_for()`, un appel au LLM peut bloquer le worker FastAPI indéfiniment. Si Claude est lent ou si Anthropic a un problème momentané, toutes les requêtes suivantes s'accumulent en file d'attente — et le service devient indisponible.

## Affirmations Vrai / Faux

**1. "Un call HTTP sans timeout bloque seulement la requête concernée, pas les autres."**

[ ] Vrai   [ ] Faux

**2. "Un timeout de 30s est une valeur universellement bonne pour tous les appels LLM."**

[ ] Vrai   [ ] Faux

**3. "La latence p95 est plus importante que la latence p50 pour détecter les appels qui pendent."**

[ ] Vrai   [ ] Faux

**4. "Il suffit de mettre un timeout côté client (ex: `httpx.AsyncClient(timeout=30)`) pour se protéger."**

[ ] Vrai   [ ] Faux

**5. "asyncio.wait_for(coroutine, timeout=None) est équivalent à ne pas utiliser wait_for."**

[ ] Vrai   [ ] Faux

---

## Réponses commentées

1. **FAUX** — FastAPI utilise un pool de workers (threads ou coroutines). Un worker bloqué est indisponible pour traiter les requêtes suivantes. Avec 4 workers et 4 appels sans timeout, le service est entièrement paralysé.

2. **FAUX** — Le timeout optimal dépend du mode : `llm_only` ≈ 10s, `rag_only` ≈ 15s, `agent` peut légitimement prendre 30-60s (plusieurs appels LLM). La bonne pratique : timeout différencié par mode, configurable via `.env`.

3. **VRAI** — La p50 montre le cas "normal". La p95 montre ce qui arrive dans 5% des cas : network jitter, cold start, rate limit Anthropic. Un p95 de 45s est le signe d'appels sans timeout qui trainent.

4. **FAUX** — Le timeout client protège le client : il abandonne après 30s. Mais le serveur continue à attendre Claude ! Il faut un timeout **côté serveur** pour libérer le worker.

5. **VRAI** — `timeout=None` dans `asyncio.wait_for()` désactive le timeout. C'est équivalent à appeler directement `await coroutine` sans filet. La documentation Python le précise explicitement.
