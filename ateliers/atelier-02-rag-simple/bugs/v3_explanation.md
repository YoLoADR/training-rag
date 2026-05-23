# Bug v3 At.02 — Reconstruction index à chaque query

## Ce qui s'est passé

`build_faiss_index(force_rebuild=True)` était appelé à l'intérieur de la boucle de requêtes. Résultat : à chaque question posée, le pipeline recalculait les embeddings de tous les chunks et reconstruisait l'index complet (10-30s). L'observable : la première requête prend 30s, la deuxième aussi, etc.

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : Reconstruire l'index FAISS à chaque requête donne des résultats plus précis car l'index est "frais".

<details>
<summary>Réponse</summary>

**FAUX.** L'index FAISS est déterministe : si les documents et le modèle d'embeddings n'ont pas changé, l'index reconstruit sera identique au précédent. Reconstruire à chaque requête est une perte de temps pure — le résultat est le même que charger l'index sauvegardé.

</details>

---

**Question 2** : FAISS peut sauvegarder l'index sur disque et le recharger sans recalculer les embeddings.

<details>
<summary>Réponse</summary>

**VRAI.** `build_faiss_index()` sauvegarde l'index dans `data/faiss_index/` (fichiers binaires). Lors du prochain appel avec `force_rebuild=False`, il rechargera l'index depuis le disque en quelques millisecondes — sans recalculer un seul embedding. C'est précisément pour ça que la persistance existe.

</details>

---

**Question 3** : La latence observable est le seul moyen de détecter ce bug en production.

<details>
<summary>Réponse</summary>

**FAUX (pas uniquement).** La latence est le signal le plus évident (10-30s au lieu de < 1s). Mais on peut aussi monitorer le CPU (pic à 100% à chaque requête plutôt qu'idle) ou observer les logs ("Construction de l'index FAISS..." qui s'affiche à chaque requête au lieu d'une seule fois au démarrage). En prod : Langfuse ou tout outil d'observabilité montre les latences p95.

</details>

---

## À retenir

- Construire l'index = opération coûteuse (calcul de tous les embeddings) → à faire **une seule fois**
- Retrieval = opération rapide (recherche ANN dans l'index) → < 1s
- Pattern correct :
  ```python
  # Construction — une seule fois au démarrage
  faiss_store = build_faiss_index(chunks, force_rebuild=True)

  # Retrieval — à chaque requête (rapide)
  for q in questions:
      results = faiss_store.similarity_search(q, k=5)
  ```
- **Fix** : déplacer `build_faiss_index()` en dehors de la boucle de requêtes
