"""统一模型调用接口 - 通过 LiteLLM 支持 100+ 模型无缝切换"""

from __future__ import annotations

import time
from typing import Any

from loguru import logger
from pydantic import BaseModel

from src.infrastructure.cache import EvalCache


class LLMResponse(BaseModel):
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float


_cache: EvalCache | None = None


def init_cache(cache_dir: str = "data/cache", ttl: int = 86400) -> None:
    global _cache
    _cache = EvalCache(cache_dir, ttl)


async def call_llm(
    model: str,
    messages: list[dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 4096,
    cache_key: str | None = None,
    **kwargs: Any,
) -> LLMResponse:
    """统一异步调用入口，内置缓存、重试、Token统计"""
    import litellm

    # 检查缓存
    if cache_key and _cache and _cache.has(cache_key, str(messages), model):
        cached = _cache.get(cache_key, str(messages), model)
        if cached is not None:
            logger.debug(f"Cache hit: {model}")
            return LLMResponse(**cached)

    start = time.monotonic()
    try:
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        latency_ms = (time.monotonic() - start) * 1000

        content = response.choices[0].message.content or ""
        prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        completion_tokens = response.usage.completion_tokens if response.usage else 0

        result = LLMResponse(
            content=content,
            model=response.model or model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
        )

        logger.info(
            f"LLM call: {model} | tokens: {prompt_tokens}+{completion_tokens} | {latency_ms:.0f}ms"
        )

        # 写入缓存
        if cache_key and _cache:
            _cache.set(cache_key, str(messages), model, result.model_dump())

        return result

    except Exception as e:
        latency_ms = (time.monotonic() - start) * 1000
        logger.error(f"LLM call failed: {model} | {latency_ms:.0f}ms | {e}")
        raise
