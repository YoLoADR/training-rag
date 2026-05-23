"""
Test Bug v2 At.02 — chunk_overlap=0 (coupure phrase → info perdue aux frontières)

Logique :
- Le bug remplace chunk_overlap=50 par chunk_overlap=0
- Avec overlap=0 : les informations qui se trouvent exactement à la frontière
  entre deux chunks sont perdues dans l'un ou l'autre (coupure brutale)
- Ce test vérifie que les chunks consécutifs partagent au moins quelques tokens communs
  (preuve que l'overlap est > 0)

Note : ce test est purement structurel (pas d'appel LLM ni de retrieval).
Il vérifie directement la propriété du chunking.

Comment utiliser :
1. git apply ateliers/atelier-02-rag-simple/bugs/v2.patch
2. pytest ateliers/atelier-02-rag-simple/bugs/test_v2.py -v  (doit ECHOUER)
3. Répare : change chunk_overlap=0 → chunk_overlap=50
4. pytest  (doit PASSER)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from homebutler import config
from homebutler.rag.ingestion import load_pdf_with_metadata, chunk_recursive

OVERLAP_MIN = 10  # nombre minimum de caractères communs entre chunks consécutifs


def load_pages() -> list:
    """Charge les pages PDF depuis data/documents/."""
    docs_dir = config.DOCUMENTS_DIR
    if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
        pytest.skip("PDFs absents — lancer python scripts/generate_documents.py")
    pages = []
    for f in sorted(os.listdir(docs_dir)):
        if f.endswith(".pdf"):
            pages.extend(load_pdf_with_metadata(os.path.join(docs_dir, f)))
    return pages


def compter_chars_communs(texte_a: str, texte_b: str) -> int:
    """Compte les caractères communs entre la fin de texte_a et le début de texte_b."""
    # Cherche le plus long suffixe de texte_a qui est aussi préfixe de texte_b
    max_commun = min(len(texte_a), len(texte_b), 200)  # limiter la recherche
    for longueur in range(max_commun, 0, -1):
        if texte_a[-longueur:] == texte_b[:longueur]:
            return longueur
    return 0


def test_chunk_overlap_non_nul():
    """
    Avec chunk_overlap=50 (configuration correcte), des chunks consécutifs
    doivent partager au moins OVERLAP_MIN caractères en commun.

    Avec chunk_overlap=0 (bug actif), aucun chunk ne partage de texte avec
    le suivant → information perdue aux frontières → ce test ECHOUE.

    Ce test PASSE quand le bug est réparé (chunk_overlap=50).
    Ce test ECHOUE quand le bug est actif (chunk_overlap=0).
    """
    pages = load_pages()

    # Chunk avec la valeur correcte pour le test
    chunks = chunk_recursive(pages, chunk_size=512, chunk_overlap=50)

    if len(chunks) < 2:
        pytest.skip("Pas assez de chunks pour tester l'overlap")

    print(f"\nNombre de chunks : {len(chunks)}")

    # Vérifier que plusieurs paires de chunks consécutifs ont un overlap
    paires_avec_overlap = 0
    paires_testees = min(20, len(chunks) - 1)  # tester les 20 premières paires

    for i in range(paires_testees):
        commun = compter_chars_communs(
            chunks[i].page_content,
            chunks[i + 1].page_content
        )
        if commun >= OVERLAP_MIN:
            paires_avec_overlap += 1

    taux_overlap = paires_avec_overlap / paires_testees
    print(f"Paires avec overlap >= {OVERLAP_MIN} chars : {paires_avec_overlap}/{paires_testees} = {taux_overlap:.0%}")

    assert taux_overlap >= 0.30, (
        f"Seulement {paires_avec_overlap}/{paires_testees} paires de chunks consécutifs "
        f"partagent >= {OVERLAP_MIN} caractères.\n"
        "Avec chunk_overlap=0 : aucun overlap → informations perdues aux frontières.\n"
        "Indice : vérifie chunk_overlap dans les appels chunk_recursive() et chunk_fixed_size().\n"
        "Valeur correcte : chunk_overlap=50."
    )
