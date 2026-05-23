"""结构化日志 - loguru + structlog"""

from __future__ import annotations

import sys
from pathlib import Path

import structlog
from loguru import logger


def setup_logger(level: str = "INFO", log_file: str | None = None) -> None:
    """配置全局日志"""
    logger.remove()
    logger.add(sys.stderr, level=level, format="{time:HH:mm:ss} | {level:<7} | {message}")

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        logger.add(log_file, level=level, rotation="10 MB", retention="7 days")


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取结构化日志实例"""
    return structlog.get_logger(name)
