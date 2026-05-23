"""
Checkpoint final — Atelier 04 Fine-tuning LoRA/QLoRA
5 questions sur l'ensemble de l'atelier.
Score ≥ 4/5 → Bonus | Score < 3/5 → Sprint.
"""

QUESTIONS = [
    {
        "question": "Pourquoi utilise-t-on LoRA au lieu de fine-tuner tous les poids du modèle ?",
        "options": {
            "A": "LoRA est plus précis car il utilise des matrices entières au lieu de flottants",
            "B": "LoRA gèle la plupart des poids et n'entraîne que de petites matrices d'adaptation → 100× moins de paramètres, GPU accessible",
            "C": "LoRA est obligatoire sur Colab — Hugging Face a supprimé le full fine-tuning",
            "D": "LoRA est plus rapide uniquement parce qu'il utilise un batch_size plus grand",
        },
        "correct": "B",
        "explication": (
            "LoRA (Low-Rank Adaptation) : décompose les mises à jour de poids en 2 petites matrices (rang r=8). "
            "Résultat : 0.1-1% des paramètres originaux à entraîner → possible sur GPU de 15 GB. "
            "QLoRA ajoute la quantization 4-bit pour réduire encore la VRAM."
        ),
    },
    {
        "question": "Tu observes : train_loss = 0.8 après 5 epochs, val_loss = 2.1. Que se passe-t-il ?",
        "options": {
            "A": "Sous-apprentissage : le modèle n'a pas assez vu les données",
            "B": "Surapprentissage (overfitting) : le modèle a mémorisé le train set sans généraliser",
            "C": "Situation normale — val_loss est toujours > train_loss en fine-tuning",
            "D": "Le learning rate est trop bas — il faut augmenter à 1e-2",
        },
        "correct": "B",
        "explication": (
            "Overfitting caractérisé : train_loss baisse mais val_loss remonte (ou reste très > train_loss). "
            "Causes possibles : dataset trop petit, trop d'epochs, lr trop élevé. "
            "Fix : early stopping, réduire epochs, ajouter des données, mixte général/spécialisé."
        ),
    },
    {
        "question": "Tu veux que ton modèle fine-tuné parle 'Merenza' (chaleureux, français, format structuré). Pourquoi le RAG ne suffit pas pour ça ?",
        "options": {
            "A": "Le RAG peut changer le style du LLM via les chunks récupérés — il suffit d'indexer des exemples de style",
            "B": "Le RAG change les connaissances factuelles mais pas le style de génération du LLM — le fine-tuning est nécessaire pour le ton",
            "C": "Le RAG et le fine-tuning font la même chose, c'est une question de préférence",
            "D": "Le RAG est plus coûteux que le fine-tuning pour ce cas d'usage",
        },
        "correct": "B",
        "explication": (
            "RAG = ajouter des connaissances contextuelles → réponses factuelles sur les docs indexés. "
            "Fine-tuning = modifier le comportement intrinsèque du modèle → style, ton, format de sortie. "
            "Pour 'parler Merenza', le fine-tuning est la seule solution efficace."
        ),
    },
    {
        "question": "Ton dataset HomeButler a 66 exemples 'autres' et 6 exemples 'marketplace'. Quelle est la meilleure stratégie ?",
        "options": {
            "A": "Supprimer les 60 exemples 'autres' en surplus pour équilibrer à 6/6",
            "B": "Sur-échantillonner la catégorie 'marketplace' (duplication ou augmentation) pour atteindre ~60 exemples",
            "C": "Ne rien changer — les modèles modernes gèrent automatiquement le déséquilibre",
            "D": "Ajouter un poids 10× aux exemples 'marketplace' dans la loss function uniquement",
        },
        "correct": "B",
        "explication": (
            "Sur-échantillonnage de la minorité : dupliquer ou générer des variantes des 6 exemples 'marketplace' "
            "pour atteindre ~60. Avantage : on ne perd pas d'exemples 'autres'. "
            "Possible aussi via class weights, mais la duplication est plus simple et visible."
        ),
    },
    {
        "question": "Qu'est-ce que le 'catastrophic forgetting' et comment LoRA le réduit-il ?",
        "options": {
            "A": "Le modèle oublie les données d'entraînement précédentes — LoRA les sauvegarde sur disque",
            "B": "Le modèle perd ses capacités générales en se spécialisant — LoRA gèle la plupart des poids originaux et n'entraîne que les adaptateurs",
            "C": "LoRA n'empêche pas le catastrophic forgetting — seul le full fine-tuning le prévient",
            "D": "Le catastrophic forgetting ne s'applique pas aux modèles > 7B paramètres",
        },
        "correct": "B",
        "explication": (
            "Catastrophic forgetting : en apprenant 'Merenza', le modèle risque d'oublier l'anglais, le code, etc. "
            "LoRA atténue ce problème car les poids originaux sont gelés — seules les petites matrices d'adaptation sont modifiées. "
            "Bonne pratique complémentaire : inclure 20-30% d'exemples généraux dans le dataset."
        ),
    },
]

SEUILS = {"bonus": 4, "sprint": 3}


def run_quiz() -> None:
    print("\n" + "=" * 65)
    print("CHECKPOINT FINAL — Atelier 04 : Fine-tuning LoRA/QLoRA")
    print("=" * 65)
    print("5 questions — Score ≥ 4/5 → Bonus | Score < 3/5 → Sprint\n")

    score = 0
    details = []

    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n[{i}/5] {q['question']}")
        for lettre, texte in q["options"].items():
            print(f"   {lettre}) {texte}")

        reponse = input("\nTa réponse (A/B/C/D) : ").strip().upper()

        if reponse == q["correct"]:
            print("   ✓ CORRECT")
            score += 1
            details.append((i, True, q["explication"]))
        else:
            print(f"   ✗ Incorrect. Bonne réponse : {q['correct']}")
            details.append((i, False, q["explication"]))

    print("\n" + "=" * 65)
    print(f"SCORE FINAL : {score}/5")
    print("=" * 65)

    print("\nExplications :")
    for num, correct, explication in details:
        statut = "✓" if correct else "✗"
        print(f"\n[{num}] {statut} — {explication}")

    print("\n" + "─" * 65)
    if score >= SEUILS["bonus"]:
        print(f"RÉSULTAT : BONUS ({score}/5 ≥ {SEUILS['bonus']}/5)")
        print("→ Pars en Bonus : générer 50 paires supplémentaires 'marketplace',")
        print("  lancer l'entraînement Colab et observer la perplexité.")
    elif score < SEUILS["sprint"]:
        print(f"RÉSULTAT : SPRINT ({score}/5 < {SEUILS['sprint']}/5)")
        print("→ Sprint : relis les sections LoRA/overfitting/RAG vs FT,")
        print("  puis réponds aux 5 questions ouvertes du Sprint.")
    else:
        print(f"RÉSULTAT : CORRECT ({score}/5)")
        print("→ Tu peux choisir Sprint (consolider) ou Bonus (approfondir).")


if __name__ == "__main__":
    run_quiz()
