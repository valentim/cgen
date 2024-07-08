from collections import deque
from evaluation.solution_result import SolutionResult
from .node import Node
from ai.prompt import Prompt
from ai.openai_provider import OpenAIProvider
from evaluation.code_evaluator import CodeEvaluator
from utils.logger import get_logger

_LOGGER = get_logger(__name__)


class TreeOfThoughts:
    def __init__(
        self, ai_provider: OpenAIProvider, code_evaluator: CodeEvaluator, max_depth=3
    ):
        self.ai_provider: OpenAIProvider = ai_provider
        self.code_evaluator: CodeEvaluator = code_evaluator
        self.max_depth = max_depth

    def expand(self, node: Node) -> list[Node]:
        def add_variations(node, new_prompt) -> Node:
            child_node = Node(parent=node, prompt=new_prompt)
            child_node.code = self.ai_provider.generate_code(child_node)
            node.add_child(child_node)

            return child_node

        new_node = []
        if node.parent is None:
            for base_variation in self.ai_provider.BASE_VARIATIONS:
                new_prompt = Prompt(
                    node.prompt.task, node.prompt.test_list, [], [base_variation]
                )

                child_node = add_variations(node, new_prompt)
                new_node.append(child_node)

            return new_node

        max_children = 3
        for _ in range(max_children):
            details = self.ai_provider.get_prompt_details(node.prompt)
            new_prompt = Prompt(
                node.prompt.task, node.prompt.test_list, node.prompt.errors, details
            )

            child_node = add_variations(node, new_prompt)
            new_node.append(child_node)

        return new_node

    def find_the_best_solution(self, task: str, task_id: str, test_list: list[str]) -> SolutionResult | None:
        prompt = Prompt(task, test_list, [], [])
        root = Node(parent=None, prompt=prompt)
        root.code = self.ai_provider.generate_code(root)
        queue = deque([root])

        best_solution = None
        best_score = 0

        while queue:
            current_node = queue.popleft()
            if current_node.depth() > self.max_depth:
                _LOGGER.debug(
                    "Skipping node with depth %d as it exceeds max_depth",
                    current_node.depth(),
                )
                continue

            score, errors = self.code_evaluator.evaluate_solution(
                current_node.code, test_list
            )
            current_node.prompt.errors = errors

            if score > best_score or best_score == 0:
                best_score = score
                best_solution = SolutionResult(task=task, code=current_node.code, score=score, errors=current_node.prompt.errors)
                _LOGGER.debug("New best score %d for task %s", score, task_id)

            if score == 100:
                _LOGGER.info("Found a perfect solution for task: %s", task_id)
                break

            if current_node.depth() < self.max_depth:
                children = self.expand(current_node)
                queue.extend(children)

        _LOGGER.info("Task %s solved with score: %d", task_id, score)
        return best_solution
