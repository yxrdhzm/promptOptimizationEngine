"""优化流程编排 - 加载数据 → 循环迭代 → 收集结果 → 生成报告"""

from __future__ import annotations

from typing import Any, Callable

from loguru import logger

from src.infrastructure.config import AppConfig, load_config
from src.infrastructure.llm_adapter import init_cache
from src.infrastructure.store import Store
from src.core.schemas import TestCase, OptimizationStep, OptimizationResult
from src.core.optimizer import OPROOptimizer
from src.core.evaluation import EvaluationPipeline


class OptimizationRunner:
    def __init__(
        self,
        config: AppConfig | None = None,
        on_progress: Callable[[str, float], None] | None = None,
    ):
        self.config = config or load_config()
        self.store = Store(self.config)

        # 初始化缓存
        init_cache(ttl=self.config.cache.ttl_seconds)

        # 初始化核心组件
        self.optimizer = OPROOptimizer(
            config=self.config.optimizer,
            optimizer_model=self.config.models.optimizer,
        )
        self.evaluator = EvaluationPipeline(
            config=self.config.evaluation,
            executor_model=self.config.models.executor,
            judge_model=self.config.models.judge,
        )
        self.on_progress = on_progress or (lambda msg, pct: None)

    def _report(self, msg: str, pct: float) -> None:
        logger.info(f"[{pct*100:.0f}%] {msg}")
        self.on_progress(msg, pct)

    async def run(
        self,
        task_desc: str,
        test_cases: list[TestCase],
        initial_prompt: str | None = None,
    ) -> OptimizationResult:
        """执行完整的优化流程"""
        max_iter = self.config.optimizer.max_iterations

        # 使用默认初始 prompt
        if not initial_prompt:
            initial_prompt = (
                "You are a helpful AI assistant. "
                "Please answer the user's question accurately and thoroughly."
            )

        self._report("Evaluating initial prompt...", 0.0)

        # 1. 评估初始 Prompt
        init_result = await self.evaluator.execute_and_evaluate(initial_prompt, test_cases)
        init_score = init_result.avg_score

        best_prompt = initial_prompt
        best_score = init_score

        self._report(f"Initial prompt score: {init_score:.2f}", 0.05)

        # 2. 迭代优化
        for iteration in range(1, max_iter + 1):
            progress = 0.05 + (iteration / max_iter) * 0.85
            self._report(f"Iteration {iteration}/{max_iter}...", progress)

            # 生成候选
            failed_details = []
            if self.optimizer.history:
                last_scores = self.optimizer.history[-1]
                # 从上一轮评估结果中提取失败案例
                # 这里简化处理，后续可以从 EvaluationResult 中获取

            candidates = await self.optimizer.generate_candidates(task_desc, failed_details)

            if not candidates:
                logger.warning(f"Round {iteration}: no candidates generated, skipping")
                continue

            # 评估所有候选
            best_candidate = ""
            best_candidate_score = -1.0

            for c_idx, candidate in enumerate(candidates):
                eval_result = await self.evaluator.execute_and_evaluate(candidate, test_cases)
                score = eval_result.avg_score

                self._report(
                    f"  Candidate {c_idx+1}/{len(candidates)}: score={score:.2f}",
                    progress,
                )

                if score > best_candidate_score:
                    best_candidate_score = score
                    best_candidate = candidate

            # 记录本轮最优
            step = OptimizationStep(
                iteration=iteration,
                prompt=best_candidate,
                score=best_candidate_score,
                candidates=candidates,
                failed_cases=[],
                notes=f"Best score this round: {best_candidate_score:.2f}",
            )
            self.optimizer.update(step)

            if best_candidate_score > best_score:
                best_score = best_candidate_score
                best_prompt = best_candidate

            self._report(
                f"Round {iteration} done: best={best_candidate_score:.2f}, global best={best_score:.2f}",
                progress,
            )

            # 早停检查
            if self.optimizer.should_stop():
                self._report("No improvement, triggering early stop", progress)
                break

        self._report("Optimization complete!", 1.0)

        # 3. 构建结果
        result = OptimizationResult(
            task_desc=task_desc,
            initial_prompt=initial_prompt,
            best_prompt=best_prompt,
            best_score=best_score,
            initial_score=init_score,
            iterations=len(self.optimizer.history),
            history=self.optimizer.history,
        )
        result.compute_improvement()

        # 4. 持久化
        run_id = self.store.save_run(
            task_desc=task_desc,
            initial_prompt=initial_prompt,
            best_prompt=best_prompt,
            best_score=best_score,
            iterations=len(self.optimizer.history),
            history=[s.model_dump() for s in self.optimizer.history],
        )
        result.run_id = run_id

        return result
