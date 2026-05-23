# Bug v2 -- Trop d'outils (15 dans la liste)

## Ce qui s'est passe

12 outils fictifs ont ete ajoutes a la liste `ALL_TOOLS`, portant le total a 16.

## Comportement observable

L'agent ReAct recoit au debut de chaque boucle la liste complete des outils avec leurs descriptions.
Avec 16 outils, le contexte du prompt d'agent devient tres long, et le LLM :
- A plus de difficulte a choisir le bon outil
- Peut halluciner des noms d'outils qui n'existent pas
- Produit plus de steps inutiles avant d'arriver a une reponse
- Est plus susceptible de depasser `max_iterations`

## Grille d'explication (vrai / faux)

1. **Plus d'outils = agent plus capable.**
   - FAUX. Un agent avec 20 outils mal definis est moins efficace qu'un agent avec 4 outils
     bien definis. La qualite des descriptions et la pertinence des outils importent plus que la quantite.

2. **Le nombre optimal d'outils pour un agent ReAct est entre 1 et 7.**
   - VRAI. Au-dela, la confusion augmente. Si tu as plus de cas d'usage, la solution est de
     creer plusieurs agents specialises (routing entre agents) plutot qu'un seul agent generaliste.

3. **Si on a besoin de 15 fonctionnalites, on doit mettre 15 outils dans un seul agent.**
   - FAUX. On peut creer des outils composites (ex: un outil "recherche_logement" qui encapsule
     plusieurs sous-fonctions), ou router vers des agents specialises selon le type de question.

4. **La latence de l'agent n'est pas affectee par le nombre d'outils.**
   - FAUX. Chaque tool description est envoyee dans le prompt a chaque tour. Plus d'outils =
     prompt plus long = plus de tokens = plus lent et plus cher.

5. **Avoir des outils fictifs/inutiles dans la liste est sans consequence.**
   - FAUX. Chaque outil inutile est du "bruit" pour le LLM. Il peut l'appeler par erreur,
     produire une observation vide, et continuer a errer avant de trouver le bon outil.

## Correction

Retirer les 12 outils fictifs de `ALL_TOOLS`. Garder uniquement les 4 outils metier :
`search_docs_tool`, `analyze_energy_tool`, `find_products_tool`, `get_weather_tool`.
