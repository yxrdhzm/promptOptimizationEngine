"""轻量持久化 - SQLite + SQLModel，存储测试集、优化记录、Token 用量"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlmodel import SQLModel, Session, create_engine, Field, select

from src.infrastructure.config import AppConfig


# --- 数据模型 ---

class TestSetRecord(SQLModel, table=True):
    __tablename__ = "test_sets"
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    name: str
    data: str  # JSON string of test cases
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class OptimizationRunRecord(SQLModel, table=True):
    __tablename__ = "optimization_runs"
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    task_desc: str
    initial_prompt: str
    best_prompt: str
    best_score: float
    iterations: int
    history: str  # JSON string of OptimizationStep list
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class TokenUsageRecord(SQLModel, table=True):
    __tablename__ = "token_usage"
    id: int | None = Field(default=None, primary_key=True)
    run_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# --- Store ---

class Store:
    def __init__(self, config: AppConfig):
        db_path = config.storage.db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        SQLModel.metadata.create_all(self.engine)

    def save_test_set(self, name: str, cases: list[dict[str, Any]]) -> str:
        record = TestSetRecord(name=name, data=json.dumps(cases, ensure_ascii=False))
        with Session(self.engine) as session:
            session.add(record)
            session.commit()
            session.refresh(record)
        return record.id

    def get_test_set(self, record_id: str) -> list[dict[str, Any]] | None:
        with Session(self.engine) as session:
            record = session.get(TestSetRecord, record_id)
            if record:
                return json.loads(record.data)
        return None

    def list_test_sets(self) -> list[dict[str, Any]]:
        with Session(self.engine) as session:
            stmt = select(TestSetRecord)
            records = session.exec(stmt).all()
        return [{"id": r.id, "name": r.name, "created_at": r.created_at} for r in records]

    def save_run(
        self,
        task_desc: str,
        initial_prompt: str,
        best_prompt: str,
        best_score: float,
        iterations: int,
        history: list[dict[str, Any]],
    ) -> str:
        record = OptimizationRunRecord(
            task_desc=task_desc,
            initial_prompt=initial_prompt,
            best_prompt=best_prompt,
            best_score=best_score,
            iterations=iterations,
            history=json.dumps(history, ensure_ascii=False),
        )
        with Session(self.engine) as session:
            session.add(record)
            session.commit()
            session.refresh(record)
        return record.id

    def save_token_usage(
        self, run_id: str, model: str, prompt_tokens: int, completion_tokens: int, latency_ms: float
    ) -> None:
        record = TokenUsageRecord(
            run_id=run_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
        )
        with Session(self.engine) as session:
            session.add(record)
            session.commit()

    def get_token_usage(self, run_id: str) -> dict[str, Any]:
        with Session(self.engine) as session:
            stmt = select(TokenUsageRecord).where(TokenUsageRecord.run_id == run_id)
            records = session.exec(stmt).all()

        total_prompt = sum(r.prompt_tokens for r in records)
        total_completion = sum(r.completion_tokens for r in records)
        total_latency = sum(r.latency_ms for r in records)
        return {
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_latency_ms": total_latency,
            "call_count": len(records),
        }
