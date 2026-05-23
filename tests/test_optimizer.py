"""OPRO 优化器测试"""

from src.core.optimizer import parse_candidates


def test_parse_candidates():
    content = """
    一些前置内容
    ---PROMPT_START---
    你是一个客服助手。请回答用户问题。
    ---PROMPT_END---
    ---PROMPT_START---
    你是专业客服。回答时要礼貌。
    ---PROMPT_END---
    """
    candidates = parse_candidates(content)
    assert len(candidates) == 2
    assert "客服助手" in candidates[0]
    assert "礼貌" in candidates[1]


def test_parse_candidates_empty():
    candidates = parse_candidates("no prompts here")
    assert isinstance(candidates, list)


def test_parse_candidates_fallback():
    content = "Some text --- candidate one prompt --- candidate two prompt ---"
    candidates = parse_candidates(content)
    assert isinstance(candidates, list)
