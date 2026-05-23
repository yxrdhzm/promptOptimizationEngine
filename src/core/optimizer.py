"""OPRO 优化器 - 封装优化算法：构建元提示、解析LLM输出、管理历史轨迹"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from loguru import logger

from src.infrastructure.config import OptimizerConfig
from src.infrastructure.llm_adapter import call_llm
from src.core.schemas import OptimizationStep, TestCase

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_jinja_env = Environment(loader=FileSystemLoader(_TEMPLATE_DIR))


def render_template(name: str, **kwargs: Any) -> str:
    template = _jinja_env.get_template(name)
    return template.render(**kwargs)


def parse_candidates(content: str) -> list[str]:
    """从LLM输出中解析候选提示词"""
    pattern = r"---PROMPT_START---\s*(.*?)\s*---PROMPT_END---"
    matches = re.findall(pattern, content, re.DOTALL)
    candidates = [m.strip() for m in matches if m.strip()]
    if not candidates:
        # fallback: 按 --- 分割
        parts = content.split("---")
        candidates = [p.strip() for p in parts if p.strip() and len(p.strip()) > 50]
    return candidates


class OPROOptimizer:
    def __init__(self, config: OptimizerConfig, optimizer_model: str):
        self.config = config
        self.optimizer_model = optimizer_model
        self.history: list[OptimizationStep] = []

    async def generate_candidates(
        self,
        task_desc: str,
        failed_cases: list[dict[str, Any]] | None = None,
    ) -> list[str]:
        """基于历史轨迹和失败案例，生成N个候选Prompt"""
        meta_prompt = render_template(
            "opro_meta.j2",
            task=task_desc,
            history=[
                {"iteration": s.iteration, "score": s.score, "prompt": s.prompt, "notes": s.notes}
                for s in self.history[-self.config.history_window :]
            ],
            failed_cases=failed_cases or [],
            num_candidates=self.config.num_candidates,
        )

        response = await call_llm(
            model=self.optimizer_model,
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=self.config.temperature,
            cache_key=None,  # 优化器调用不缓存
        )

        candidates = parse_candidates(response.content)
        logger.info(f"Generated {len(candidates)} candidates")
        return candidates[: self.config.num_candidates]

    def update(self, step: OptimizationStep) -> None:
        """记录本轮最优结果"""
        self.history.append(step)

    def should_stop(self) -> bool:
        """早停判断：连续 patience 轮无提升则停止"""
        if len(self.history) < self.config.early_stop_patience + 1:
            return False
        recent = self.history[-self.config.early_stop_patience :]
        scores = [s.score for s in recent]
        return max(scores) - min(scores) < 0.01

    def get_best(self) -> OptimizationStep | None:
        if not self.history:
            return None
        return max(self.history, key=lambda s: s.score)

    def get_failed_cases_details(
        self, scores: list[dict[str, Any]], top_n: int = 3
    ) -> list[dict[str, Any]]:
        """提取得分最低的 top_n 个案例"""
        sorted_scores = sorted(scores, key=lambda x: x.get("score", 0))
        return sorted_scores[:top_n]
