import argparse
from injector import inject, Injector
from config.settings import Settings
from ai.openai_provider import OpenAIProvider
from evaluation.code_executor import CodeExecutor
from evaluation.code_evaluator import CodeEvaluator
from tot.three_of_thoughts import TreeOfThoughts
from utils.data_loader import DataLoader
from db.trainings import Trainings
from summarize_results import SummarizeResults
from dependency_container import DependencyContainer
from typing import List


class TrainModel:
    @inject
    def __init__(
        self,
        ai_provider: OpenAIProvider,
        code_executor: CodeExecutor,
        code_evaluator: CodeEvaluator,
        tot: TreeOfThoughts,
        trainings: Trainings,
        summarize_results: SummarizeResults,
    ):
        self.ai_provider = ai_provider
        self.code_executor = code_executor
        self.code_evaluator = code_evaluator
        self.tot = tot
        self.trainings = trainings
        self.summarize_results = summarize_results
        self.data_path = Settings().DATASET_PATH
        self.results = []

    def load_data(self) -> List[dict]:
        """
        Loads data from the specified data path.

        This method reads data from the file specified by the `data_path` attribute
        and returns it as a list of dictionaries.

        Returns:
            List[dict]: A list of dictionaries, where each dictionary represents
                        a data entry loaded from the data file.
        """
        return DataLoader.load_mbpp(self.data_path)

    def generate_context(self, code: str, score: float, errors: list) -> str:
        """
        Generates a descriptive context from a solution code, score, and list of errors.

        Args:
            code (str): The attempted solution code.
            score (float): The score assigned to the solution.
            errors (list): A list of errors found in the solution.

        Returns:
            str: A string containing the generated context, including the solution code,
                score, and formatted list of errors.
        """
        context = f"Tried solution: {code}\nScore: {score}"
        if errors:
            errors = [str(error) for error in errors]
            context += "\nErrors found in the tried solution:\n" + "\n".join(errors)

        return context

    def process_data(self, data: List[dict], lines: int = None):
        """
        Processes the provided data and optionally limits the number of lines processed.

        This method processes the input data, generates embeddings, stores data in the database,
        find a solution, and writes results to a CSV file. It iterates through the provided data and processes
        each entry. If the 'lines' parameter is specified, it limits the processing to the
        specified number of lines.

        Args:
            data (List[dict]): A list of dictionaries, where each dictionary represents
                            a data entry to be processed.
            lines (int, optional): The number of lines to process. If not specified, all
                                lines in the data will be processed.

        Returns:
            None
        """
        processed_count = 0

        for use_case in data:
            if lines and processed_count >= lines:
                break

            task_id = use_case["task_id"]
            prompt = use_case["text"]

            document = self.trainings.get_training_by_task_id(task_id)
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

            embedding = self.ai_provider.generate_embedding(
                prompt, self.ai_provider.EMBEDDINGS_LLM
            )
            new_context = self.generate_context(
                result.code, result.score, result.errors
            )

            new_solution = result.code
            if result.score != 100:
                new_solution = solution

            self.trainings.store_training(
                task_id, problem, new_solution, embedding, result.score, new_context
            )

            processed_count += 1

    def run(self, lines: int = None):
        """
        Executes the code generation process and optionally limits the number of lines processed.

        This method orchestrates the entire workflow of loading data, processing it,
        and displaying the results. If the 'lines' parameter is specified, it limits
        the processing to the specified number of lines.

        Args:
            lines (int, optional): The number of lines to process. If not specified,
                                all lines in the data will be processed.

        Returns:
            None
        """
        data_mbpp = self.load_data()
        self.process_data(data_mbpp, lines)
        self.summarize_results.display_results(self.results)


if __name__ == "__main__":
    api_key = Settings().OPENAI_API_KEY
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    parser = argparse.ArgumentParser(description="Run the TrainModel")
    parser.add_argument(
        "--lines", type=int, help="Number of lines to process from the dataset"
    )
    args = parser.parse_args()

    injector = Injector([DependencyContainer()])
    app = injector.get(TrainModel)
    app.run(lines=args.lines)
