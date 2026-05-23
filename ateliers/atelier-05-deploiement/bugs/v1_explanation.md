# Bug v1 — Clé API exposée dans la réponse JSON

## Contexte

Le bug ajoute un champ `api_key` dans le modèle Pydantic `ChatResponse`, peuplé avec la valeur de la variable d'environnement `ANTHROPIC_API_KEY`. Cette clé apparaît alors dans chaque réponse de l'endpoint `/chat`.

## Affirmations Vrai / Faux

Réponds à chaque affirmation avant de regarder les réponses.

**1. "Exposer la clé API dans la réponse JSON n'est un problème que si l'API est publique sur Internet."**

[ ] Vrai   [ ] Faux

**2. "Un attaquant qui récupère la clé `sk-ant-...` peut l'utiliser pour appeler Claude à tes frais, sans limite."**

[ ] Vrai   [ ] Faux

**3. "Pour corriger ce bug, il suffit de masquer la clé côté front-end (ne pas l'afficher dans l'UI)."**

[ ] Vrai   [ ] Faux

**4. "La bonne pratique est de ne jamais inclure de secret (clé API, mot de passe, token) dans un modèle de réponse Pydantic."**

[ ] Vrai   [ ] Faux

**5. "Si on utilise HTTPS, la clé dans la réponse JSON est chiffrée et donc inoffensive."**

[ ] Vrai   [ ] Faux

---

## Réponses commentées

1. **FAUX** — Même sur un réseau interne, un collègue malveillant, un log de débogage, ou un outil d'observabilité mal configuré peut capturer la réponse. La règle est : *les secrets ne doivent jamais quitter le backend*, quelle que soit l'audience.

2. **VRAI** — Une clé Anthropic n'a pas de limite intégrée. Un attaquant peut lancer des millions de requêtes avant que tu réalises la fuite. Coût potentiel : milliers d'euros en quelques heures.

3. **FAUX** — Masquer côté front ne change rien : les outils de développement du navigateur (Network tab), les proxies, les logs de réseau capturent la réponse brute. Le fix doit être côté serveur : retirer le champ du modèle.

4. **VRAI** — Les modèles Pydantic définissent le contrat de l'API. Tout champ ajouté est potentiellement exposé. Revue de code systématique sur les `ChatResponse`, `APIResponse`, etc.

5. **FAUX** — HTTPS chiffre le transport, pas la donnée. Une fois déchiffrée côté client, la réponse JSON est en clair. HTTPS ne compense pas une fuite de données dans le payload.
