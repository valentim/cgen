import pytest
from unittest.mock import Mock
from evaluation.code_evaluator import CodeEvaluator


@pytest.fixture
def mock_code_executor():
    return Mock()


@pytest.fixture
def code_evaluator(mock_code_executor):
    return CodeEvaluator(mock_code_executor)


def test_evaluate_solution_success(code_evaluator, mock_code_executor):
    mock_code_executor.execute_test.return_value = (True, None)

    code = "def add(a, b): return a + b"
    test_list = [
        "assert add(1, 2) == 3",
        "assert add(0, 0) == 0",
        "assert add(-1, -1) == -2",
    ]

    score, errors = code_evaluator.evaluate_solution(code, test_list)

    assert score == 100
    assert errors == []
    assert mock_code_executor.execute_test.call_count == len(test_list)


def test_evaluate_solution_partial_success(code_evaluator, mock_code_executor):
    mock_code_executor.execute_test.side_effect = [
        (True, None),
        (False, "Test failed"),
        (True, None),
    ]

    code = "def add(a, b): return a + b"
    test_list = [
        "assert add(1, 2) == 3",
        "assert add(0, 0) == 1",
        "assert add(-1, -1) == -2",
    ]

    score, errors = code_evaluator.evaluate_solution(code, test_list)

    assert score == (2 / 3) * 100
    assert errors == ["Test failed"]
    assert mock_code_executor.execute_test.call_count == len(test_list)


def test_evaluate_solution_failure(code_evaluator, mock_code_executor):
    mock_code_executor.execute_test.return_value = (False, "Test failed")

    code = "def add(a, b): return a + b"
    test_list = [
        "assert add(1, 2) == 4",
        "assert add(0, 0) == 1",
        "assert add(-1, -1) == 0",
    ]

    score, errors = code_evaluator.evaluate_solution(code, test_list)

    assert score == 0
    assert errors == ["Test failed", "Test failed", "Test failed"]
    assert mock_code_executor.execute_test.call_count == len(test_list)
