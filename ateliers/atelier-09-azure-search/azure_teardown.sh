#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# azure_teardown.sh — GARDE-FOU COÛT (control plane)
# Supprime le groupe de ressources → le service ET tout son contenu.
#
# IMPORTANT : sur un tier Dedicated (Free/Basic/S1…), Azure facture à l'HEURE
# dès la création (pas à l'usage). On supprime donc en fin de séance.
#
# Usage : bash ateliers/atelier-09-azure-search/azure_teardown.sh
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

RG="${AZ_RG:-rg-atelier-rag}"

az account show >/dev/null 2>&1 || { echo "❌ Lance d'abord : az login"; exit 1; }

echo "▸ Suppression du groupe de ressources : $RG (service + index inclus)"
az group delete --name "$RG" --yes --no-wait
echo "✅ Suppression lancée (asynchrone). Vérifie : az group list -o table"
