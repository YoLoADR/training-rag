"""
Optimisation du pipeline RAG — reranking, multi-query, HyDE.

Atelier 08. On part du retrieval d'AT02/AT03 (FAISS / EnsembleRetriever) et on
ajoute trois techniques d'amélioration de la PRÉCISION de récupération, toutes
100% locales et sans GPU :

  1. Reranking cross-encoder (flashrank)  → entonnoir base_k ≫ top_n
  2. Multi-query (reformulation LLM)        → couvre les variantes de vocabulaire
  3. HyDE (Hypothetical Document Embeddings) → embed une réponse hypothétique

Le reranker `flashrank` télécharge un petit modèle ONNX (ms-marco-MiniLM-L-12-v2,
~34 Mo) au premier appel, puis tourne sur CPU. Cohérent avec le choix `fastembed`
d'AT02 (zéro GPU, zéro API tierce).
"""

import os

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.document_compressors import FlashrankRerank
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from homebutler.llm.provider import get_llm
from homebutler.rag.retriever import get_faiss_retriever, get_ensemble_retriever

# ─── Paramètres (surchargeables par variables d'env, défauts raisonnables) ───
RERANK_MODEL = os.getenv("RERANK_MODEL", "ms-marco-MiniLM-L-12-v2")
RERANK_BASE_K = int(os.getenv("RERANK_BASE_K", "20"))   # taille du pool de candidats
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", "5"))      # documents finaux après reclassement


# ─── Prompt multi-query : c'est CE prompt qui crée la diversité ───────────────
# La diversité ne vient PAS de la température (un seul appel LLM génère toutes
# les variantes) mais de la CONSIGNE : on demande explicitement N reformulations.
MULTIQUERY_PROMPT = ChatPromptTemplate.from_template(
    "Tu es un assistant qui aide à améliorer la recherche documentaire.\n"
    "Génère 3 reformulations DIFFÉRENTES de la question ci-dessous, afin de\n"
    "couvrir plusieurs façons de la poser (synonymes, angle technique, angle usager).\n"
    "Une reformulation par ligne, sans numérotation.\n\n"
    "Question : {question}"
)


def get_reranked_retriever(base_k: int = RERANK_BASE_K,
                           top_n: int = RERANK_TOP_N,
                           use_ensemble: bool = False):
    """
    Retriever à 2 étages : récupération LARGE puis reclassement cross-encoder.

    Étage 1 (rappel) : on récupère `base_k` candidats (FAISS, ou EnsembleRetriever
                       FAISS+Chroma si use_ensemble).
    Étage 2 (précision) : le cross-encoder `flashrank` re-score chaque (question,
                       chunk) et ne garde que les `top_n` meilleurs.

    Concept clé — l'ENTONNOIR : `base_k` doit être nettement plus grand que `top_n`.
    Si base_k == top_n, le reranker n'a plus rien à filtrer (il ne fait que
    réordonner le même ensemble) et le bénéfice de précision disparaît.
    """
    if use_ensemble:
        base_retriever = get_ensemble_retriever(faiss_k=base_k, chroma_k=base_k)
    else:
        base_retriever = get_faiss_retriever(k=base_k, fetch_k=max(base_k, 20))

    compressor = FlashrankRerank(model=RERANK_MODEL, top_n=top_n)
    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever,
    )


def get_multiquery_retriever(k: int = 4, use_ensemble: bool = False):
    """
    MultiQueryRetriever : le LLM reformule la question en plusieurs variantes,
    on récupère pour chacune, puis on prend l'union des documents.

    Utile quand le vocabulaire de l'utilisateur diverge de celui des documents
    (ex. "ma clim" vs "VMC double flux" dans les notices).
    """
    base_retriever = (get_ensemble_retriever(faiss_k=k, chroma_k=k)
                      if use_ensemble else get_faiss_retriever(k=k))
    return MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=get_llm(temperature=0),
        prompt=MULTIQUERY_PROMPT,
    )


def get_hyde_chain():
    """
    HyDE (Hypothetical Document Embeddings) — chaîne LCEL.

    Idée : au lieu d'embedder la question (souvent courte), on demande au LLM de
    GÉNÉRER une réponse hypothétique, puis on embedde CE paragraphe pour la
    recherche vectorielle. Le paragraphe hypothétique ressemble davantage aux
    chunks cibles que la question brute → meilleur rappel sur questions vagues.

    Retourne une chaîne qui transforme {question} -> paragraphe hypothétique.
    À brancher ensuite sur `vectorstore.similarity_search(paragraphe)`.
    """
    hyde_prompt = ChatPromptTemplate.from_template(
        "Rédige un court paragraphe (3-4 phrases) qui répondrait à la question\n"
        "suivante comme s'il provenait d'une notice technique de logement.\n"
        "N'invente pas de marque précise ; reste générique mais plausible.\n\n"
        "Question : {question}"
    )
    return hyde_prompt | get_llm(temperature=0) | StrOutputParser()
