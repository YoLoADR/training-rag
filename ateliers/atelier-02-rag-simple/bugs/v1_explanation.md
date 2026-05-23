# Bug v1 At.02 — chunk_size=2000 (trop grand)

## Ce qui s'est passé

`chunk_size` a été passé de 512 à 2000. Les chunks sont devenus très gros (plusieurs paragraphes entiers dans un seul embedding). Résultat : l'embedding moyen sur 2000 caractères noie les détails précis — le retriever ne trouve plus les bons chunks sur des questions spécifiques.

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : Plus les chunks sont grands, mieux c'est — le LLM a plus de contexte pour répondre.

<details>
<summary>Réponse</summary>

**FAUX.** Il y a un compromis. Chunks trop grands = embedding "moyen" qui ne représente aucun sujet précis → retriever rate. Chunks trop petits = contexte mutilé, phrase coupée → LLM n'a pas assez d'info. Sweet spot pour les PDFs techniques = 400-800 chars + overlap 50-100.

</details>

---

**Question 2** : Avec chunk_size=2000, le nombre total de chunks diminue.

<details>
<summary>Réponse</summary>

**VRAI.** Si les PDFs font 10 000 caractères en tout et que chunk_size=2000 avec overlap=50, on obtient environ 5 chunks (10000/2000 ≈ 5). Avec chunk_size=512, on obtient ~20 chunks. Moins de chunks = chaque chunk est plus générique = embeddings moins précis.

</details>

---

**Question 3** : Le Recall@5 peut baisser si chunk_size est trop grand.

<details>
<summary>Réponse</summary>

**VRAI.** Avec des chunks de 2000 caractères, l'embedding couvre plusieurs sujets à la fois (marque de la chaudière + codes d'erreur + instructions d'entretien). La distance cosinus entre la requête "Quelle est la marque de ma chaudière ?" et ce chunk géant est plus faible que si le chunk ne parlait que de la marque. Le retriever peut préférer d'autres chunks.

</details>

---

## À retenir

- Le sweet spot pour les PDFs techniques HomeButler = `chunk_size=512`, `chunk_overlap=50`
- Trop grand (> 1000) : embedding bruité, retriever confus
- Trop petit (< 200) : contexte insuffisant pour le LLM
- **Fix** : remplacer `chunk_size=2000` par `chunk_size=512`
