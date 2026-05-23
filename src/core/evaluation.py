"""并发评估管道 - 批量评估调度：并发执行 Judge、聚合分数、处理异常重试"""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from src.infrastructure.config import EvaluationConfig
from src.infrastructure.llm_adapter import call_llm
from src.core.schemas import TestCase, CaseScore, EvaluationResult
from src.core.judge import call_judge


class EvaluationPipeline:
    def __init__(self, config: EvaluationConfig, executor_model: str, judge_model: str):
        self.config = config
        self.executor_model = executor_model
        self.judge_model = judge_model
        self.semaphore = asyncio.Semaphore(config.max_concurrency)

    async def evaluate_batch(
        self,
        prompt: str,
        test_cases: list[TestCase],
    ) -> EvaluationResult:
        """并发评估整个测试集"""
        tasks = [
            self._evaluate_single(prompt, case, idx)
            for idx, case in enumerate(test_cases)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scores: list[CaseScore] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Eval failed for case {i}: {result}")
                scores.append(CaseScore(
                    case_id=test_cases[i].id,
                    score=0.0,
                    output="",
                    judge_reasoning=f"评估失败: {result}",
                ))
            else:
                scores.append(result)

        eval_result = EvaluationResult(prompt=prompt, scores=scores)
        eval_result.compute_avg()
        logger.info(f"Evaluation done: avg_score={eval_result.avg_score:.2f} ({len(scores)} cases)")
        return eval_result

    async def _evaluate_single(
        self,
        prompt: str,
        case: TestCase,
        idx: int,
    ) -> CaseScore:
        """评估单个测试用例：先执行生成回答，再用Judge评分"""
        async with self.semaphore:
            # 1. 用执行模型生成回答
            exec_response = await call_llm(
                model=self.executor_model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": case.input},
                ],
                temperature=0.3,
            )

            # 2. 用Judge模型评分
            case_score = await call_judge(
                judge_model=self.judge_model,
                input_text=case.input,
                expected=case.expected,
                actual_output=exec_response.content,
                eval_rubric=case.eval_rubric,
                cache_key=f"judge_{prompt[:50]}_{case.id}",
            )
            case_score.case_id = case.id

            logger.debug(f"Case {idx} ({case.id}): score={case_score.score}")
            return case_score

    async def execute_and_evaluate(
        self,
        prompt: str,
        test_cases: list[TestCase],
    ) -> EvaluationResult:
        """完整的执行+评估流程"""
        return await self.evaluate_batch(prompt, test_cases)
