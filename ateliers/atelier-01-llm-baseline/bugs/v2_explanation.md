# Bug v2 — max_tokens=50 (réponse tronquée)

## Ce qui s'est passé

Le code utilisait `max_tokens=50` dans `get_llm()`. Un token ≈ 4 caractères → 50 tokens ≈ 200 caractères. La réponse du LLM était coupée brutalement en plein milieu d'une phrase, sans signal d'avertissement.

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : `max_tokens=50` signifie que le LLM peut produire au maximum 50 mots en réponse.

<details>
<summary>Réponse</summary>

**FAUX.** `max_tokens` est exprimé en **tokens**, pas en mots. 1 token ≈ 3–4 caractères en français (les mots courts comme "le", "un", "à" font 1 token ; un mot long comme "chaudière" fait 2–3 tokens). 50 tokens ≈ 35–40 mots environ — très court pour une réponse utile.

</details>

---

**Question 2** : Quand un LLM atteint la limite `max_tokens`, il termine proprement la phrase en cours.

<details>
<summary>Réponse</summary>

**FAUX.** Quand le LLM atteint `max_tokens`, il s'arrête immédiatement, même en plein milieu d'un mot ou d'une phrase. Il n'existe pas de mécanisme natif de "terminer proprement" — c'est au développeur de fixer un `max_tokens` suffisamment grand pour le type de réponse attendu.

</details>

---

**Question 3** : Augmenter `max_tokens` augmente toujours le coût et la latence, même si la réponse est courte.

<details>
<summary>Réponse</summary>

**FAUX.** `max_tokens` est une limite haute, pas une longueur cible. Si le LLM termine sa réponse en 80 tokens alors que `max_tokens=1024`, on paie et on attend uniquement les 80 tokens produits. La latence et le coût dépendent du nombre de tokens **réellement générés**, pas de la limite.

</details>

---

## À retenir

- `max_tokens` = plafond de tokens en sortie, pas une cible
- Valeur recommandée pour un assistant maison : `max_tokens=1024` (réponses complètes sans gaspiller)
- Pour des résumés courts : `max_tokens=256` peut suffire
- **Fix** : supprimer `max_tokens=50` ou le remplacer par `max_tokens=1024`
