import os
import csv
from config.settings import Settings
from openai import OpenAI
from ai.openai_provider import OpenAIProvider
from ai.prompt_template import PromptTemplate
from evaluation.code_executor import CodeExecutor
from evaluation.code_evaluator import CodeEvaluator
from tot.three_of_thoughts import TreeOfThoughts
from utils.data_loader import DataLoader
from tabulate import tabulate
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

    def load_data(self) -> List[dict]:
        return DataLoader.load_mbpp(self.data_path)

    def process_data(self, data: List[dict]):
        for use_case in data:
            prompt = use_case["text"]
            test_list = use_case["test_list"]
            task_id = use_case["task_id"]
            result = self.tot.find_the_best_solution(prompt, task_id, test_list)
            self.results.append(result)

    def display_results(self):
        table_data = []
        for idx, result in enumerate(self.results):
            table_data.append([idx + 1, result.score])

        headers = ["Case #", "Score"]
        print(tabulate(table_data, headers, tablefmt="pretty"))

        self.save_results_as_csv('output')

    def save_results_as_csv(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        csv_file_path = os.path.join(output_dir, 'results.csv')
        
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Case #", "Task Description", "Code Solution", "Score"])

            for idx, result in enumerate(self.results):
                writer.writerow([
                    idx + 1,
                    result.task,
                    result.code,
                    result.score
                ])

        print(f"Results saved to {csv_file_path}")

    def run(self):
        data_mbpp = self.load_data()
        self.process_data(data_mbpp)
        self.display_results()


if __name__ == "__main__":
    api_key = Settings().OPENAI_API_KEY
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    app = CodeGenerationApp(api_key=api_key, data_path="datasets/mbpp.jsonl")
    app.run()
