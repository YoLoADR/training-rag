# Bug v3 At.07 — LLM-as-judge non déterministe (temperature > 0)

## Ce qui s'est passé

Le LLM-as-judge a été instancié avec `temperature=1.0`. Un juge à température élevée
échantillonne ses réponses : le même couple (question, réponse) reçoit des notes différentes
d'un run à l'autre. L'évaluation devient **non reproductible** — impossible de comparer deux
versions du pipeline de façon fiable.

## Questions vrai/faux

**Q1** : Un juge "créatif" (température haute) évalue mieux.
<details><summary>Réponse</summary>
**FAUX.** Pour NOTER, on veut de la CONSTANCE, pas de la créativité. Température 0 = le juge
applique le même barème à chaque fois. La créativité est utile pour GÉNÉRER, pas pour MESURER.
</details>

**Q2** : Avec temperature=0, le score est garanti identique à 100 % entre deux runs.
<details><summary>Réponse</summary>
**Presque.** temperature=0 rend le LLM quasi déterministe, mais certains fournisseurs gardent
une micro-variabilité (batching, versions). C'est BEAUCOUP plus stable qu'à température > 0,
et c'est ce qu'on veut pour une évaluation reproductible.
</details>

**Q3** : Ce réglage vaut aussi pour le juge RAGAS.
<details><summary>Réponse</summary>
**VRAI.** Le LLM passé à RAGAS via `LangchainLLMWrapper(get_llm(temperature=0))` doit aussi
être déterministe, pour la même raison. Toute notation (judge maison ou RAGAS) = température 0.
</details>

## À retenir
- Un évaluateur (LLM-judge ou juge RAGAS) doit être DÉTERMINISTE.
- **Fix** : `get_llm(temperature=0)` dans `llm_as_judge`.
