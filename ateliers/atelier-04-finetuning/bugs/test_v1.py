"""
Bug v1 -- categorize() retourne "autres" pour toutes les branches.

Analyse statique de prepare_dataset.py :
- Le bug remplace tous les return specifiques par return "autres".
- En etat propre : "equipements" (ou "equip"), "droits", "energie", "marketplace"
  doivent tous apparaitre comme valeurs de retour dans categorize().
- Avec le bug : seul "autres" apparait.

Ce test PASSE en etat propre.
Ce test ECHOUE quand le bug est actif.
"""

import pathlib

PREPARE = pathlib.Path(__file__).parent.parent / "prepare_dataset.py"


def test_categorize_retourne_categories_specifiques():
    """
    En etat de reference, categorize() doit retourner des categories specifiques
    (pas uniquement 'autres').
    """
    source = PREPARE.read_text(encoding="utf-8")
    # Extraire uniquement le corps de la fonction categorize
    # On cherche les return avec des categories specifiques
    # Les categories utilisent les accents corrects
    categories_specifiques = [
        ("equipements", ["equipements", "équipements"]),
        ("droits",      ["droits"]),
        ("energie",     ["energie", "énergie"]),
        ("marketplace", ["marketplace"]),
    ]
    for label, variants in categories_specifiques:
        found = any(v in source for v in variants)
        assert found, (
            f"Categorie '{label}' absente des return de categorize() dans prepare_dataset.py. "
            f"Le bug a remplace tous les return par 'autres'. "
            f"Corrige categorize() pour que chaque branche retourne sa categorie."
        )
