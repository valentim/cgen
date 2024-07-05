import pytest
from tot.node import Node
from ai.prompt import Prompt
from tot.three_of_thoughts import TreeOfThoughts


class MockAIProvider:
    BASE_VARIATIONS = ["variation1", "variation2", "variation3"]

    def generate_code(self, node):
        return f"code for {node.prompt.details}"

    def get_prompt_details(self, prompt):
        return ["detail1", "detail2"]


class MockCodeEvaluator:
    def evaluate_solution(self, code, test_list):
        if "variation1" in code:
            return 100, []
        else:
            return 50, ["error1"]


@pytest.fixture
def ai_provider():
    return MockAIProvider()


@pytest.fixture
def code_evaluator():
    return MockCodeEvaluator()


@pytest.fixture
def tree_of_thoughts(ai_provider, code_evaluator):
    # pass
    return TreeOfThoughts(ai_provider, code_evaluator, max_depth=3)


def test_expand_root_node(tree_of_thoughts):
    initial_prompt = Prompt("task", ["test1", "test2"], [], [])
    root = Node(parent=None, prompt=initial_prompt)

    children = tree_of_thoughts.expand(root)

    assert len(children) == len(tree_of_thoughts.ai_provider.BASE_VARIATIONS)
    for child in children:
        assert child.code is not None
        assert child.parent == root


def test_expand_non_root_node(tree_of_thoughts):
    initial_prompt = Prompt("task", ["test1", "test2"], [], [])
    root = Node(parent=None, prompt=initial_prompt)
    non_root_node = Node(parent=root, prompt=initial_prompt)

    children = tree_of_thoughts.expand(non_root_node)

    assert len(children) == 3
    for child in children:
        assert child.code is not None
        assert child.parent == non_root_node


def test_find_the_best_solution(tree_of_thoughts):
    initial_prompt = "task"
    test_list = ["test1", "test2"]
    task_id = "1"

    best_solution = tree_of_thoughts.find_the_best_solution(
        initial_prompt, task_id, test_list
    )

    assert best_solution is not None
    assert best_solution.score == 100
    assert "variation1" in best_solution.code
