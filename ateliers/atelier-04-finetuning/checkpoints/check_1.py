"""
Checkpoint 1 — Atelier 04 Fine-tuning LoRA/QLoRA
3 termes tirés aléatoirement du lexique obligatoire.
Le stagiaire doit expliquer chaque terme avec ses propres mots.
LLM-judge ou auto-évaluation.
"""

import random

LEXIQUE = [
    {
        "terme": "GPU (Graphics Processing Unit)",
        "definition_attendue": "carte dédiée aux calculs parallèles, indispensable pour le training de gros modèles",
        "analogie_attendue": "cuisine de restaurant avec 100 cuisiniers en parallèle vs 1 cuisinier (CPU)",
        "question_verification": "Pourquoi ne peut-on pas entraîner Mistral-7B sur un Mac sans GPU ?",
        "reponse_cle": "Le Mac n'a pas de GPU Nvidia avec assez de VRAM. Mistral-7B en QLoRA nécessite ~12 GB de VRAM.",
    },
    {
        "terme": "Learning rate (lr)",
        "definition_attendue": "vitesse d'apprentissage, à chaque exemple le modèle ajuste ses poids de ce montant",
        "analogie_attendue": "vitesse d'un cuisinier qui ajuste sa recette : trop vite il rate, trop lentement il ne progresse pas",
        "question_verification": "Que se passe-t-il si lr=1e-2 sur Mistral-7B ?",
        "reponse_cle": "Loss explose (NaN) au premier epoch — le modèle n'apprend rien. LoRA : sweet spot 1e-4 à 5e-4.",
    },
    {
        "terme": "Epoch",
        "definition_attendue": "une passe complète sur tout le dataset d'entraînement",
        "analogie_attendue": "relire 5 fois ses fiches de révision avant un examen",
        "question_verification": "Pourquoi 10 epochs peuvent-ils poser problème ?",
        "reponse_cle": "Surapprentissage (overfitting) : val_loss remonte alors que train_loss continue à baisser.",
    },
    {
        "terme": "Perplexité",
        "definition_attendue": "mesure de surprise du modèle face à la bonne réponse — plus c'est bas, mieux c'est",
        "analogie_attendue": "note d'incompréhension — si la bonne réponse surprend le modèle, il l'a mal apprise",
        "question_verification": "Perplexité val de 12 vs perplexité train de 8 : que signifie cet écart ?",
        "reponse_cle": "Signal d'overfitting léger : le modèle performe mieux sur les données vues (train) que sur les nouvelles (val).",
    },
    {
        "terme": "Dataset déséquilibré",
        "definition_attendue": "certaines catégories sur-représentées — le modèle apprend bien les catégories dominantes et ignore les minoritaires",
        "analogie_attendue": "prof qui ne donne que des exos de maths → élève nul en français à l'examen",
        "question_verification": "Dataset HomeButler : 66 'autres' vs 6 'marketplace'. Quel est le risque ?",
        "reponse_cle": "Le modèle fine-tuné sera incapable de répondre aux questions 'marketplace' — il répond toujours 'autres'.",
    },
    {
        "terme": "Catastrophic forgetting",
        "definition_attendue": "le modèle, en apprenant le domaine cible, oublie ses connaissances générales",
        "analogie_attendue": "cuisinier qui se spécialise en pâtisserie et oublie comment faire un steak",
        "question_verification": "Comment éviter le catastrophic forgetting dans notre cas ?",
        "reponse_cle": "Mélanger 20-30% de données générales dans le dataset (ou utiliser LoRA qui gèle la plupart des poids).",
    },
    {
        "terme": "Quantization 4-bit (QLoRA)",
        "definition_attendue": "stocker les poids sur 4 bits au lieu de 16 → 4× moins de mémoire, légère perte de précision",
        "analogie_attendue": "compresser une photo HD en JPG basse qualité : 4× plus léger, presque pas visible",
        "question_verification": "Pourquoi QLoRA (4-bit) au lieu de LoRA (16-bit) sur Colab T4 gratuit ?",
        "reponse_cle": "T4 = 15 GB VRAM. Mistral-7B en 16-bit = ~14 GB → trop juste. En 4-bit = ~4 GB → confortable.",
    },
]

SCORE_MIN = 2


def run_quiz() -> None:
    print("\n" + "=" * 65)
    print("CHECKPOINT 1 — Atelier 04 : Lexique Fine-tuning")
    print("=" * 65)
    print("3 termes au hasard à expliquer avec TES PROPRES MOTS.")
    print("Score minimum pour valider : 2/3\n")
    print("Mode auto-évaluation : lis ta réponse, puis compare avec la définition attendue.")
    print("Sois honnête — c'est ton apprentissage.\n")

    termes_choisis = random.sample(LEXIQUE, 3)
    score = 0

    for i, item in enumerate(termes_choisis, 1):
        print(f"\n{'─' * 55}")
        print(f"[{i}/3] TERME : {item['terme']}")
        print("\nExplique ce terme en 2-3 phrases avec tes propres mots")
        print("(sans relire le Carnet de bord) :")
        _ = input("> Ta réponse : ")

        print(f"\n📖 Définition attendue : {item['definition_attendue']}")
        print(f"🎯 Analogie : {item['analogie_attendue']}")
        print(f"\n❓ Question de vérification : {item['question_verification']}")
        _ = input("> Ta réponse : ")
        print(f"✅ Réponse clé : {item['reponse_cle']}")

        verdict = input("\nTu te considères : (A) À l'aise / (B) À renforcer ? ").strip().upper()
        if verdict == "A":
            score += 1
            print("   → Comptabilisé comme validé ✓")
        else:
            print("   → À retravailler — relis la section Carnet de bord pour ce terme.")

    print("\n" + "=" * 65)
    print(f"SCORE DÉCLARÉ : {score}/3")
    print("=" * 65)

    if score >= SCORE_MIN:
        print(f"\nRÉSULTAT : VALIDE ({score}/3 ≥ {SCORE_MIN}/3)")
        print("→ Continue vers l'Étape 2 (Colab + Training).")
    else:
        print(f"\nRÉSULTAT : À RENFORCER ({score}/3 < {SCORE_MIN}/3)")
        print("→ Relis le Carnet de bord pour les termes manqués.")
        print("→ Demande à un pair d'expliquer sans le guide.")
        print("→ Relance ce checkpoint quand tu te sens prêt.")


if __name__ == "__main__":
    run_quiz()
