#!/usr/bin/env bash
# check_atelier_ready.sh — Vérifie qu'un atelier est prêt à démarrer
# Usage: bash scripts/check_atelier_ready.sh 02
# Exit 0 si tout OK, exit 1 sinon

set -euo pipefail

# ─── Couleurs ────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

OK="✅"
KO="❌"
WARN="⚠️ "

problems=0

check_ok()   { echo -e "${OK}  $1"; }
check_fail() { echo -e "${KO}  $1"; ((problems++)) || true; }
check_warn() { echo -e "${WARN} $1"; }

# ─── 1. Argument ─────────────────────────────────────────────────────────────
if [[ $# -ne 1 ]]; then
  echo "Usage: bash scripts/check_atelier_ready.sh <N>"
  echo "  N = numéro de l'atelier : 01 02 03 04 05 06"
  exit 1
fi

ATELIER="$1"

# Valider le format (01-06)
if ! [[ "$ATELIER" =~ ^0[1-6]$ ]]; then
  echo -e "${KO}  Argument invalide : '$ATELIER'. Attendu : 01 02 03 04 05 06"
  exit 1
fi

echo ""
echo "============================================"
echo "  Check Atelier $ATELIER — $(date '+%Y-%m-%d %H:%M')"
echo "============================================"
echo ""

# ─── 2. venv activé ──────────────────────────────────────────────────────────
echo "── Environnement Python ──"
if python -c "import sys; assert hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)" 2>/dev/null; then
  PYTHON_VERSION=$(python --version 2>&1)
  check_ok "venv activé ($PYTHON_VERSION)"
else
  check_fail "venv non activé — lance : source .venv/bin/activate (ou source .venv_atelier${ATELIER}/bin/activate)"
fi

# ─── 3. Fichier .env ─────────────────────────────────────────────────────────
echo ""
echo "── Variables d'environnement ──"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$REPO_ROOT/.env" ]]; then
  check_ok ".env présent"
  # Charger .env sans exporter (lecture seule)
  set -o allexport
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.env" 2>/dev/null || true
  set +o allexport
else
  check_fail ".env absent — copie .env.example en .env et renseigne les clés"
fi

# ANTHROPIC_API_KEY
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  check_ok "ANTHROPIC_API_KEY définie"
else
  check_fail "ANTHROPIC_API_KEY manquante ou vide dans .env"
fi

# Langfuse (obligatoire At.05, avertissement sinon)
if [[ "$ATELIER" == "05" ]]; then
  if [[ -n "${LANGFUSE_PUBLIC_KEY:-}" ]] && [[ -n "${LANGFUSE_SECRET_KEY:-}" ]]; then
    check_ok "LANGFUSE_PUBLIC_KEY et LANGFUSE_SECRET_KEY définies"
  else
    check_fail "LANGFUSE_PUBLIC_KEY et/ou LANGFUSE_SECRET_KEY manquantes — obligatoires pour At.05. Crée un compte gratuit sur https://cloud.langfuse.com"
  fi
else
  if [[ -n "${LANGFUSE_PUBLIC_KEY:-}" ]] && [[ -n "${LANGFUSE_SECRET_KEY:-}" ]]; then
    check_ok "LANGFUSE_PUBLIC_KEY et LANGFUSE_SECRET_KEY définies (bonus At.05)"
  else
    check_warn "LANGFUSE_PUBLIC_KEY/SECRET_KEY non définies (pas nécessaires pour At.${ATELIER})"
  fi
fi

# ─── 4. PDFs dans data/documents/ ────────────────────────────────────────────
echo ""
echo "── Données ──"
NEEDS_PDFS=false
case "$ATELIER" in
  01|02|03|05|06) NEEDS_PDFS=true ;;
esac

if [[ "$NEEDS_PDFS" == "true" ]]; then
  PDF_DIR="$REPO_ROOT/data/documents"
  if [[ -d "$PDF_DIR" ]]; then
    PDF_COUNT=$(find "$PDF_DIR" -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$PDF_COUNT" -gt 0 ]]; then
      check_ok "PDFs présents dans data/documents/ ($PDF_COUNT fichiers)"
    else
      check_fail "Aucun PDF dans data/documents/ — lance : python scripts/generate_documents.py"
    fi
  else
    check_fail "Dossier data/documents/ absent — lance : python scripts/generate_documents.py"
  fi
fi

# ─── 5. Index FAISS (At.02 et At.03) ─────────────────────────────────────────
if [[ "$ATELIER" == "02" ]] || [[ "$ATELIER" == "03" ]]; then
  FAISS_DIR="$REPO_ROOT/data/faiss_index"
  if [[ -d "$FAISS_DIR" ]] && [[ "$(ls -A "$FAISS_DIR" 2>/dev/null)" ]]; then
    check_ok "Index FAISS présent dans data/faiss_index/"
  else
    check_warn "Index FAISS absent — il sera reconstruit au premier lancement (python -c \"from homebutler.rag.vectorstore_faiss import build_faiss_index; build_faiss_index()\")"
  fi
fi

# ─── 6. Index Chroma (At.03) ──────────────────────────────────────────────────
if [[ "$ATELIER" == "03" ]]; then
  CHROMA_DIR="$REPO_ROOT/data/chroma_db"
  if [[ -d "$CHROMA_DIR" ]] && [[ "$(ls -A "$CHROMA_DIR" 2>/dev/null)" ]]; then
    check_ok "Index Chroma présent dans data/chroma_db/"
  else
    check_fail "Index Chroma absent — lance : python -c \"from homebutler.rag.vectorstore_chroma import build_chroma_index; build_chroma_index()\""
  fi
fi

# ─── 7. Fichiers spécifiques At.04 ────────────────────────────────────────────
if [[ "$ATELIER" == "04" ]]; then
  echo ""
  echo "── Fichiers atelier 04 ──"
  AT04_DIR="$REPO_ROOT/ateliers/atelier-04-finetuning"
  if [[ -f "$AT04_DIR/prepare_dataset.py" ]]; then
    check_ok "prepare_dataset.py présent"
  else
    check_fail "prepare_dataset.py absent dans ateliers/atelier-04-finetuning/"
  fi
  if [[ -f "$AT04_DIR/explore_dataset.py" ]]; then
    check_ok "explore_dataset.py présent"
  else
    check_fail "explore_dataset.py absent dans ateliers/atelier-04-finetuning/"
  fi
fi

# ─── 8. Ports libres : 8000, 8501, 3300 ──────────────────────────────────────
echo ""
echo "── Ports réseau ──"
for PORT in 8000 8501 3300; do
  PIDS=$(lsof -ti :"$PORT" 2>/dev/null || true)
  if [[ -z "$PIDS" ]]; then
    check_ok "Port $PORT libre"
  else
    PROCESS=$(lsof -ti :"$PORT" 2>/dev/null | head -1 | xargs -I{} ps -p {} -o comm= 2>/dev/null || echo "processus inconnu")
    check_fail "Port $PORT occupé par '$PROCESS' (PID: $PIDS) — arrête ce processus ou change le port"
  fi
done

# ─── 9. Dépendances via requirements ─────────────────────────────────────────
echo ""
echo "── Dépendances Python ──"
REQ_FILE="$REPO_ROOT/requirements_atelier${ATELIER}.txt"
if [[ -f "$REQ_FILE" ]]; then
  check_ok "requirements_atelier${ATELIER}.txt présent"
  # Test import des packages principaux selon l'atelier
  IMPORT_OK=true
  case "$ATELIER" in
    01)
      python -c "import anthropic, langchain" 2>/dev/null || IMPORT_OK=false
      ;;
    02)
      python -c "import anthropic, langchain, faiss, fastembed" 2>/dev/null || IMPORT_OK=false
      ;;
    03)
      python -c "import anthropic, langchain, faiss, fastembed, chromadb" 2>/dev/null || IMPORT_OK=false
      ;;
    04)
      python -c "import datasets, transformers" 2>/dev/null || IMPORT_OK=false
      ;;
    05)
      python -c "import fastapi, streamlit, langfuse" 2>/dev/null || IMPORT_OK=false
      ;;
    06)
      python -c "import anthropic, langchain, faiss, fastembed, fastapi" 2>/dev/null || IMPORT_OK=false
      ;;
  esac

  if [[ "$IMPORT_OK" == "true" ]]; then
    check_ok "Imports principaux atelier ${ATELIER} OK"
  else
    check_fail "Certains packages manquent — lance : pip install -r requirements_atelier${ATELIER}.txt"
  fi

  # pip check pour détecter les conflits
  if pip check &>/dev/null; then
    check_ok "Aucun conflit de dépendances (pip check)"
  else
    check_warn "Conflits de dépendances détectés — lance 'pip check' pour détails"
  fi
else
  check_warn "requirements_atelier${ATELIER}.txt absent — installe les dépendances manuellement"
fi

# ─── 10. Résumé final ─────────────────────────────────────────────────────────
echo ""
echo "============================================"
if [[ "$problems" -eq 0 ]]; then
  echo -e "${GREEN}  Atelier ${ATELIER} : PRÊT${NC}"
  echo "============================================"
  echo ""
  exit 0
else
  echo -e "${RED}  Atelier ${ATELIER} : $problems problème(s) à corriger${NC}"
  echo "============================================"
  echo ""
  echo "  Corrige les ❌ ci-dessus, puis relance :"
  echo "  bash scripts/check_atelier_ready.sh ${ATELIER}"
  echo ""
  exit 1
fi
