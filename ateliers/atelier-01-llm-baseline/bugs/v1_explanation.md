# Bug v1 — Temperature trop haute (T=0.9)

## Ce qui s'est passé

Le code utilisait `temperature=0.9` au lieu de `temperature=0.1` dans l'appel `get_llm()`. Résultat : les réponses varient à chaque exécution, même sur la même question, rendant l'assistant imprévisible.

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : À `temperature=0.9`, un LLM produira toujours la même réponse à la même question.

<details>
<summary>Réponse</summary>

**FAUX.** À `temperature=0.9`, le sampling est très aléatoire. Le même prompt peut produire des réponses radicalement différentes d'un run à l'autre. `temperature=0` est le seul réglage qui garantit le déterminisme complet.

</details>

---

**Question 2** : Pour un assistant maison factuel, une `temperature` élevée (0.7–1.0) est dangereuse car elle augmente la créativité et donc les hallucinations.

<details>
<summary>Réponse</summary>

**VRAI.** Une temperature élevée élargit la distribution des tokens possibles, incluant des tokens moins probables. Cela produit des réponses plus "créatives" mais aussi plus susceptibles d'inclure des informations inventées ou incohérentes. Pour un assistant factuel, on veut `T ≤ 0.3`.

</details>

---

**Question 3** : La `temperature` affecte uniquement le style de la réponse, pas le contenu factuel — un LLM ne peut pas inventer des faits à cause de la temperature.

<details>
<summary>Réponse</summary>

**FAUX.** La `temperature` influence directement le sampling des tokens. À T=0.9, le modèle peut sélectionner des tokens moins probables qui construisent des affirmations factuellement incorrectes. La `temperature` affecte bien le contenu factuel, pas seulement le style.

</details>

---

## À retenir

- `temperature=0.0` → déterministe, reproductible, recommandé pour les tests
- `temperature=0.1–0.3` → légèrement stochastique, recommandé pour la prod factuelle
- `temperature=0.7–1.0` → créatif, pour la génération de texte, risqué pour les faits
- **Fix** : remplacer `temperature=0.9` par `temperature=0.1` dans `get_llm()`
