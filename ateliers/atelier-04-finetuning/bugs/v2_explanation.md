# Bug v2 -- Learning rate trop grand (1e-2)

## Ce qui s'est passe (en langage non-tech)

La valeur `LEARNING_RATE = 1e-2` a ete configuree dans le fichier de preparation du dataset.
C'est 50 a 500 fois trop grand pour LoRA.

"J'ai mis un learning rate trop grand -- le modele saute trop loin a chaque correction
et n'apprend plus rien. Ca se manifeste par une loss qui devient NaN (valeur impossible)
des le 1er epoch. C'est comme tourner un bouton de volume a fond d'un coup : ca grille le haut-parleur."
(cf. Carnet de bord, ligne Learning rate)

## Comportement observable dans Colab

Si tu lances le training avec `lr=1e-2`, tu verras dans les logs :
```
Epoch 1/5
Step 10/30 | loss: 2.3145
Step 20/30 | loss: nan      <- le modele explose
Step 30/30 | loss: nan
```

Une fois que la loss est NaN, le training continue mais le modele ne "repare" pas --
il reste dans un etat brise jusqu'a la fin des epochs.

## Grille d'explication (vrai / faux)

1. **Un learning rate de 1e-2 est toujours trop grand pour le fine-tuning.**
   - FAUX (nuance). 1e-2 peut etre correct pour des petits modeles ou d'autres architectures.
     Pour LoRA sur Mistral-7B, c'est systematiquement trop grand. Sweet spot LoRA : 1e-4 a 5e-4.

2. **Quand la loss devient NaN, on peut continuer le training et ca se resoudra.**
   - FAUX. Une loss NaN signifie que les poids du modele sont devenus +/- infinis.
     Il faut ARRETER, corriger le lr, et recommencer depuis le debut.

3. **Le learning rate par defaut d'un tuto generique est toujours adapte a LoRA.**
   - FAUX. Les tutos plein FT utilisent souvent lr=2e-5 a 3e-5 sur Adam.
     LoRA avec un rang r=8 necessite un lr plus eleve (1e-4 a 5e-4) car on entraine
     beaucoup moins de parametres. Copier le lr d'un autre contexte = erreur classique.

4. **Trop petit (lr=1e-7) est aussi un bug.**
   - VRAI. Avec lr trop petit, le modele "apprend" mais si lentement qu'apres 5 epochs
     la loss a peine bouge. On ne detecte pas le probleme pendant le training.

5. **La bonne approche est de tester plusieurs lr (grid search) plutot que d'en choisir un.**
   - VRAI en production. En atelier, pour gagner du temps Colab, on fixe lr=2e-4 (valeur sure)
     et on fait varier un seul autre parametre a la fois.

## Correction

```python
LEARNING_RATE = 2e-4  # Sweet spot pour LoRA r=8 sur Mistral-7B
```

Plage valide pour LoRA : 1e-5 a 5e-4.
