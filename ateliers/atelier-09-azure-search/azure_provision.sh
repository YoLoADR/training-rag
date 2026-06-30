#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# azure_provision.sh — CONTROL PLANE (CLI `az search`)
# Provisionne un service Azure AI Search et écrit l'endpoint + la clé dans .env.
#
# C'est la SEULE partie de l'atelier qui passe par `az` : créer le SERVICE.
# Tout le reste (index, vecteurs, ingestion, requêtes) = SDK Python (data plane).
#
# Usage (formateur, idéalement la veille) :
#   az login                       # device code (interactif)
#   bash ateliers/atelier-09-azure-search/azure_provision.sh
#
# En classe : 1 service Basic PARTAGÉ par le formateur, puis chaque élève crée
# SON index (index_name = trigramme) → pas de limite "1 service Free / souscription".
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

RG="${AZ_RG:-rg-atelier-rag}"
LOC="${AZ_LOCATION:-francecentral}"
SVC="${AZ_SEARCH_SERVICE:-svc-atelier-rag-$RANDOM}"
SKU="${AZ_SEARCH_SKU:-basic}"   # 'free' = 1/souscription, 50 Mo ; 'basic' recommandé en classe

echo "▸ Vérification de la connexion Azure (az account show)…"
az account show >/dev/null 2>&1 || { echo "❌ Lance d'abord : az login"; exit 1; }

echo "▸ [control plane] Groupe de ressources : $RG ($LOC)"
az group create --name "$RG" --location "$LOC" --output none

echo "▸ [control plane] Service de recherche : $SVC (sku=$SKU)"
az search service create \
  --name "$SVC" --resource-group "$RG" \
  --sku "$SKU" --partition-count 1 --replica-count 1 \
  --output none

echo "▸ [control plane] Récupération de l'endpoint et de la clé admin…"
ENDPOINT="https://${SVC}.search.windows.net"
KEY="$(az search admin-key show --resource-group "$RG" --service-name "$SVC" --query primaryKey -o tsv)"

# ── Écriture dans .env (data plane : utilisé par le SDK Python) ──────────────
ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/.env"
touch "$ENV_FILE"
# remplace ou ajoute les variables
for kv in "AZURE_SEARCH_ENDPOINT=$ENDPOINT" "AZURE_SEARCH_KEY=$KEY"; do
  k="${kv%%=*}"
  if grep -q "^${k}=" "$ENV_FILE"; then
    sed -i.bak "s|^${k}=.*|${kv}|" "$ENV_FILE" && rm -f "${ENV_FILE}.bak"
  else
    echo "$kv" >> "$ENV_FILE"
  fi
done

echo "✅ Service prêt."
echo "   AZURE_SEARCH_ENDPOINT=$ENDPOINT"
echo "   AZURE_SEARCH_KEY=*** (écrite dans .env)"
echo "   AZURE_SEARCH_INDEX=${AZURE_SEARCH_INDEX:-homebutler-index} (mets ton trigramme en classe)"
echo
echo "▸ Étape suivante (DATA PLANE, SDK Python) :"
echo "   python ateliers/atelier-09-azure-search/solution.py"
echo
echo "⚠️  En fin de séance, libère les ressources :"
echo "   bash ateliers/atelier-09-azure-search/azure_teardown.sh"
