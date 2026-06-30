# Bug v2 At.08 — multi-query qui ne demande qu'UNE reformulation

## Ce qui s'est passé

Le prompt `MULTIQUERY_PROMPT` a été réécrit pour ne demander qu'**1** reformulation
au lieu de 3. Résultat : le `MultiQueryRetriever` ne génère plus de variantes
diverses — il interroge l'index avec une seule reformulation, ce qui n'apporte
quasiment rien par rapport à la requête initiale.

Le point conceptuel clé : **la diversité des requêtes vient du PROMPT** (on demande
explicitement N versions), **pas de la température**. Un seul appel LLM produit les
N reformulations d'un coup.

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : Pour diversifier les reformulations du multi-query, il faut augmenter la température du LLM.

<details>
<summary>Réponse</summary>

**FAUX.** Le `MultiQueryRetriever` génère toutes ses variantes dans **un seul appel**,
piloté par la consigne du prompt ("génère 3 reformulations différentes"). La diversité
est demandée explicitement, pas obtenue par échantillonnage stochastique. On garde même
`temperature=0` pour la reproductibilité.

</details>

---

**Question 2** : Le multi-query augmente le RAPPEL (recall), pas forcément la précision.

<details>
<summary>Réponse</summary>

**VRAI.** En interrogeant l'index avec plusieurs formulations puis en prenant l'UNION
des documents, on récupère des chunks qu'une seule formulation aurait manqués (vocabulaire
divergent). C'est complémentaire du reranking, qui lui améliore la précision/l'ordre.
On combine souvent les deux : multi-query (rappel) → reranking (précision).

</details>

---

**Question 3** : Demander 10 reformulations est toujours mieux que 3.

<details>
<summary>Réponse</summary>

**FAUX.** Trop de reformulations = plus d'appels de retrieval, plus de bruit dans l'union,
plus de latence, et des variantes redondantes. 3 à 5 reformulations couvrent l'essentiel
des angles (synonymes, registre technique, registre usager).

</details>

---

## À retenir

- La diversité multi-query vient de la **consigne du prompt**, pas de la température.
- Multi-query = levier de **rappel** ; reranking = levier de **précision**.
- **Fix** : redemander plusieurs reformulations (ex. 3) dans `MULTIQUERY_PROMPT`.
