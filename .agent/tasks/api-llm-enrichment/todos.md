# TODOs — Enrichissement API/LLM HomeButler (RAFT)

## BLOC 3 — homebutler/llm/provider.py ✅
- [x] Ajouter paramètre `streaming` à `get_llm()`
- [x] Créer `get_llm_cached()` avec Anthropic prompt caching

## BLOC 4 — homebutler/llm/prompts.py ✅
- [x] Ajouter `BARE_LLM_TEMPLATE` (mode sans contexte documentaire)

## BLOC 5 — homebutler/agent/react_agent.py ✅
- [x] Ajouter `get_session_agent(session_id)` avec `ConversationBufferWindowMemory`
- [x] Passer à `hwchase17/react-chat` (supporte `chat_history`)
- [x] Ajouter paramètres `debug` et `memory` à `get_agent_executor()`
- [x] Mettre à jour le fallback local pour inclure `{chat_history}`

## BLOC 1 — api/routers/chat.py ✅
- [x] Nouveaux modèles Pydantic (`SourceDoc`, `ChatResponse` enrichi, `CompareResponse`)
- [x] Logique `mode="llm_only"` avec `BARE_LLM_TEMPLATE`
- [x] Logique `mode="rag_only"` avec sources retournées
- [x] Logique `mode="agent"` avec session memory + debug steps
- [x] `POST /chat/compare` — 3 modes en parallèle
- [x] `GET /chat/stream` — SSE streaming

## BLOC 2 — api/routers/rag.py (création) ✅
- [x] `POST /rag/retrieve` — chunks pour une query + strategy
- [x] `POST /rag/evaluate` — Recall@1/@3/@5 sur QA dataset
- [x] `POST /rag/compare-strategies` — 3 chunkers sur même query

## BLOC 6 — api/main.py ✅
- [x] Ajouter `slowapi` rate limiting (30/min sur /chat)
- [x] Étendre patterns injection (9 patterns → 19)
- [x] Ajouter validation API key optionnelle
- [x] Inclure `rag.router`
- [x] Ajouter `slowapi` à `requirements.txt`

## BLOC 9 — scripts/augment_qa_dataset.py (création) ✅
- [x] Fonction `paraphrase_question()` (variantes linguistiques)
- [x] Fonction `augment_dataset()` (150 → 431 paires après dédup)
- [x] Écriture `augmented_concierge_qa.jsonl`
- [x] Exécuter et valider le script — 431 paires (cible ~500, dédup réduit)

## BLOC 7 — notebooks/01_llm_baseline.ipynb ✅
- [x] Cellule intro + tableau comparatif HF vs Ollama (markdown)
- [x] Cellule install Colab (transformers, torch, bitsandbytes)
- [x] Cellule chargement Mistral-7B avec QLoRA 4-bit
- [x] Cellule test 5 questions via HF (format [INST]...[/INST])
- [x] Cellule tableau comparatif HF vs Ollama avec grille décision

## BLOC 8 — notebooks/02_ingestion_vectorisation.ipynb ✅
- [x] Cellule markdown panorama frameworks (LangChain vs LlamaIndex vs Haystack)
- [x] Tableau FAISS vs ChromaDB vs Weaviate vs Pinecone
- [x] Cellule code LlamaIndex syntaxe (commentée) + comparaison LangChain

## BLOC 10 — notebooks/03_finetuning_lora.ipynb (création) ✅
- [x] Section 1 : théorie Full FT vs LoRA vs QLoRA (tableau, formule W=W₀+α×BA)
- [x] Section 2 : setup Colab + vérif GPU + install (transformers, peft, trl, bitsandbytes, mlflow)
- [x] Section 3 : chargement dataset URL/local + formatage Mistral + split 90/10
- [x] Section 4 : modèle base QLoRA 4-bit (BitsAndBytesConfig NF4)
- [x] Section 5 : config LoRA (r=8, q_proj/v_proj) + tableau impact rang r
- [x] Section 6 : SFTTrainer + MLFlow tracking (params + métriques)
- [x] Section 7 : évaluation qualitative avant/après + ROUGE-L quantitatif
- [x] Section 8 : distillation Teacher→Student (concept + pseudocode Claude API)
- [x] Section 9 : export GGUF (merge → llama.cpp Q4_K_M) + Modelfile Ollama + bascule .env

## VALIDATION FINALE
- [x] pip install slowapi dans venv
- [x] Restart API + test curl mode llm_only → hallucine + token_usage ✅
- [x] Test curl mode rag_only + debug → "Viessmann" + sources[] ✅
- [x] Test curl /chat/compare (3 modes) → llm_only hallucine, rag_only+agent OK ✅
- [x] Test mémoire conversationnelle → 2e tour utilise contexte 1er ✅
- [x] Test /rag/retrieve → 6 chunks avec attribution source ✅
- [x] Test /rag/evaluate → recall@1=0.7, recall@3=0.8, recall@5=1.0 ✅
- [x] Test /rag/compare-strategies → fixed/recursive/ensemble avec chunks différents ✅
- [x] Test /chat/stream (SSE) → tokens streamés un par un ✅
- [x] Test rate limiting → 35 requêtes parallèles : 21×200 + 14×429 ✅ (fix: api/limiter.py partagé)
- [x] Exécuter augment_qa_dataset.py → 431 paires ✅
- [x] Git commit final → db11074 "feat: complétion RAFT — BLOCs 7-10 + fix rate limiting"
