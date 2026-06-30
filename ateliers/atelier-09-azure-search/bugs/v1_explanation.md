# Bug v1 At.09 — dimension du schéma (1536) ≠ dimension de l'embedding (384)

## Ce qui s'est passé

`AZURE_VECTOR_DIM` est passé de 384 à 1536 (valeur typique d'un embedding Azure OpenAI
`text-embedding-ada-002`). Or on utilise **fastembed** (`paraphrase-multilingual-MiniLM-L12-v2`)
qui produit des vecteurs de **384** dimensions. Le champ vectoriel de l'index déclare donc 1536,
mais on y pousse des vecteurs de 384 → **Azure rejette l'upload** (la longueur du vecteur doit
égaler la dimension déclarée du champ).

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : La dimension du champ vectoriel peut être choisie librement.

<details>
<summary>Réponse</summary>

**FAUX.** Elle est DICTÉE par le modèle d'embedding : 384 pour MiniLM, 1536 pour
text-embedding-3-small/ada-002, 3072 pour text-embedding-3-large. Le schéma doit refléter
exactement la sortie de ton encodeur.

</details>

---

**Question 2** : Si on laisse LangChain créer l'index automatiquement, ce bug n'arrive pas.

<details>
<summary>Réponse</summary>

**VRAI — mais on perd le contrôle.** `AzureSearch.add_documents` peut créer l'index en infèrant
la dimension du 1er vecteur. C'est pratique en proto, mais ici on crée le schéma À LA MAIN
(data plane) pour MAÎTRISER les champs — d'où l'obligation d'accorder la dimension nous-mêmes.
C'est précisément le piège que cet atelier enseigne.

</details>

---

**Question 3** : `az search` permet de corriger la dimension de l'index en CLI.

<details>
<summary>Réponse</summary>

**FAUX.** `az search` gère le SERVICE (control plane), pas le contenu. La définition d'index
(data plane) se fait UNIQUEMENT via SDK/REST. De plus, on ne change pas la dimension d'un champ
existant : il faut recréer l'index.

</details>

---

## À retenir

- dimension du champ vectoriel = dimension de l'embedding (ici **384** pour fastembed MiniLM).
- Créer le schéma à la main (data plane) donne le contrôle… et la responsabilité de la cohérence.
- **Fix** : `AZURE_VECTOR_DIM = 384`.
