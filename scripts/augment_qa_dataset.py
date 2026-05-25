"""
Augmentation du dataset QA concierge : 150 → ~500 paires.

Techniques employées (sans LLM — reproductible et déterministe) :
  1. Paraphrase de question via règles linguistiques (2 variantes par paire)
  2. Reformulation de réponse (variation de style : formel / direct)
  3. Questions négatives / contre-exemples (validation du refus ou de la limite)

Sortie : data/qa_dataset/augmented_concierge_qa.jsonl (~500 paires)
Le fichier original concierge_qa.jsonl (150 paires) est conservé intact.

Usage :
    python scripts/augment_qa_dataset.py
    python scripts/augment_qa_dataset.py --input data/qa_dataset/concierge_qa.jsonl \
                                          --output data/qa_dataset/augmented_concierge_qa.jsonl \
                                          --target 500
"""

import argparse
import json
import os
import random
import re
import sys
from pathlib import Path

# ── Constantes ────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "data" / "qa_dataset" / "concierge_qa.jsonl"
DEFAULT_OUTPUT = BASE_DIR / "data" / "qa_dataset" / "augmented_concierge_qa.jsonl"
DEFAULT_TARGET = 500

INSTRUCTION = (
    "Tu es HomeButler, conciergerie domestique bienveillante. "
    "Réponds à la question suivante sur le logement."
)

# ── Règles de paraphrase (FR) ─────────────────────────────────────────────────

# (pattern, remplacement) — ordre important, les patterns les plus longs d'abord
_QUESTION_REWRITES = [
    # Interrogatifs → variantes
    (r"^Comment\s+", "De quelle façon "),
    (r"^Comment\s+", "Quel est le moyen de "),
    (r"^Pourquoi\s+", "Pour quelle raison "),
    (r"^Quand\s+", "À quel moment "),
    (r"^Où\s+", "Dans quel endroit "),
    (r"^Que\s+", "Qu'est-ce que "),
    (r"^Quel\s+est\s+", "Quelle est la valeur de "),
    (r"^Quels?\s+sont\s+", "Pouvez-vous me lister "),
    # Structures verbales
    (r"^Puis-je\s+", "Est-ce que je peux "),
    (r"^Dois-je\s+", "Est-il nécessaire que je "),
    (r"^Faut-il\s+", "Est-il obligatoire de "),
    (r"^Est-ce\s+que\s+", ""),
    # Reformulations contextuelles
    (r"^Ma\s+", "La "),
    (r"^Mon\s+", "Le "),
    (r"^mes\s+", "les "),
]

_LOCATAIRE_PREFIXES = [
    "En tant que locataire, ",
    "En tant qu'habitant du logement, ",
    "Pour mon appartement, ",
    "Concernant mon logement : ",
    "Dans ma situation de locataire, ",
]

_FORMEL_SUFFIXES = [
    " Merci de me conseiller.",
    " Pourriez-vous m'éclairer ?",
    " Quelle est votre recommandation ?",
    " Qu'en pensez-vous ?",
]


def _apply_first_matching_rewrite(q: str) -> str | None:
    """Applique la première règle de réécriture qui matche."""
    for pattern, replacement in _QUESTION_REWRITES:
        if re.match(pattern, q, flags=re.IGNORECASE):
            rewritten = re.sub(pattern, replacement, q, count=1, flags=re.IGNORECASE)
            rewritten = rewritten.strip()
            if rewritten and rewritten != q:
                if not rewritten.endswith("?"):
                    rewritten = rewritten.rstrip(".") + " ?"
                return rewritten
    return None


def paraphrase_question(q: str, seed: int = 0) -> list[str]:
    """
    Génère jusqu'à 2 variantes de formulation pour une question.

    Variante 1 : réécriture grammaticale via la première règle qui matche
                 (cf. `_QUESTION_REWRITES` au-dessus).
    Variante 2 : ajout d'un préfixe contextuel locataire + suffixe formel,
                 et mise en minuscule de la 1re lettre du corps de la question.

    Args:
        q:    la question originale.
        seed: graine random pour la reproductibilité.

    Returns:
        Liste de 0, 1 ou 2 paraphrases distinctes (jamais la question
        originale elle-même).

    --- Indice léger ---
    L'augmentation de dataset SANS LLM = règles + randomisation déterministe.
    `random.Random(seed)` te donne un RNG isolé. Tu construis `variants = []`,
    tu tentes V1 (réécriture par règle), puis V2 (préfixe + suffixe), et tu
    renvoies au plus 2 résultats DIFFÉRENTS de l'original.

    --- Indice fort ---
    ```python
    rng = random.Random(seed)
    variants = []

    # V1 : réécriture grammaticale
    v1 = _apply_first_matching_rewrite(q)
    if v1:
        variants.append(v1)

    # V2 : préfixe contextuel + ponctuation formelle
    prefix = rng.choice(_LOCATAIRE_PREFIXES)
    body = q[0].lower() + q[1:] if q else q
    body = body.rstrip("?").strip()
    suffix = rng.choice(_FORMEL_SUFFIXES)
    v2 = f"{prefix}{body}{suffix}"
    if v2 != q and v2 not in variants:
        variants.append(v2)

    return variants[:2]
    ```
    """
    raise NotImplementedError(
        "Atelier 04 § 4.3 — paraphrase_question. "
        "Solution : git diff student/04-finetuning atelier/04-finetuning -- scripts/augment_qa_dataset.py"
    )


# ── Règles de reformulation de réponse ────────────────────────────────────────

_FORMAL_OPENERS = [
    "Voici ce que je vous recommande : ",
    "Pour répondre à votre question, ",
    "Je vous explique : ",
    "Bonne question ! Voici ma réponse : ",
]

_DIRECT_OPENERS = [
    "",  # pas de préambule
    "En résumé : ",
    "Voici l'essentiel : ",
]


def reformulate_response(answer: str, style: str = "formel", seed: int = 0) -> str:
    """Reformule une réponse dans un style formel ou direct."""
    rng = random.Random(seed)

    # Supprimer l'éventuel opener existant (heuristique simple)
    body = answer
    for opener_end in ["! ", ": ", ". "]:
        parts = body.split(opener_end, 1)
        first_word = parts[0].split()[0] if parts[0].split() else ""
        if (
            len(parts) == 2
            and len(parts[0]) < 60
            and first_word[0].isupper()
            and "." not in parts[0]
        ):
            body = parts[1]
            break

    if style == "formel":
        opener = rng.choice(_FORMAL_OPENERS)
    else:
        opener = rng.choice(_DIRECT_OPENERS)

    result = (opener + body).strip()
    return result if result != answer else answer


# ── Questions négatives / contre-exemples ────────────────────────────────────

_NEGATIVE_TEMPLATES = {
    "équipements": [
        ("Est-ce que HomeButler peut faire les réparations à ma place ?",
         "Je suis là pour vous guider et vous orienter, mais les interventions techniques doivent être réalisées par un professionnel qualifié. Ce que je peux faire : vous aider à diagnostiquer le problème et trouver le bon artisan près de chez vous !"),
        ("Puis-je ignorer l'entretien annuel obligatoire de ma chaudière ?",
         "Je vous déconseille fortement de l'ignorer ! L'entretien annuel est obligatoire par la loi (décret 2009-649) et votre assurance habitation peut refuser de couvrir un sinistre si l'entretien n'est pas à jour. Je vous aide à trouver un technicien RGE si vous le souhaitez."),
    ],
    "droits": [
        ("Mon propriétaire peut-il entrer dans mon logement sans prévenir ?",
         "Non, absolument pas. La loi du 6 juillet 1989 protège votre droit à la jouissance paisible du logement. Votre propriétaire doit vous prévenir au moins 48h à l'avance, sauf urgence. Si cela se produit, je vous recommande d'envoyer un courrier recommandé en citant l'article 1719 du Code civil."),
        ("Est-ce que je peux sous-louer mon appartement sans l'accord du propriétaire ?",
         "Non, la sous-location sans autorisation écrite du propriétaire est illégale (loi du 6 juillet 1989, art. 8). Cela peut entraîner la résiliation de votre bail. Si vous souhaitez sous-louer, commencez par demander l'accord écrit de votre propriétaire."),
    ],
    "énergie": [
        ("Ma consommation a doublé ce mois-ci, est-ce normal ?",
         "Un doublement de consommation n'est pas normal et mérite investigation. Les causes possibles : appareil défectueux (chauffe-eau, réfrigérateur), fuite de chaleur (vitre cassée, porte mal isolée), ou erreur de compteur. Je vous conseille de vérifier l'index de votre compteur directement et de comparer avec la même période l'an dernier."),
        ("Je peux laisser les appareils en veille sans impact sur ma facture, non ?",
         "Pas tout à fait ! La veille représente en moyenne 10 à 15% de la consommation électrique d'un foyer français, soit environ 100 à 200€ par an. Les plus gourmands : TV, box internet, ordinateur. Je vous recommande d'utiliser des multiprises avec interrupteur pour couper facilement l'alimentation."),
    ],
    "marketplace": [
        ("Puis-je commander auprès de producteurs qui ne sont pas dans votre base ?",
         "Pour l'instant, HomeButler référence uniquement les producteurs locaux vérifiés dans un rayon de 30km autour de votre adresse. Si vous connaissez un producteur local de qualité, vous pouvez me le signaler et j'enverrai une demande de référencement !"),
        ("Est-ce que HomeButler garantit la fraîcheur des produits livrés ?",
         "HomeButler met en relation avec des producteurs locaux partenaires, mais nous ne sommes pas transporteurs. La fraîcheur dépend du producteur et du mode de livraison choisi. Chaque fiche producteur affiche les délais habituels et les conditions de livraison."),
    ],
}


def generate_negative_examples(category: str, seed: int = 0) -> list[dict]:
    """Génère des contre-exemples pour une catégorie donnée."""
    examples = _NEGATIVE_TEMPLATES.get(category, [])
    return [
        {
            "instruction": INSTRUCTION,
            "input": q,
            "output": a,
            "category": category,
            "augmentation": "negative_example",
        }
        for q, a in examples
    ]


# ── Augmentation principale ───────────────────────────────────────────────────

def augment_dataset(
    input_path: Path,
    output_path: Path,
    target_size: int = DEFAULT_TARGET,
    seed: int = 42,
) -> int:
    """
    Lit input_path (JSONL), génère des variantes, écrit output_path.
    Retourne le nombre de paires écrites.
    """
    rng = random.Random(seed)

    with open(input_path, encoding="utf-8") as f:
        originals = [json.loads(line) for line in f if line.strip()]

    print(f"  Paires originales : {len(originals)}")

    augmented: list[dict] = []

    # 1. Inclure toutes les paires originales (avec marqueur)
    for pair in originals:
        pair["augmentation"] = "original"
        augmented.append(pair)

    # 2. Paraphrase de question (2 variantes × 150 = 300 nouvelles paires)
    for i, pair in enumerate(originals):
        question = pair.get("input", "")
        variants = paraphrase_question(question, seed=seed + i)
        for j, v in enumerate(variants):
            augmented.append({
                "instruction": INSTRUCTION,
                "input": v,
                "output": pair["output"],
                "category": pair.get("category", "général"),
                "augmentation": f"paraphrase_q_{j + 1}",
            })

    # 3. Reformulation de réponse (style direct — 1 variante × 150 = 150 nouvelles paires)
    for i, pair in enumerate(originals):
        # alterner formel / direct selon parité pour la diversité
        style = "formel" if i % 2 == 0 else "direct"
        new_answer = reformulate_response(pair["output"], style=style, seed=seed + i)
        if new_answer != pair["output"]:
            augmented.append({
                "instruction": INSTRUCTION,
                "input": pair["input"],
                "output": new_answer,
                "category": pair.get("category", "général"),
                "augmentation": f"reformulate_{style}",
            })

    # 4. Contre-exemples par catégorie
    categories = list(_NEGATIVE_TEMPLATES.keys())
    for cat in categories:
        augmented.extend(generate_negative_examples(cat, seed=seed))

    print(f"  Paires avant déduplication : {len(augmented)}")

    # 5. Déduplication sur (input, output) normalisé
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for pair in augmented:
        key = (pair["input"].strip().lower(), pair["output"][:100].strip().lower())
        if key not in seen:
            seen.add(key)
            deduped.append(pair)

    print(f"  Après déduplication : {len(deduped)}")

    # 6. Mélange reproductible puis troncature à target_size
    rng.shuffle(deduped)
    final = deduped[:target_size]

    # 7. Écriture
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for pair in final:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    return len(final)


# ── Rapport de distribution ───────────────────────────────────────────────────

def print_distribution(output_path: Path) -> None:
    with open(output_path, encoding="utf-8") as f:
        pairs = [json.loads(line) for line in f if line.strip()]

    total = len(pairs)
    print(f"\n  Distribution — {total} paires au total :")

    by_cat: dict[str, int] = {}
    by_aug: dict[str, int] = {}
    for p in pairs:
        cat = p.get("category", "?")
        aug = p.get("augmentation", "?")
        by_cat[cat] = by_cat.get(cat, 0) + 1
        by_aug[aug] = by_aug.get(aug, 0) + 1

    print("  Par catégorie :")
    for cat, n in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"    {cat:<20} {n:>4}  ({100*n/total:.1f}%)")

    print("  Par type d'augmentation :")
    for aug, n in sorted(by_aug.items(), key=lambda x: -x[1]):
        print(f"    {aug:<30} {n:>4}  ({100*n/total:.1f}%)")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Augmente le dataset QA concierge.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--target", type=int, default=DEFAULT_TARGET)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Erreur : fichier source introuvable : {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Augmentation {args.input.name} → {args.output.name} (cible : {args.target} paires)")
    n = augment_dataset(args.input, args.output, target_size=args.target, seed=args.seed)
    print(f"  ✓ {n} paires écrites dans {args.output}")
    print_distribution(args.output)


if __name__ == "__main__":
    main()
