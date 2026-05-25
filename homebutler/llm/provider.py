"""
Provider LLM unifié — Atelier 01.

Une seule fonction `get_llm()` doit retourner soit Claude (cloud) soit Ollama (local)
selon la variable `config.LLM_PROVIDER`. C'est le seul point d'entrée vers le modèle
pour tout le reste du projet — d'où l'importance de garder une signature stable.

═══════════════════════════════════════════════════════════════════════════
🎓 Atelier 01 — Tu dois compléter `get_llm()` et `get_llm_cached()`.
   Solution finale (en dernier recours) :
   git diff student/01-llm-baseline atelier/01-llm-baseline -- homebutler/llm/provider.py
═══════════════════════════════════════════════════════════════════════════
"""

from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from homebutler import config


def get_llm(
    temperature: float = ...,   # TODO (indice : 0.0 = déterministe / 1.0 = créatif ; pour une conciergerie factuelle on vise plutôt 0.0–0.2)
    max_tokens: int = ...,      # TODO (indice : nombre maximum de tokens en sortie ; ~1024 = ~750 mots, largement suffisant pour une réponse de conciergerie)
    streaming: bool = False,
):
    """
    Retourne le LLM configuré selon LLM_PROVIDER.
    - "anthropic" → Claude via Anthropic API
    - "ollama"    → modèle local/VPS via Ollama
    streaming=True : active le streaming token par token (J3 déploiement).

    Args:
        temperature: contrôle l'aléatoire du sampling (0.0–1.0).
        max_tokens: limite de tokens générés par appel.
        streaming: True pour activer le streaming SSE (Atelier 05).

    Returns:
        Un objet LangChain BaseChatModel (ChatAnthropic ou ChatOllama).

    --- Indice léger ---
    Lis `config.LLM_PROVIDER` : c'est soit `"anthropic"` soit `"ollama"`.
    Pour Anthropic, vérifie d'abord que `config.ANTHROPIC_API_KEY` est défini
    (sinon `raise ValueError`). Ensuite, instancie `ChatAnthropic` (déjà importé)
    avec model / api_key / temperature / max_tokens / streaming.
    Pour Ollama, instancie `ChatOllama` avec base_url=config.OLLAMA_HOST,
    model=config.OLLAMA_MODEL, temperature, et `num_predict=max_tokens`
    (Ollama appelle ce paramètre `num_predict` au lieu de `max_tokens`).

    --- Indice fort ---
    ```python
    if config.LLM_PROVIDER == "anthropic":
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY manquant dans .env")
        return ChatAnthropic(
            model=config.ANTHROPIC_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
        )
    return ChatOllama(
        base_url=config.OLLAMA_HOST,
        model=config.OLLAMA_MODEL,
        temperature=temperature,
        num_predict=max_tokens,
    )
    ```
    """
    raise NotImplementedError(
        "Atelier 01 § 1.2 — provider LLM. "
        "Solution finale : git diff student/01-llm-baseline atelier/01-llm-baseline -- homebutler/llm/provider.py"
    )


def get_llm_cached(temperature: float = 0.1, max_tokens: int = 1024):
    """
    Version Anthropic avec prompt caching (beta 'prompt-caching-2024-07-31').
    Réduit le coût token du system prompt après le premier appel (cache 5 min).
    Pédagogie J3 — optimisation production.
    Fallback sur get_llm() si provider != anthropic.

    --- Indice léger ---
    Même logique que `get_llm()` mais on ajoute un header HTTP Anthropic
    via `model_kwargs={"extra_headers": {"anthropic-beta": "prompt-caching-2024-07-31"}}`.
    Si on n'est PAS sur Anthropic, on délègue à `get_llm(temperature, max_tokens)`.

    --- Indice fort ---
    ```python
    if config.LLM_PROVIDER == "anthropic":
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY manquant dans .env")
        return ChatAnthropic(
            model=config.ANTHROPIC_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
            model_kwargs={
                "extra_headers": {"anthropic-beta": "prompt-caching-2024-07-31"}
            },
        )
    return get_llm(temperature, max_tokens)
    ```
    """
    raise NotImplementedError(
        "Atelier 01 § 1.3 — prompt caching Anthropic. "
        "Solution finale : git diff student/01-llm-baseline atelier/01-llm-baseline -- homebutler/llm/provider.py"
    )
