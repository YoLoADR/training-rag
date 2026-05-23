# Bug v1 -- Dataset 100% categorie "autres"

## Ce qui s'est passe (en langage non-tech)

La fonction qui classe les questions par sujet a ete sabotee : elle met tout dans la categorie
"autres", meme les questions sur les equipements, les droits ou la marketplace.

Resultat : le modele fine-tune verra 150 questions "autres" et zero question sur
les producteurs locaux ou les artisans. Apres training, si un utilisateur lui demande
"Connais-tu un bon plombier dans le quartier ?", le modele ne saura strictement rien repondre.

## Analogie

C'est comme former un assistant en lui faisant lire uniquement des guides de cuisine,
alors qu'il devra aussi repondre sur la decoration, les travaux et les services. Le jour J,
sur ces trois derniers sujets, il sera completement bloque.

## Comportement observable

```bash
# Apres avoir applique le patch :
python ateliers/atelier-04-finetuning/prepare_dataset.py
# Tu verras :
#   Distribution par categorie :
#     autres        150  ████████████████████████████████
# (toutes les autres categories = 0)
```

## Grille d'explication (vrai / faux)

1. **Un dataset avec 90% "autres" et 10% "marketplace" est suffisamment equilibre.**
   - FAUX. Le modele sera bon sur "autres" et mauvais sur "marketplace".
     Pour du fine-tuning sur un domaine specifique, un ratio > 5:1 entre la categorie
     dominante et la minoritaire est deja risque.

2. **La fonction categorize() n'a pas d'impact sur la qualite du fine-tuning.**
   - FAUX. categorize() determine quelles questions tombent dans quelle categorie.
     Si elle est cassee, le dataset est biaise avant meme le training.

3. **On peut corriger un dataset desequilibre apres le training.**
   - FAUX. Le desequilibre doit etre corrige AVANT le training.
     Apres, il faut re-entrainer (cout GPU), ou accepter un modele defaillant sur la minorite.

4. **Sur-echantillonner la categorie "marketplace" est une solution valide.**
   - VRAI, mais seulement si categorize() classe correctement les paires.
     Si elle classe tout en "autres", il n'y a rien a sur-echantillonner.
     Le bug v1 doit d'abord etre corrige, puis on peut sur-echantillonner.

5. **Un dataset de 150 paires toutes dans la meme categorie est equivalent a 150 exemples equilibres.**
   - FAUX. 150 exemples du meme type = modele qui memorise ce type et ne generalise pas.
     La diversite du dataset est aussi importante que sa taille.

## Correction

Restaurer la logique de categorize() pour que chaque mot-cle metier soit detecte :
- "chaudiere", "radiateur", "vmc"... -> "equipements"
- "bail", "loyer", "preavis"... -> "droits"
- "consommation", "energie", "kwh"... -> "energie"
- "producteur", "artisan", "marketplace"... -> "marketplace"
- tout le reste -> "autres"
