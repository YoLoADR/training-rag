"""
Templates de prompts LangChain — Atelier 01.

Tous les prompts utilisateurs et système du projet sont centralisés ici. Les
4 templates ci-dessous sont importés par le reste du code (RAG, agent, API).
Tu dois reconstruire leur contenu — les VARIABLES sont définies à vide pour
ne PAS casser les imports, mais elles produiront des réponses absurdes
tant que tu n'auras pas écrit le bon prompt.

═══════════════════════════════════════════════════════════════════════════
🎓 Atelier 01 — Tu dois écrire les 4 templates de prompts ci-dessous.
   Solution finale (en dernier recours) :
   git diff student/01-llm-baseline atelier/01-llm-baseline -- homebutler/llm/prompts.py
═══════════════════════════════════════════════════════════════════════════
"""

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder

# ── Prompt système conciergerie (À ÉCRIRE) ───────────────────────────────────
# CONCIERGE_SYSTEM_PROMPT = le "rôle" donné au LLM. C'est ce qui définit son TON,
# son DOMAINE, et ses LIMITES. Voir analogie "fiche de poste" du carnet de bord.
#
# --- Indice léger ---
# Doit décrire : (a) qui est HomeButler (conciergerie domestique chaleureuse),
# (b) ses domaines (documents logement, énergie, producteurs locaux, conseils
# pratiques), (c) son ton (chaleureux, vocabulaire accessible, actions concrètes,
# cite les sources), (d) sa limite : "Si tu ne sais pas, dis-le plutôt qu'inventer".
#
# --- Indice fort ---
# Triple-quoted string de 8-12 lignes, en français, qui commence par
# "Tu es HomeButler, la conciergerie domestique intelligente et bienveillante."
# et qui détaille les 4 domaines, le ton, et la règle anti-hallucination.
CONCIERGE_SYSTEM_PROMPT = (
    "# TODO (Atelier 01) — Écris ici le system prompt de HomeButler. "
    "Voir docstring ci-dessus. "
    "Solution : git diff student/01-llm-baseline atelier/01-llm-baseline -- homebutler/llm/prompts.py"
)

# ── 1) Q/A avec contexte documentaire RAG (À ÉCRIRE) ────────────────────────
# RAG_QA_TEMPLATE est utilisé par /chat?mode=rag_only. Il reçoit deux variables :
# `{context}` (chunks récupérés par FAISS) et `{question}` (la question utilisateur).
#
# --- Indice léger ---
# ChatPromptTemplate.from_messages([...]) avec 2 rôles : "system" (le system prompt
# ci-dessus) et "human" (un texte qui contient les chunks puis la question, et qui
# demande au LLM de citer la source entre crochets [nom_du_document]).
#
# --- Indice fort ---
# ```python
# RAG_QA_TEMPLATE = ChatPromptTemplate.from_messages([
#     ("system", CONCIERGE_SYSTEM_PROMPT),
#     ("human",
#      "Voici des extraits de documents de votre logement pertinents pour votre question :\n\n"
#      "{context}\n\n---\nQuestion : {question}\n\n"
#      "Réponds en te basant sur les documents ci-dessus. "
#      "Cite la source entre crochets [nom_du_document]."),
# ])
# ```
RAG_QA_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "TODO Atelier 01 — réécris ce system prompt"),
    ("human", "TODO — utilise {context} et {question} — voir docstring ci-dessus"),
])

# ── 2) Analyse énergie (À ÉCRIRE) ────────────────────────────────────────────
# ENERGY_ANALYSIS_TEMPLATE est utilisé pour l'outil "analyse de consommation".
# Variables : `{monthly_summary}`, `{anomalies}`, `{question}`.
#
# --- Indice léger ---
# ChatPromptTemplate à 2 messages (system + human). Le human contient les
# 3 variables et demande "une analyse personnalisée avec des conseils concrets
# pour optimiser la consommation".
#
# --- Indice fort ---
# ```python
# ENERGY_ANALYSIS_TEMPLATE = ChatPromptTemplate.from_messages([
#     ("system", CONCIERGE_SYSTEM_PROMPT),
#     ("human",
#      "Voici les données de consommation électrique de votre logement :\n\n"
#      "Résumé mensuel (derniers mois) :\n{monthly_summary}\n\n"
#      "Anomalies détectées :\n{anomalies}\n\n"
#      "Question : {question}\n\n"
#      "Donne une analyse personnalisée avec des conseils concrets pour optimiser la consommation."),
# ])
# ```
ENERGY_ANALYSIS_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "TODO Atelier 01 — réécris ce system prompt"),
    ("human", "TODO — utilise {monthly_summary}, {anomalies}, {question}"),
])

# ── 3) Template ReAct fallback (À ÉCRIRE) ───────────────────────────────────
# REACT_SYSTEM_TEMPLATE est utilisé par l'agent ReAct quand le hub LangChain
# (`hwchase17/react`) est indisponible. Variables imposées par LangChain :
# `{tools}`, `{tool_names}`, `{input}`, `{agent_scratchpad}`.
#
# --- Indice léger ---
# Texte brut (string Python) qui :
#   1. Présente HomeButler et liste les outils via {tools},
#   2. Force le format STRICT : Question / Réflexion / Action / Entrée de l'action
#      / Observation (boucle) / Réflexion / Réponse finale,
#   3. Termine par "Question : {input}\nRéflexion : {agent_scratchpad}".
#
# --- Indice fort ---
# String triple-quotée de ~15-20 lignes, voir exemple dans la doc LangChain
# "ReAct prompting" ou dans la version corrigée via git diff. Doit obligatoirement
# contenir les 4 placeholders `{tools}`, `{tool_names}`, `{input}`, `{agent_scratchpad}`.
REACT_SYSTEM_TEMPLATE = (
    "TODO Atelier 01 — écris ici le template ReAct. "
    "Variables OBLIGATOIRES : {tools} {tool_names} {input} {agent_scratchpad}. "
    "Solution : git diff student/01-llm-baseline atelier/01-llm-baseline -- homebutler/llm/prompts.py"
)

# ── 4) LLM seul, sans contexte documentaire (À ÉCRIRE) ──────────────────────
# BARE_LLM_TEMPLATE est utilisé par /chat?mode=llm_only — c'est le mode qui
# démontre les hallucinations en J1 matin (le LLM ne reçoit AUCUN document).
#
# --- Indice léger ---
# ChatPromptTemplate ultra-minimaliste : 2 messages (system + human), le human
# ne contient QUE la question (pas de context).
#
# --- Indice fort ---
# ```python
# BARE_LLM_TEMPLATE = ChatPromptTemplate.from_messages([
#     ("system", CONCIERGE_SYSTEM_PROMPT),
#     ("human", "{question}"),
# ])
# ```
BARE_LLM_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "TODO Atelier 01 — réécris ce system prompt"),
    ("human", "{question}"),
])
