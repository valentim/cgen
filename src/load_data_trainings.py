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


def generate_context(solution: str, test_list: list) -> str:
    """Generate context from solution and test list."""
    context = f"Solution:\n{solution}\n\nTest List:\n" + "\n".join(test_list)
    return context


def process_csv_and_store(
    data: List[dict], trainings: Trainings, ai_provider: OpenAIProvider
):
    """Process CSV file, generate embeddings and store data in the database."""
    for item in data:
        task_id = item["task_id"]

        if trainings.get_training_by_task_id(task_id):
            logger.info(f"Training for task: {task_id} already exists. Skipping...")
            continue

        problem = item["text"]
        solution = item["code"]
        embedding = ai_provider.generate_embedding(problem, ai_provider.EMBEDDINGS_LLM)
        score = 0.0
        test_list = item["test_list"]
        context = generate_context(solution, test_list)
        trainings.store_training(task_id, problem, solution, embedding, score, context)
        logger.info(f"Stored training for problem: {problem}")


def main():
    api_key = Settings().OPENAI_API_KEY
    open_ai = OpenAI(api_key=api_key)
    prompt_template = PromptTemplate()
    ai_provider = OpenAIProvider(open_ai, prompt_template)

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=True, help="Path to the CSV file")
    args = parser.parse_args()

    db = next(get_db())
    trainings = Trainings(db)
    data = DataLoader.load_mbpp(args.path)
    process_csv_and_store(data, trainings, ai_provider)


if __name__ == "__main__":
    main()
