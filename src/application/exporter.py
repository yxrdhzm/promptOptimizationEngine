"""报告导出 - Markdown格式完整评估报告"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.core.schemas import OptimizationResult


def generate_report(result: OptimizationResult) -> str:
    """生成 Markdown 格式的完整评估报告"""
    lines = [
        f"# 提示词优化报告",
        f"",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**运行ID**: `{result.run_id}`",
        f"",
        f"## 任务描述",
        f"",
        f"{result.task_desc}",
        f"",
        f"## 优化结果摘要",
        f"",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| 初始得分 | {result.initial_score:.2f} |",
        f"| 最终得分 | {result.best_score:.2f} |",
        f"| 提升幅度 | {result.improvement_pct:+.1f}% |",
        f"| 迭代轮数 | {result.iterations} |",
        f"",
        f"## 最优提示词",
        f"",
        f"```",
        f"{result.best_prompt}",
        f"```",
        f"",
        f"## 迭代历史",
        f"",
        f"| 轮次 | 得分 | 备注 |",
        f"|------|------|------|",
    ]

    for step in result.history:
        lines.append(f"| {step.iteration} | {step.score:.2f} | {step.notes} |")

    lines.extend([
        f"",
        f"## 原始提示词",
        f"",
        f"```",
        f"{result.initial_prompt}",
        f"```",
        f"",
        f"---",
        f"",
        f"*报告由提示词优化引擎自动生成*",
    ])

    return "\n".join(lines)


def generate_diff(old_prompt: str, new_prompt: str) -> str:
    """生成两个提示词的差异对比"""
    old_lines = old_prompt.splitlines()
    new_lines = new_prompt.splitlines()

    lines = ["# Prompt Diff", ""]

    max_len = max(len(old_lines), len(new_lines))
    for i in range(max_len):
        old = old_lines[i] if i < len(old_lines) else ""
        new = new_lines[i] if i < len(new_lines) else ""

        if old == new:
            lines.append(f"  {old}")
        else:
            if old:
                lines.append(f"- {old}")
            if new:
                lines.append(f"+ {new}")

    return "\n".join(lines)
