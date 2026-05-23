"""CLI 入口 - 命令行方式运行优化流程"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.infrastructure.config import load_config
from src.infrastructure.logger import setup_logger
from src.core.schemas import TestCase
from src.application.runner import OptimizationRunner
from src.application.exporter import generate_report


console = Console()


def load_test_cases(path: str) -> list[TestCase]:
    """从 JSONL 文件加载测试集"""
    cases = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            cases.append(TestCase(
                id=data.get("id", f"case_{line_num:03d}"),
                input=data["input"],
                expected=data["expected"],
                eval_rubric=data.get("eval_rubric"),
                tags=data.get("tags", []),
            ))
    return cases


async def main() -> None:
    parser = argparse.ArgumentParser(description="提示词优化引擎 CLI")
    parser.add_argument("--task", required=True, help="任务描述")
    parser.add_argument("--test-set", required=True, help="测试集文件路径 (JSONL)")
    parser.add_argument("--prompt", default=None, help="初始系统提示词")
    parser.add_argument("--config", default="configs/default.yaml", help="配置文件路径")
    parser.add_argument("--output", default=None, help="报告输出路径")
    args = parser.parse_args()

    setup_logger()
    config = load_config(args.config)

    console.print(f"[bold green]任务:[/bold green] {args.task}")
    console.print(f"[bold green]测试集:[/bold green] {args.test_set}")

    cases = load_test_cases(args.test_set)
    console.print(f"[bold green]测试用例数:[/bold green] {len(cases)}")

    def on_progress(msg: str, pct: float) -> None:
        pass

    runner = OptimizationRunner(config=config, on_progress=on_progress)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("优化中...", total=None)
        result = await runner.run(
            task_desc=args.task,
            test_cases=cases,
            initial_prompt=args.prompt,
        )
        progress.update(task, completed=True)

    console.print(f"\n[bold green]优化完成![/bold green]")
    console.print(f"  初始得分: {result.initial_score:.2f}")
    console.print(f"  最终得分: {result.best_score:.2f}")
    console.print(f"  提升幅度: {result.improvement_pct:+.1f}%")

    report = generate_report(result)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        console.print(f"\n报告已保存: {args.output}")
    else:
        console.print("\n" + report)


if __name__ == "__main__":
    asyncio.run(main())
