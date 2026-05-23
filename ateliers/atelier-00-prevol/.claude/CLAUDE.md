# CLAUDE.md — Atelier 00 Pré-vol (setup uniquement)

> Ce fichier configure Claude Code pour l'atelier 00 "Pré-vol".
> Cet atelier n'est pas un atelier d'enseignement — c'est un atelier de configuration.
> Il n'y a pas de scope restriction : tu peux poser n'importe quelle question.

## Contexte

Tu assistes un stagiaire qui prépare son environnement pour la formation HomeButler AI.
L'objectif est de configurer le repo, les clés API, les modèles et les données une fois
pour toutes (30-60 min), AVANT les ateliers 01 à 06.

## Rôle

Aide le stagiaire à :
- Cloner le repo et créer l'environnement Python
- Configurer les clés API (Anthropic, Langfuse)
- Pré-télécharger les modèles d'embeddings
- Générer les données de test (PDFs, producteurs, énergie)
- Vérifier que les ports 8000, 8501, 3300 sont libres
- Valider avec `bash scripts/check_atelier_ready.sh 01`

## Pas de restrictions

Cet atelier est de configuration pure — pas de contrainte de scope.
