# Bug v1 At.08 — base_k == top_n (l'entonnoir du reranking est cassé)

## Ce qui s'est passé

`RERANK_BASE_K` est passé de 20 à 5, soit la même valeur que `RERANK_TOP_N` (5).
Le retriever de base ne fournit plus que 5 candidats, et le reranker en garde 5 :
il n'a donc **plus rien à filtrer**. Le cross-encoder se contente de réordonner
le même petit ensemble — on perd tout le bénéfice de précision (et on dépense des
calculs cross-encoder pour rien).

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : Le reranking améliore les résultats même si on ne lui donne que `top_n` candidats.

<details>
<summary>Réponse</summary>

**FAUX (en grande partie).** Le reranking a deux effets : (a) RÉORDONNER et (b) FILTRER.
Si `base_k == top_n`, il ne peut plus filtrer : tous les candidats ressortent. Le seul
effet restant est un réordonnancement marginal. L'intérêt principal — repêcher un bon
chunk situé au rang 8-15 du retrieval initial pour le faire entrer dans le top-5 —
disparaît.

</details>

---

**Question 2** : Plus `base_k` est grand, mieux c'est, sans limite.

<details>
<summary>Réponse</summary>

**FAUX.** Le cross-encoder score chaque paire (question, chunk) : son coût est linéaire
en `base_k`. `base_k=20` est un bon compromis rappel/latence sur ce corpus. `base_k=200`
serait 10× plus lent pour un gain marginal. L'entonnoir, c'est `base_k` assez grand pour
repêcher les bons chunks, mais pas trop pour rester rapide.

</details>

---

**Question 3** : Le reranking remplace le retriever vectoriel.

<details>
<summary>Réponse</summary>

**FAUX.** Le reranking vient APRÈS le retriever, en 2e étage. Étage 1 (bi-encodeur /
embeddings) = rapide, ratisse large parmi des milliers de chunks. Étage 2 (cross-encoder)
= lent mais précis, appliqué seulement aux `base_k` candidats. On ne peut pas mettre le
cross-encoder en étage 1 : scorer tout le corpus à chaque requête serait inutilisable.

</details>

---

## À retenir

- L'**entonnoir** est l'essence du reranking : `base_k` (large) → `top_n` (étroit).
- Règle de pouce : `base_k` ≈ 4 à 10 × `top_n` (ici 20 vs 5).
- **Fix** : remettre `RERANK_BASE_K=20` (≫ `RERANK_TOP_N=5`).
