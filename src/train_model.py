import argparse
from config.settings import Settings
from openai import OpenAI
from ai.openai_provider import OpenAIProvider
from ai.prompt_template import PromptTemplate
from evaluation.code_executor import CodeExecutor
from evaluation.code_evaluator import CodeEvaluator
from evaluation.solution_result import SolutionResult
from tot.three_of_thoughts import TreeOfThoughts
from utils.data_loader import DataLoader
from db.session import get_db
from db.trainings import store_training, get_training_by_task_id
from summarize_results import SummarizeResults
from typing import List

class CodeGenerationApp:
    def __init__(self, api_key: str, data_path: str):
        self.api_key = api_key
        self.data_path = data_path
        self.results = []

        open_ai = OpenAI(api_key=api_key)
        prompt_template = PromptTemplate()
        self.ai_provider = OpenAIProvider(open_ai, prompt_template)
        self.code_executor = CodeExecutor()
        self.code_evaluator = CodeEvaluator(self.code_executor)
        self.tot = TreeOfThoughts(self.ai_provider, self.code_evaluator, max_depth=Settings().THREE_MAX_DEPTH)
        self.db = next(get_db())
        self.sumarize_results = SummarizeResults()

    def load_data(self) -> List[dict]:
        return DataLoader.load_mbpp(self.data_path)

    def generate_context(self, code: str, score: float, errors: list) -> str:
        """Generate context from solution and test list."""
        context = f"Tried solution: {code}\nScore: {score}"
        if errors:
            errors = [str(error) for error in errors]
            context += f"\nErrors found in the tried solution:\n" + "\n".join(errors)

        return context

    def process_data(self, data: List[dict], lines: int = None):
        processed_count = 0

        for use_case in data:
            if lines and processed_count >= lines:
                break

            task_id = use_case["task_id"]
            prompt = use_case["text"]

            document = get_training_by_task_id(self.db, task_id)
            score = document.score
            problem = document.problem
            context = document.context
            solution = document.solution
            if score == 100:
                continue

            if solution:
                prompt = f"{prompt}\n\nAdditional context: {solution}\n\n{context}"

            test_list = use_case["test_list"]
            result = self.tot.find_the_best_solution(prompt, task_id, test_list)
            self.results.append(result)


            embedding = self.ai_provider.generate_embedding(prompt, self.ai_provider.EMBEDDINGS_LLM)
            new_context = self.generate_context(result.code, result.score, result.errors)
            
            new_solution = result.code
            if result.score != 100:
                new_solution = solution

            store_training(self.db, task_id, problem, new_solution, embedding, result.score, new_context)

            processed_count += 1


    def run(self, lines: int = None):
        data_mbpp = self.load_data()
        self.process_data(data_mbpp, lines)
        self.sumarize_results.display_results(self.results)


if __name__ == "__main__":
    api_key = Settings().OPENAI_API_KEY
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    parser = argparse.ArgumentParser(description="Run the Code Generation App")
    parser.add_argument("--lines", type=int, help="Number of lines to process from the dataset")
    args = parser.parse_args()

    app = CodeGenerationApp(api_key=api_key, data_path="datasets/mbpp.jsonl")
    app.run(lines=args.lines)
