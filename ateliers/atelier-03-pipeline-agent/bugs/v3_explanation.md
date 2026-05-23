# Bug v3 -- Agent sans max_iterations

## Ce qui s'est passe

Le parametre `max_iterations=8` a ete retire de `AgentExecutor(...)`.

## Comportement observable

Sans `max_iterations`, LangChain utilise sa valeur par defaut (15 dans la version 0.3.x).
Mais si le LLM hallucine des observations ou genere des reponses mal formatees en boucle,
l'agent peut depasser meme cette valeur par defaut et continuer indefiniment.

Resultat :
- L'utilisateur attend sans fin
- Chaque step = 1 appel API -> cout qui explose
- Sur des questions ou l'agent ne trouve pas de reponse, il boucle plutot que de s'arreter

## Grille d'explication (vrai / faux)

1. **Sans max_iterations, l'agent s'arrete automatiquement quand il a une reponse.**
   - VRAI dans le cas nominal. FAUX dans les cas pathologiques (hallucination d'observations,
     format de reponse incorrect). Dans ces cas, l'agent boucle.

2. **max_iterations=8 est une valeur arbitraire sans fondement.**
   - FAUX. 8 est un compromis : suffisant pour orchestrer 3-4 outils avec 1-2 retries,
     assez bas pour couper une boucle pathologique rapidement.

3. **handle_parsing_errors=True remplace l'utilite de max_iterations.**
   - FAUX. Ce sont deux mecanismes complementaires :
     - `handle_parsing_errors=True` : gere les erreurs de format LLM (une iteration)
     - `max_iterations=8` : plafonne le nombre total de tours, quelle que soit la cause

4. **Un agent qui depasse max_iterations retourne une erreur a l'utilisateur.**
   - FAUX (par defaut). Il retourne une reponse partielle avec ce qu'il a trouve jusqu'ici.
     C'est le comportement de `AgentExecutor` avec `early_stopping_method="force"`.

5. **max_iterations=100 est sans risque si les outils sont rapides.**
   - FAUX. Chaque iteration = 1 appel LLM. 100 iterations = potentiellement 100 appels API.
     Sur un agent a 5 outils, ca peut couter plusieurs euros par question.

## Correction

Ajouter `max_iterations=8` dans `AgentExecutor(...)`.
Valeur recommandee : entre 6 et 12 selon la complexite des questions.
