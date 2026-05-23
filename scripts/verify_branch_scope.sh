#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────
# verify_branch_scope.sh
# Vérifie que la branche courante respecte le scope défini pour son atelier
# (anti-débordement : pas de code d'un chapitre suivant).
#
# Usage : bash scripts/verify_branch_scope.sh
# ─────────────────────────────────────────────────────────────────────────

set -u
BRANCH=$(git branch --show-current)
ERRORS=0

red()   { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
blue()  { printf "\033[34m%s\033[0m\n" "$*"; }

blue "═══════════════════════════════════════════════════════"
blue "Vérification scope branche : $BRANCH"
blue "═══════════════════════════════════════════════════════"

fail() { red "  ✗ $1"; ERRORS=$((ERRORS+1)); }
ok()   { green "  ✓ $1"; }

forbid_dir() {
  # Vérifie qu'aucun fichier tracké par git n'existe sous ce chemin.
  # Ignore donc les __pycache__ ou autres artefacts laissés par d'autres branches.
  if git ls-files --error-unmatch "$1" >/dev/null 2>&1 || \
     [ -n "$(git ls-files "$1" 2>/dev/null)" ]; then
    fail "Répertoire interdit (fichiers trackés) : $1"
  else
    ok "absent : $1"
  fi
}

forbid_file() {
  if git ls-files --error-unmatch "$1" >/dev/null 2>&1; then
    fail "Fichier interdit présent : $1"
  else
    ok "absent : $1"
  fi
}

forbid_grep() {
  # $1 = motif regex, $2 = chemin
  TRACKED=$(git ls-files "$2" 2>/dev/null | grep -E '\.py$')
  if [ -z "$TRACKED" ]; then
    ok "$2 vide (aucun .py tracké)"
    return
  fi
  if echo "$TRACKED" | xargs grep -l -E "$1" 2>/dev/null | grep -q .; then
    fail "Motif interdit trouvé '$1' dans $2"
  else
    ok "$2 propre de '$1'"
  fi
}

case "$BRANCH" in
  atelier/01*)
    blue "Atelier 01 — LLM seul (pas de RAG / agent / API / UI)"
    forbid_dir homebutler/rag
    forbid_dir homebutler/agent
    forbid_dir homebutler/services
    forbid_dir api
    forbid_dir ui
    forbid_file notebooks/02_ingestion_vectorisation.ipynb
    forbid_file notebooks/02_rag_simple_faiss.ipynb
    forbid_file notebooks/03_finetuning_lora.ipynb
    ;;

  atelier/02*)
    blue "Atelier 02 — RAG FAISS seul (pas de ChromaDB / agent / API / UI)"
    forbid_dir homebutler/agent
    forbid_dir homebutler/services
    forbid_dir api
    forbid_dir ui
    forbid_file homebutler/rag/vectorstore_chroma.py
    forbid_file notebooks/02_ingestion_vectorisation.ipynb
    forbid_file notebooks/03_finetuning_lora.ipynb
    forbid_grep "chromadb|ChromaDB|EnsembleRetriever|AgentExecutor" homebutler/
    if [ -f requirements_atelier02.txt ] && grep -E "^chromadb" requirements_atelier02.txt >/dev/null; then
      fail "chromadb listé dans requirements_atelier02.txt"
    else
      ok "requirements_atelier02.txt sans chromadb"
    fi
    ;;

  atelier/03*)
    blue "Atelier 03 — Pipeline + Agent (pas d'API complète / Streamlit / dataset FT)"
    forbid_dir ui/pages
    forbid_file api/limiter.py
    forbid_file api/routers/consumption.py
    forbid_file api/routers/products.py
    forbid_file api/routers/orders.py
    forbid_file scripts/generate_qa_dataset.py
    forbid_file scripts/augment_qa_dataset.py
    forbid_file notebooks/03_finetuning_lora.ipynb
    ;;

  atelier/04*)
    blue "Atelier 04 — Fine-tuning (pas d'API complète / Streamlit)"
    forbid_dir ui/pages
    forbid_file api/limiter.py
    forbid_file api/routers/consumption.py
    forbid_file api/routers/products.py
    forbid_file api/routers/orders.py
    ;;

  atelier/05*)
    blue "Atelier 05 — Déploiement (routes comparaison désactivées via feature flag)"
    # Depuis le refactor feature-flag, les routes /evaluate et /compare restent dans le code
    # mais sont protégées par ENABLE_COMPARE_ROUTES. Vérifier que le flag est bien à false par défaut.
    if [ -f api/routers/rag.py ] && grep -E '_ENABLE_COMPARE\s*=.*"false"' api/routers/rag.py >/dev/null; then
      ok "api/routers/rag.py — feature flag ENABLE_COMPARE_ROUTES par défaut à false"
    else
      fail "ENABLE_COMPARE_ROUTES manquant ou mal configuré dans api/routers/rag.py"
    fi
    if [ -f .env ] && grep -E "^ENABLE_COMPARE_ROUTES=true" .env >/dev/null; then
      fail ".env active ENABLE_COMPARE_ROUTES=true — interdit pour l'atelier 05"
    else
      ok ".env n'active pas ENABLE_COMPARE_ROUTES (attendu)"
    fi
    ;;

  atelier/06*|main)
    blue "Atelier 06 / main — version complète, pas de vérification anti-débordement"
    if [ -f .env ] && grep -E "^ENABLE_COMPARE_ROUTES=true" .env >/dev/null; then
      ok ".env active ENABLE_COMPARE_ROUTES=true (requis pour At.06)"
    else
      fail ".env n'active pas ENABLE_COMPARE_ROUTES=true — les routes /evaluate et /compare seront en 404"
    fi
    ;;

  solution/*)
    blue "Branche solution — lecture seule, pas de vérification scope"
    ok "Branche solution : accès réservé post-atelier"
    ;;

  *)
    red "Branche inconnue : $BRANCH (pas de règle de scope)"
    exit 2
    ;;
esac

# ── Vérification transversale : fichiers prompt-guard présents ────────────────
blue "─────────────────────────────────────────────────────────"
blue "Vérification prompt-guard (.claude/CLAUDE.md + .cursorrules par atelier)"

check_atelier_guard() {
  local dir="$1"
  local n="$2"
  if [ -f "${dir}/.claude/CLAUDE.md" ]; then
    ok "At.${n} — .claude/CLAUDE.md présent"
  else
    fail "At.${n} — .claude/CLAUDE.md MANQUANT dans ${dir}/"
  fi
  if [ -f "${dir}/.cursorrules" ]; then
    ok "At.${n} — .cursorrules présent"
  else
    fail "At.${n} — .cursorrules MANQUANT dans ${dir}/"
  fi
  if [ -f "${dir}/.claude/settings.json" ]; then
    ok "At.${n} — .claude/settings.json présent"
  else
    fail "At.${n} — .claude/settings.json MANQUANT dans ${dir}/"
  fi
}

for atelier_dir in ateliers/atelier-0[0-9]-*/; do
  if [ -d "$atelier_dir" ]; then
    n=$(echo "$atelier_dir" | grep -o 'atelier-[0-9][0-9]' | grep -o '[0-9][0-9]')
    check_atelier_guard "$atelier_dir" "$n"
  fi
done

blue "─────────────────────────────────────────────────────────"
if [ "$ERRORS" -eq 0 ]; then
  green "✓ Scope conforme pour $BRANCH"
  exit 0
else
  red "✗ $ERRORS violation(s) de scope détectée(s)"
  exit 1
fi
