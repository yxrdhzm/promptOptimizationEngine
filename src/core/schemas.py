"""Pydantic 数据模型 - 核心数据结构定义"""

from __future__ import annotations

from pydantic import BaseModel, Field
from uuid import uuid4


class TestCase(BaseModel):
    id: str = Field(default_factory=lambda: f"case_{uuid4().hex[:8]}")
    input: str
    expected: str
    eval_rubric: str | None = None
    tags: list[str] = Field(default_factory=list)


class CaseScore(BaseModel):
    case_id: str
    score: float
    output: str
    judge_reasoning: str = ""


class EvaluationResult(BaseModel):
    prompt: str
    scores: list[CaseScore]
    avg_score: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0

    def compute_avg(self) -> float:
        if self.scores:
            self.avg_score = sum(s.score for s in self.scores) / len(self.scores)
        return self.avg_score


class OptimizationStep(BaseModel):
    iteration: int
    prompt: str
    score: float
    candidates: list[str] = Field(default_factory=list)
    failed_cases: list[dict] = Field(default_factory=list)
    notes: str = ""


class OptimizationResult(BaseModel):
    run_id: str = Field(default_factory=lambda: uuid4().hex)
    task_desc: str
    initial_prompt: str
    best_prompt: str
    best_score: float
    initial_score: float
    iterations: int
    history: list[OptimizationStep]
    improvement_pct: float = 0.0

    def compute_improvement(self) -> float:
        if self.initial_score > 0:
            self.improvement_pct = ((self.best_score - self.initial_score) / self.initial_score) * 100
        return self.improvement_pct
