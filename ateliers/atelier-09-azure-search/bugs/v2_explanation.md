# Bug v2 At.09 — search_type "similarity" au lieu de "hybrid"

## Ce qui s'est passé

Le `search_type` par défaut de `get_azure_store` est passé de `"hybrid"` à `"similarity"`
(recherche vectorielle PURE). Sur des questions dont le vocabulaire diverge des documents,
le recall chute : le vecteur seul rate ce que les mots-clés auraient trouvé.

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : La recherche hybride = recherche vectorielle + recherche par mots-clés (BM25).

<details>
<summary>Réponse</summary>

**VRAI.** Azure AI Search exécute les DEUX et fusionne les classements via RRF (Reciprocal Rank
Fusion). On récupère le meilleur des deux mondes : le sens (vecteurs) ET les correspondances
exactes de termes (BM25), utiles pour les noms propres, codes, références.

</details>

---

**Question 2** : "similarity" est toujours moins bon que "hybrid".

<details>
<summary>Réponse</summary>

**FAUX (nuance).** Sur des requêtes purement sémantiques sans terme-clé discriminant, les deux
se valent. Mais en pratique, sur des corpus techniques (codes erreur, marques, références),
l'hybride gagne presque toujours — d'où le bon défaut "hybrid".

</details>

---

**Question 3** : "semantic_hybrid" = "hybrid" + un reclassement sémantique (semantic ranker).

<details>
<summary>Réponse</summary>

**VRAI.** `semantic_hybrid` ajoute le semantic ranker d'Azure par-dessus l'hybride. Il exige un
tier Basic+ ET une semantic configuration dans le schéma. C'est l'équivalent managé du reranking
qu'on a fait localement en AT08.

</details>

---

## À retenir

- "similarity" = vecteur seul ; "hybrid" = vecteur + BM25 (RRF) ; "semantic_hybrid" = + semantic ranker.
- Bon défaut : **"hybrid"** (rattrape le vocabulaire divergent).
- **Fix** : `search_type: str = "hybrid"` dans `get_azure_store`.
