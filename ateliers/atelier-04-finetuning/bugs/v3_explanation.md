# Bug v3 -- Absence de validation split (100/0/0 au lieu de 80/10/10)

## Ce qui s'est passe (en langage non-tech)

La fonction `split_train_val_test()` a ete modifiee pour mettre TOUTES les paires dans le
train set (100%), laissant le val set et le test set vides.

"J'ai omis le fichier de validation -- le modele s'entraine sans qu'on surveille
s'il apprend par coeur ou s'il generalise. On decouvre l'overfitting seulement au
test final, quand il est trop tard. C'est comme passer un examen sans jamais faire
de controles blancs : la deception au vrai examen peut etre severe."
(cf. Carnet de bord, lignes val_loss et Overfitting)

## Comportement observable

```bash
# Apres avoir applique le patch :
python ateliers/atelier-04-finetuning/prepare_dataset.py
# Tu verras :
#   Split 80/10/10 : train=150  val=0  test=0

# Consequence dans Colab :
#   - Le trainer ne peut pas surveiller val_loss
#   - On ne detecte pas l'overfitting pendant le training
#   - Le modele peut memoriser les 150 exemples et echouer sur toute question nouvelle
```

## Pourquoi c'est grave

Sans val set, tu ne peux pas savoir si le modele :
- Apprend vraiment (generalise) -> val_loss baisse avec train_loss
- Apprend par coeur (overfit) -> train_loss baisse mais val_loss remonte

Tu le saurais seulement a la fin, sur le test set. Mais a ce stade, il faut tout relancer
(plusieurs heures de GPU). Le val set est ton "systeme d'alarme precoce".

## Grille d'explication (vrai / faux)

1. **Un val set de 0 paires n'est pas un probleme si le dataset est de bonne qualite.**
   - FAUX. La qualite du dataset ne change rien au besoin de surveiller l'overfitting.
     Sans val set, on ne peut pas savoir quand arreter le training (early stopping).

2. **Le split 80/10/10 est une convention arbitraire, on peut mettre 95/5/0.**
   - PARTIELLEMENT VRAI. Le split exact depend du dataset. Mais un test set de 0 paires
     signifie qu'on n'evalue jamais le modele sur des donnees vraiment non vues.

3. **L'early stopping (arreter le training quand val_loss remonte) necessite un val set.**
   - VRAI. Sans val set, on ne peut pas appliquer l'early stopping et le modele va overfit.

4. **On peut evaluer l'overfitting uniquement en regardant train_loss.**
   - FAUX. train_loss baisse toujours (le modele apprend les exemples par coeur si besoin).
     L'overfitting se detecte quand val_loss commence a REMONTER alors que train_loss continue
     a baisser.

5. **Avec 150 paires, on peut se permettre de mettre tout en train et rien en val.**
   - FAUX. Avec seulement 150 paires, l'overfitting est ENCORE PLUS probable.
     Le val set est d'autant plus important que le dataset est petit.

## Correction

Restaurer le split 80/10/10 dans `split_train_val_test()` :
```python
n_train = int(n * 0.8)
n_val   = int(n * 0.1)
# le reste (~10%) va dans test
```
