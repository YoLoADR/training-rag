# Bug v3 At.09 — champ `content` non searchable → 0 résultat en hybride

## Ce qui s'est passé

Le champ `content` du schéma a été déclaré `searchable=False`. Conséquence : Azure n'indexe pas
ce texte pour BM25. L'index se construit, l'upload réussit (aucune erreur !), mais le volet
mots-clés de la recherche hybride est MUET → les requêtes hybrides renvoient peu ou pas de
résultats. Bug silencieux et déroutant.

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : `searchable=False` empêche aussi la recherche vectorielle sur ce champ.

<details>
<summary>Réponse</summary>

**FAUX (subtil).** `searchable` concerne l'indexation plein-texte (BM25) du champ texte. La
recherche vectorielle se fait sur `content_vector` (un autre champ). Mais en mode HYBRIDE, le
volet BM25 sur `content` est neutralisé → on perd la moitié de l'hybride.

</details>

---

**Question 2** : Un champ peut être stocké mais non recherchable.

<details>
<summary>Réponse</summary>

**VRAI.** Les attributs sont indépendants : `retrievable` (renvoyé dans les résultats),
`searchable` (indexé BM25), `filterable`, `sortable`, `facetable`. On peut stocker/retourner un
champ sans le rendre recherchable — mais alors la recherche plein-texte l'ignore.

</details>

---

**Question 3** : Ce bug aurait provoqué une erreur à l'ingestion.

<details>
<summary>Réponse</summary>

**FAUX.** C'est tout le piège : l'ingestion réussit, l'index existe, aucune exception. Le
problème n'apparaît qu'à la REQUÊTE (peu/pas de résultats). Les bugs de configuration d'index
sont silencieux — d'où l'importance de tester une requête après ingestion.

</details>

---

## À retenir

- `searchable=True` sur le champ texte est requis pour le volet BM25 de la recherche hybride.
- Un mauvais flag de champ ne plante pas à l'ingestion : il dégrade silencieusement les requêtes.
- **Fix** : `SearchField(name="content", ..., searchable=True)`.
