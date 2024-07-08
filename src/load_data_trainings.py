import argparse
from openai import OpenAI
from typing import List
from config.settings import Settings
from db.session import get_db
from db.trainings import Trainings
from ai.openai_provider import OpenAIProvider
from ai.prompt_template import PromptTemplate
from utils.data_loader import DataLoader
from utils.logger import get_logger

logger = get_logger(__name__)


class LoadDataTrainings:
    def __init__(self, trainings: Trainings, ai_provider: OpenAIProvider):
        self.trainings = trainings
        self.ai_provider = ai_provider

    def generate_context(self, solution: str, test_list: list) -> str:
        """
        Generate a context string from the provided solution and test list.

        This method formats the solution and test list into a single string that
        includes the solution followed by the test list. The test list items are
        concatenated into a single string separated by newline characters.

        Args:
            solution (str): The code solution to be included in the context.
            test_list (list): A list of test cases related to the solution.

        Returns:
            str: A formatted string containing the solution and test list.
        """
        context = f"Solution:\n{solution}\n\nTest List:\n" + "\n".join(test_list)
        return context

    def process_csv_and_store(self, data: List[dict]):
        """
        Process a list of dictionaries containing task data and store it in the database.

        This method iterates through each item in the provided data list, checks if a
        training record with the same task ID already exists in the database, and if
        not, it generates an embedding, creates a context string, and stores the new
        training data in the database.

        Args:
            data (List[dict]): A list of dictionaries where each dictionary contains
            task data including 'task_id', 'text', 'code', and 'test_list'.
        """
        for item in data:
            task_id = item["task_id"]

            if self.trainings.get_training_by_task_id(task_id):
                logger.info(f"Training for task: {task_id} already exists. Skipping...")
                continue

            problem = item["text"]
            solution = item["code"]
            embedding = self.ai_provider.generate_embedding(
                problem, self.ai_provider.EMBEDDINGS_LLM
            )
            score = 0.0
            test_list = item["test_list"]
            context = self.generate_context(solution, test_list)
            self.trainings.store_training(
                task_id, problem, solution, embedding, score, context
            )
            logger.info(f"Stored training for problem: {problem}")

    def run(self, path: str):
        """
        Execute the process of loading data from a specified path and storing it in the database.

        This method loads the data from the specified CSV file path using the DataLoader,
        and then processes and stores the data in the database by calling the
        process_csv_and_store method.

        Args:
            path (str): The file path to the CSV file containing the task data.
        """
        data = DataLoader.load_mbpp(path)
        self.process_csv_and_store(data)


if __name__ == "__main__":
    api_key = Settings().OPENAI_API_KEY
    open_ai = OpenAI(api_key=api_key)
    prompt_template = PromptTemplate()
    ai_provider = OpenAIProvider(open_ai, prompt_template)

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=True, help="Path to the CSV file")
    args = parser.parse_args()

    db = next(get_db())
    trainings = Trainings(db)
    load_data_trainings = LoadDataTrainings(trainings, ai_provider)
    load_data_trainings.run(args.path)
