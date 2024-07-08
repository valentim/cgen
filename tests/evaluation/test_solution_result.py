import pytest
from evaluation.solution_result import SolutionResult


def test_solution_result_initialization():
    result = SolutionResult(
        task="print a hello, world", code="print('Hello, world!')", score=100.0
    )
    assert result.task == "print a hello, world"
    assert result.code == "print('Hello, world!')"
    assert result.score == 100.0


def test_solution_result_repr():
    result = SolutionResult(
        task="print a hello, world", code="print('Hello, world!')", score=100.0
    )
    assert (
        repr(result)
        == "SolutionResult(task=print a hello, world, code=print('Hello, world!'), score=100.0, errors=[])"
    )
