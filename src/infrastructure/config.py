"""配置管理 - 基于 pydantic-settings，支持 YAML + 环境变量覆盖"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ModelsConfig(BaseModel):
    executor: str = "openai/gpt-4o-mini"
    optimizer: str = "openai/gpt-4o"
    judge: str = "openai/gpt-4o-mini"


class OptimizerConfig(BaseModel):
    max_iterations: int = 5
    num_candidates: int = 3
    early_stop_patience: int = 2
    history_window: int = 5
    temperature: float = 0.9


class EvaluationConfig(BaseModel):
    max_concurrency: int = 10
    score_consistency_rounds: int = 1
    timeout_seconds: int = 60


class CacheConfig(BaseModel):
    enabled: bool = True
    ttl_seconds: int = 86400
    max_size_mb: int = 500


class StorageConfig(BaseModel):
    db_path: str = "data/cache.db"
    runs_dir: str = "data/runs"


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "data/optimizer.log"


class AppConfig(BaseSettings):
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    optimizer: OptimizerConfig = Field(default_factory=OptimizerConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    model_config = {"env_prefix": "PO_"}


def load_config(config_path: str | Path = "configs/default.yaml") -> AppConfig:
    """加载配置文件，环境变量可覆盖 YAML 中的值"""
    path = Path(config_path)
    data: dict[str, Any] = {}
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    return AppConfig(**data)
