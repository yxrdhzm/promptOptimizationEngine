"""数据模型测试"""

from src.core.schemas import TestCase, CaseScore, EvaluationResult, OptimizationStep, OptimizationResult


def test_test_case_creation():
    case = TestCase(input="hello", expected="world")
    assert case.input == "hello"
    assert case.expected == "world"
    assert case.id.startswith("case_")


def test_case_score():
    score = CaseScore(case_id="c1", score=4.5, output="test output")
    assert score.score == 4.5


def test_evaluation_result_avg():
    result = EvaluationResult(
        prompt="test",
        scores=[
            CaseScore(case_id="c1", score=4.0, output="a"),
            CaseScore(case_id="c2", score=5.0, output="b"),
        ],
    )
    avg = result.compute_avg()
    assert avg == 4.5


def test_optimization_result_improvement():
    result = OptimizationResult(
        task_desc="test",
        initial_prompt="old",
        best_prompt="new",
        best_score=4.5,
        initial_score=3.0,
        iterations=3,
        history=[],
    )
    pct = result.compute_improvement()
    assert pct == 50.0
