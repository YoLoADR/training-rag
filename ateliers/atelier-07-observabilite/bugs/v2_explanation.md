# Bug v2 At.07 — `reference` absent du dataset RAGAS (context_recall = NaN)

## Ce qui s'est passé

`build_eval_dataset` a été modifié pour NE PAS transmettre le champ `reference` (la réponse
de référence / ground truth) aux `SingleTurnSample`. Conséquence : les métriques
**context_recall** et **context_precision** (variantes « with reference ») ne peuvent plus
se calculer → elles renvoient **NaN**. L'évaluation paraît « marcher » mais deux métriques
clés sont silencieusement perdues.

## Questions vrai/faux

**Q1** : Toutes les métriques RAGAS ont besoin d'une réponse de référence.
<details><summary>Réponse</summary>
**FAUX.** `faithfulness` (ancrage dans le contexte) et `answer_relevancy` (pertinence vis-à-vis
de la question) se calculent SANS référence. En revanche `context_recall` et la variante par
défaut de `context_precision` exigent `reference`.
</details>

**Q2** : Dans notre dataset HomeButler, d'où vient la `reference` ?
<details><summary>Réponse</summary>
**VRAI : du champ `output` du dataset Alpaca.** Chaque paire `{instruction, input, output}` :
`input` = la question (`user_input`), `output` = la réponse gold (`reference`). C'est le même
dataset que celui du fine-tuning (AT04).
</details>

**Q3** : Un NaN sur une métrique est sans conséquence.
<details><summary>Réponse</summary>
**FAUX.** Une moyenne avec des NaN devient NaN (ou fausse selon l'agrégation). Pire : on croit
mesurer la couverture du contexte alors qu'on ne mesure rien. Un pipeline d'éval doit échouer
fort ou signaler les NaN, pas les masquer.
</details>

## À retenir
- `context_recall`/`context_precision` (with reference) exigent `reference`.
- **Fix** : `build_eval_dataset` doit propager `reference` à `SingleTurnSample`.
