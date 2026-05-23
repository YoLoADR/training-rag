# Bug v2 At.02 — chunk_overlap=0 (coupure de phrase)

## Ce qui s'est passé

`chunk_overlap` a été passé de 50 à 0. Résultat : les chunks sont découpés sans aucun chevauchement. Si une information clé se trouve exactement à la frontière entre deux chunks, elle est perdue — coupée dans l'un ou l'autre, mais jamais préservée entière dans un seul chunk.

## Questions vrai/faux — réponds avant de regarder les réponses

**Question 1** : chunk_overlap=0 est optimal car il évite les données redondantes dans l'index.

<details>
<summary>Réponse</summary>

**FAUX.** L'overlap est intentionnel. Il garantit que les informations à cheval sur deux chunks (ex: une phrase qui commence à la fin du chunk N et se termine au début du chunk N+1) sont entièrement présentes dans au moins l'un des deux. L'overhead de redondance est faible (50 chars sur 512 = ~10%) et le gain en qualité de retrieval est significatif.

</details>

---

**Question 2** : Avec chunk_overlap=0 et chunk_size=512, la somme des longueurs de tous les chunks égale la longueur totale des documents.

<details>
<summary>Réponse</summary>

**VRAI (environ).** Sans overlap, chaque caractère du document apparaît dans exactement 1 chunk. Avec overlap=50, les 50 caractères à chaque frontière apparaissent dans 2 chunks consécutifs → la taille totale des chunks > taille totale des documents.

</details>

---

**Question 3** : Le problème de chunk_overlap=0 se voit surtout sur les questions qui portent sur des informations courtes et précises (ex: un code erreur, un numéro de téléphone).

<details>
<summary>Réponse</summary>

**VRAI.** Une information courte qui se retrouve à cheval entre deux chunks (ex: "Code erreur F4 : signifie..." coupé entre deux chunks) est littéralement perdue. Ni le chunk précédent ni le suivant ne contient l'information complète. L'overlap garantit que ce type d'information critique reste dans un seul chunk.

</details>

---

## À retenir

- `chunk_overlap` = fenêtre de chevauchement entre chunks consécutifs (en caractères)
- `chunk_overlap=50` → les 50 derniers caractères du chunk N sont les 50 premiers du chunk N+1
- L'overhead est faible (~10%) pour un gain qualité important
- **Fix** : remplacer `chunk_overlap=0` par `chunk_overlap=50`
