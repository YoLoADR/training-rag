# Bug v3 At.08 — top_n non transmis au reranker (sortie non bornée)

## Ce qui s'est passé

`FlashrankRerank` a été instancié sans l'argument `top_n`. Le reranker applique
alors sa valeur **par défaut** (3) au lieu des 5 documents attendus. La chaîne
en aval (prompt LLM) reçoit le mauvais nombre de chunks : trop peu de contexte,
résultats incohérents avec le reste du pipeline qui attend `top_n=5`.

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : `top_n` du reranker et `k` du retriever de base, c'est la même chose.

<details>
<summary>Réponse</summary>

**FAUX.** `base_k` (ou `k`) = nombre de candidats récupérés par le retriever vectoriel
(étage 1, large). `top_n` = nombre de documents conservés APRÈS reclassement cross-encoder
(étage 2, étroit). L'entonnoir, c'est précisément `base_k` ≫ `top_n`.

</details>

---

**Question 2** : Si on oublie `top_n`, le reranker plante avec une erreur.

<details>
<summary>Réponse</summary>

**FAUX.** Il ne plante pas — il applique une valeur par défaut silencieuse. C'est plus
sournois qu'un crash : le pipeline tourne, mais renvoie un nombre de chunks inattendu.
Les bugs de configuration silencieux sont les plus difficiles à diagnostiquer (d'où
l'intérêt d'un test qui vérifie la taille de sortie).

</details>

---

**Question 3** : La taille de sortie (`top_n`) influe sur le coût LLM en aval.

<details>
<summary>Réponse</summary>

**VRAI.** Chaque chunk conservé est injecté dans le prompt du LLM = des tokens en plus
(coût + latence). `top_n` est un curseur précision/coût : trop petit → contexte insuffisant,
trop grand → bruit et facture. 3-5 chunks rerankés est un bon réglage pour HomeButler.

</details>

---

## À retenir

- `base_k` (candidats, étage 1) ≠ `top_n` (sortie, étage 2).
- Un paramètre oublié ne crashe pas toujours : il prend une valeur par défaut silencieuse.
- **Fix** : passer `top_n=top_n` à `FlashrankRerank(model=..., top_n=top_n)`.
