# Bug v1 -- Description d'outil bacle

## Ce qui s'est passe

La description de `search_docs_tool` a ete remplacee par "cherche des documents".

## Comportement observable

L'agent ReAct lit les descriptions de tous ses outils pour decider lequel appeler.
Avec une description aussi vague, il ne sait pas :
- Quand utiliser cet outil plutot qu'un autre
- Quel type de questions il peut traiter
- Comment formuler l'input

Resultat : l'agent ignore l'outil ou l'appelle avec des inputs mal formes.

## Grille d'explication (vrai / faux)

Reponds sans regarder la reponse, puis verifie :

1. **La description d'un outil sert uniquement a l'humain dev qui lit le code.**
   - FAUX. Le LLM lit la description a chaque appel pour decider s'il doit utiliser l'outil.
     C'est un contrat entre toi et le modele de langage.

2. **Une description courte est preferable pour economiser des tokens.**
   - FAUX. Une description trop courte entraine des outils ignores ou mal utilises.
     Le cout de tokens d'une bonne description (200 chars) est negligeable par rapport
     au cout d'une reponse incorrecte.

3. **La description doit mentionner : (a) le domaine, (b) quand utiliser l'outil,
   (c) le format de l'input.**
   - VRAI. Ces trois elements sont necessaires pour que le LLM prenne la bonne decision.

4. **Si le LLM n'utilise pas un outil, c'est forcement un bug dans le code Python.**
   - FAUX. La cause la plus frequente est une description insuffisante ou ambigue.
     80% du succes d'un agent vient de la qualite des descriptions d'outils.

5. **On peut compenser une mauvaise description en ajoutant plus d'outils.**
   - FAUX. Plus d'outils avec de mauvaises descriptions = plus de confusion.
     Le modele a encore moins de contexte pour choisir.

## Correction

Restaurer une description complete qui mentionne :
- Le domaine couvert (bail, notices, equipements, DPE...)
- Quand l'utiliser ("pour toute question sur le fonctionnement...")
- Le format de l'input ("Input : question ou mots-cles en francais")
