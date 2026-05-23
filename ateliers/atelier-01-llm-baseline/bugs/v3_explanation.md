# Bug v3 — Pas de system prompt (modèle off-topic)

## Ce qui s'est passé

Le `SystemMessage` (system prompt HomeButler) a été supprimé. Le LLM reçoit donc uniquement le message utilisateur, sans contexte de rôle ni contrainte de comportement. Il répond en mode "assistant généraliste" et peut fabriquer des réponses sur des données qu'il ne peut pas connaître.

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : Sans system prompt, le LLM peut quand même adopter un comportement approprié si l'utilisateur formule bien sa question.

<details>
<summary>Réponse</summary>

**VRAI dans certains cas, mais pas fiable.** Sans system prompt, le LLM improvise un comportement "par défaut" qui dépend de son RLHF (entraînement par renforcement). Claude dira souvent "je ne sais pas" sur des données privées, mais ce comportement n'est pas garanti et peut varier selon le modèle, la version, et la formulation. Le system prompt est le seul moyen **fiable et prévisible** de cadrer le comportement.

</details>

---

**Question 2** : Le system prompt est visible par l'utilisateur final dans l'interface d'un chatbot.

<details>
<summary>Réponse</summary>

**FAUX.** Le system prompt est envoyé à l'API mais est invisible pour l'utilisateur dans une interface standard. C'est précisément pourquoi il peut contenir des instructions de comportement, des règles métier et des contraintes de ton — sans que l'utilisateur puisse les contourner facilement via le chat.

</details>

---

**Question 3** : Un system prompt bien rédigé peut complètement empêcher les hallucinations d'un LLM sur des données privées.

<details>
<summary>Réponse</summary>

**FAUX.** Le system prompt peut réduire significativement les hallucinations en instruisant le modèle à dire "je ne sais pas" plutôt qu'inventer. Mais il ne peut pas lui donner des informations qu'il ne possède pas. La solution complète = system prompt (cadrage comportemental) + RAG (injection des vraies données). Le system prompt seul est insuffisant pour les données privées volumineuses.

</details>

---

## À retenir

- Le system prompt = fiche de poste de l'assistant : rôle, périmètre, contraintes de ton
- Sans system prompt, le LLM adopte un comportement non garanti
- **Fix** : ajouter `SystemMessage(content=SYSTEM_PROMPT)` avant `HumanMessage` dans `llm.invoke([...])`
- Ordre correct : `[SystemMessage(...), HumanMessage(...)]`
- Le system prompt est la première ligne de défense — le RAG est la deuxième
