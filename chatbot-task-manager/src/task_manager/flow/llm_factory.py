"""Сборка LLM и лимитов агентов CrewAI из настроек приложения."""

from crewai import LLM
from loguru import logger

from src.task_manager.config.settings import settings


def build_crew_llm() -> LLM:
    """
    LLM для CrewAI через OpenAI-compatible vLLM (/v1/chat/completions).
    """
    if not settings.vllm_base_url or not settings.llm_model_name:
        raise ValueError(
            "Не заданы VLLM_BASE_URL и LLM_MODEL_NAME. "
            "Укажите их в .env для работы CrewAI."
        )

    model = settings.llm_model_name
    if "/" in model and not model.startswith(("openai/", "hosted_vllm/")):
        # LiteLLM (через CrewAI) ожидает префикс провайдера для custom OpenAI API
        model = f"openai/{model}"

    llm_kwargs: dict = {
        "model": model,
        "base_url": settings.vllm_base_url.rstrip("/"),
        "api_key": settings.vllm_api_key or "not-needed",
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
    }

    if not settings.llm_reasoning:
        llm_kwargs["reasoning_effort"] = "none"
        # Qwen3 на vLLM: явно отключаем thinking в chat template
        llm_kwargs["extra_body"] = {
            "chat_template_kwargs": {"enable_thinking": False},
        }

    logger.info(
        f"Crew LLM → vLLM: model={model}, base_url={settings.vllm_base_url}, "
        f"reasoning={settings.llm_reasoning}, max_tokens={settings.llm_max_tokens}"
    )

    return LLM(**llm_kwargs)


def crew_agent_kwargs() -> dict:
    """Общие лимиты для Agent в crew (max_iter ≈ AGENT_REQUEST_LIMIT)."""
    return {
        "max_iter": settings.agent_request_limit,
        "max_tool_calls": settings.agent_tool_calls_limit,
    }
