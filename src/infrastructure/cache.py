"""评估缓存 - 基于 diskcache，相同 Prompt+Input 的评估结果缓存"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from diskcache import Cache


class EvalCache:
    def __init__(self, cache_dir: str = "data/cache", ttl: int = 86400):
        self.cache = Cache(cache_dir)
        self.ttl = ttl

    def _make_key(self, prompt: str, input_text: str, model: str) -> str:
        raw = f"{prompt}||{input_text}||{model}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, prompt: str, input_text: str, model: str) -> Any | None:
        key = self._make_key(prompt, input_text, model)
        return self.cache.get(key)

    def set(self, prompt: str, input_text: str, model: str, value: Any) -> None:
        key = self._make_key(prompt, input_text, model)
        self.cache.set(key, value, expire=self.ttl)

    def has(self, prompt: str, input_text: str, model: str) -> bool:
        key = self._make_key(prompt, input_text, model)
        return key in self.cache

    def clear(self) -> int:
        count = len(self.cache)
        self.cache.clear()
        return count

    def stats(self) -> dict[str, Any]:
        return {
            "size": len(self.cache),
            "directory": self.cache.directory,
        }
