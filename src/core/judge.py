"""LLM Judge - 封装评估逻辑：构建评分Prompt、解析结构化评分结果"""

from __future__ import annotations

import json
import re
from typing import Any

from loguru import logger

from src.infrastructure.llm_adapter import call_llm
from src.core.schemas import CaseScore


def _parse_judge_response(content: str) -> dict[str, Any]:
    """解析Judge模型的JSON输出"""
    # 尝试提取 JSON 块
    json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试直接解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # 尝试找到第一个 { 到最后一个 }
    start = content.find("{")
    end = content.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass

    logger.warning(f"Failed to parse judge response: {content[:200]}")
    return {"score": 3, "reasoning": "评分解析失败，默认3分"}


async def call_judge(
    judge_model: str,
    input_text: str,
    expected: str,
    actual_output: str,
    eval_rubric: str | None = None,
    cache_key: str | None = None,
) -> CaseScore:
    """调用Judge模型对单个输出进行评分"""
    from jinja2 import Environment, FileSystemLoader
    from pathlib import Path

    template_dir = Path(__file__).parent / "templates"
    jinja_env = Environment(loader=FileSystemLoader(template_dir))
    template = jinja_env.get_template("judge_rubric.j2")

    prompt = template.render(
        input=input_text,
        expected=expected,
        actual_output=actual_output,
        eval_rubric=eval_rubric,
    )

    response = await call_llm(
        model=judge_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,  # Judge需要低温度保证一致性
        max_tokens=1024,
        cache_key=cache_key,
    )

    result = _parse_judge_response(response.content)
    score = float(result.get("score", 3))
    score = max(1.0, min(5.0, score))  # 钳位到 1-5
    reasoning = result.get("reasoning", "")

    return CaseScore(
        case_id="",
        score=score,
        output=actual_output,
        judge_reasoning=reasoning,
    )
