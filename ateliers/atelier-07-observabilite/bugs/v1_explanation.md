# Bug v1 At.07 — mauvais import du CallbackHandler Langfuse (v3 au lieu de v2)

## Ce qui s'est passé

L'import a été changé en `from langfuse.langchain import CallbackHandler` — c'est l'API
**Langfuse v3**. Or le projet est épinglé sur **v2** (`langfuse==2.57.1`), où le module
`langfuse.langchain` n'existe pas. Dès qu'on configure des clés, `get_langfuse_handler`
lève `ModuleNotFoundError` → aucune trace n'arrive dans le dashboard.

## Questions vrai/faux

**Q1** : Mettre à jour Langfuse en dernière version réglerait le problème.
<details><summary>Réponse</summary>
**FAUX (et risqué).** Le projet pin v2 volontairement : l'intégration LangChain a changé
en v3 (`langfuse.langchain`) puis en v4 (réécriture OTEL). Passer en v3/v4 casserait d'autres
parties. La bonne correction est d'utiliser l'import correspondant à la version installée :
`from langfuse.callback import CallbackHandler` (v2).
</details>

**Q2** : Sans clés Langfuse, ce bug ne se manifeste pas.
<details><summary>Réponse</summary>
**VRAI.** `get_langfuse_handler` retourne `None` AVANT l'import si les clés sont absentes
(no-op). Le bug ne se déclenche qu'avec des clés configurées — d'où un test d'analyse
statique du code, déterministe et indépendant de l'environnement.
</details>

**Q3** : Le tracing échoue bruyamment (le script plante).
<details><summary>Réponse</summary>
**Ça dépend.** Ici l'import lève une exception → on s'en rend compte. Mais beaucoup de bugs
d'observabilité sont SILENCIEUX (traces non envoyées, mais le script tourne). D'où
l'importance de VÉRIFIER que les traces arrivent réellement, pas de supposer.
</details>

## À retenir
- L'import du CallbackHandler dépend de la version : v2 = `langfuse.callback`, v3 = `langfuse.langchain`.
- **Fix** : `from langfuse.callback import CallbackHandler` (cohérent avec `langfuse==2.57.1`).
