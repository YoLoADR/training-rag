# Bug v2 — CORS wildcard (allow_origins=["*"])

## Contexte

CORS (Cross-Origin Resource Sharing) est le mécanisme par lequel un navigateur vérifie si un site web (ex: `https://evil-site.com`) a le droit d'appeler ton API. Avec `allow_origins=["*"]`, n'importe quel site peut appeler l'API depuis le navigateur d'un utilisateur authentifié.

## Affirmations Vrai / Faux

**1. "CORS=* n'est dangereux que si l'API n'a pas d'authentification."**

[ ] Vrai   [ ] Faux

**2. "Un attaquant peut exploiter CORS=* même si l'utilisateur ne visite pas son site intentionnellement (ex: pub malveillante sur un site légitime)."**

[ ] Vrai   [ ] Faux

**3. "La solution est d'ajouter tous les domaines possibles dans allow_origins pour être safe."**

[ ] Vrai   [ ] Faux

**4. "En développement local, CORS=* est acceptable. Le problème est uniquement en production."**

[ ] Vrai   [ ] Faux

**5. "Le CORS est vérifié par le navigateur, pas par le serveur. Une requête curl ignore complètement CORS."**

[ ] Vrai   [ ] Faux

---

## Réponses commentées

1. **FAUX mais partiellement vrai** — CORS=* sur un endpoint sans auth est effectivement moins grave (n'importe qui peut appeler l'API de toute façon). Le vrai danger : CORS=* sur un endpoint **avec auth par cookie de session**. Le navigateur envoie automatiquement les cookies → un site malveillant peut appeler l'API en se faisant passer pour l'utilisateur. C'est une **CSRF via CORS**.

2. **VRAI** — Une pub malveillante (`<iframe>`, JavaScript dans une bannière) peut déclencher des requêtes vers ton API si CORS le permet. L'utilisateur ne fait rien de suspect.

3. **FAUX** — La solution est une **liste blanche explicite et minimale** : uniquement les domaines que tu contrôles. Ex: `["http://localhost:8501", "https://homebutler.example.com"]`.

4. **VRAI en pratique, FAUX en principe** — En dev, CORS=* évite les frictions. Le vrai danger est en prod. Mais l'habitude de mettre `*` en dev fait qu'on l'oublie souvent en prod. La bonne pratique : gérer l'origine via une variable d'environnement `CORS_ORIGINS` dès le début.

5. **VRAI** — `curl` ignore totalement CORS. CORS est une restriction **des navigateurs web** pour protéger les utilisateurs. Un attaquant avec un script Python ou curl n'est pas concerné par CORS — il a d'autres vecteurs d'attaque.
