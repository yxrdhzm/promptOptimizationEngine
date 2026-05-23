"""报告导出测试"""

from src.core.schemas import OptimizationResult, OptimizationStep
from src.application.exporter import generate_report, generate_diff


def test_generate_report():
    result = OptimizationResult(
        task_desc="电商客服",
        initial_prompt="你是客服",
        best_prompt="你是专业客服助手",
        best_score=4.5,
        initial_score=3.0,
        iterations=3,
        history=[
            OptimizationStep(iteration=1, prompt="v1", score=3.5, notes="第一轮"),
            OptimizationStep(iteration=2, prompt="v2", score=4.0, notes="第二轮"),
            OptimizationStep(iteration=3, prompt="v3", score=4.5, notes="第三轮"),
        ],
    )
    result.compute_improvement()

    report = generate_report(result)
    assert "电商客服" in report
    assert "4.50" in report
    assert "+50.0%" in report


def test_generate_diff():
    diff = generate_diff("line1\nline2", "line1\nline3")
    assert "- line2" in diff
    assert "+ line3" in diff
