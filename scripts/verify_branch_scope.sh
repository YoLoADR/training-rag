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
    blue "Atelier 05 — Déploiement (pas d'endpoints /rag/evaluate ni /chat/compare)"
    if [ -f api/routers/rag.py ] && grep -E '@router\.post\("/(evaluate|compare-strategies)' api/routers/rag.py >/dev/null; then
      fail "endpoints d'évaluation actifs dans api/routers/rag.py"
    else
      ok "api/routers/rag.py limité à /retrieve"
    fi
    if [ -f api/routers/chat.py ] && grep -E '@router\.post\("/compare' api/routers/chat.py >/dev/null; then
      fail "endpoint /chat/compare actif (réservé atelier 06)"
    else
      ok "api/routers/chat.py sans /compare"
    fi
    ;;

  atelier/06*|main)
    blue "Atelier 06 / main — version complète, pas de vérification anti-débordement"
    ;;

  *)
    red "Branche inconnue : $BRANCH (pas de règle de scope)"
    exit 2
    ;;
esac

blue "─────────────────────────────────────────────────────────"
if [ "$ERRORS" -eq 0 ]; then
  green "✓ Scope conforme pour $BRANCH"
  exit 0
else
  red "✗ $ERRORS violation(s) de scope détectée(s)"
  exit 1
fi
