import os
import csv
from evaluation.solution_result import SolutionResult
from db.session import get_db
from db.trainings import Trainings
from tabulate import tabulate


class SummarizeResults:
    def __init__(self, trainings: Trainings):
        self.trainings = trainings

    def process_data(self):
        """
        Processes the stored training data, generates a results CSV file, and returns the results.

        This method performs the following steps:
        1. Creates an output directory if it doesn't already exist.
        2. Initializes a CSV file with headers for storing the results.
        3. Retrieves all training data from the database.
        4. Iterates through the training data, appending each result to the results list and writing it to the CSV file.
        5. Returns the list of results.

        The CSV file includes the following columns:
        - Case #: The unique identifier of the task.
        - Task Description: The description of the task/problem.
        - Code Solution: The code solution provided for the task.
        - Score: The score assigned to the solution.

        Returns:
            List[SolutionResult]: A list of SolutionResult objects containing the processed training data.
        """
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        csv_file_path = os.path.join(output_dir, "results.csv")

        results = []
        with open(csv_file_path, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Case #", "Task Description", "Code Solution", "Score"])

        data = self.trainings.get_all_trainings()
        for use_case in data:
            task_id = use_case.task_id
            problem = use_case.problem

            score = use_case.score
            solution = use_case.solution

            results.append(SolutionResult(task=problem, code=solution, score=score))

            with open(csv_file_path, mode="a", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([task_id, problem, solution, score])

        return results

    def display_results(self, results):
        """
        Displays the summary of test results in a formatted table.

        This method performs the following steps:
        1. Initializes a list to hold the table data.
        2. Calculates the total number of tested cases.
        3. Sums up the scores of all the results.
        4. Calculates the overall score by averaging the total scores and rounding to two decimal places.
        5. Appends the total tested cases and overall score to the table data.
        6. Prints the table with headers using the 'tabulate' library.

        Args:
            results (List[SolutionResult]): A list of SolutionResult objects containing the test results.
        """
        table_data = []
        overall_score = 0

        total_tested_cases = len(results)
        for result in results:
            overall_score += result.score

        overall_score = round(overall_score / len(results), 2) if results else 0
        table_data.append([total_tested_cases, overall_score])

        headers = ["Total Tested Cases", "Overall Score"]
        print(tabulate(table_data, headers, tablefmt="pretty"))

    def run(self):
        """
        Executes the main workflow of the code generation application.

        This method performs the following steps:
        1. Processes the data to generate results.
        2. Displays the results in a formatted table.

        The `process_data` method retrieves and processes the training data, 
        generating a list of SolutionResult objects. The `display_results` 
        method then takes these results and displays them in a table format.

        Returns:
            None
        """
        results = self.process_data()
        self.display_results(results)


if __name__ == "__main__":
    db = next(get_db())
    trainings = Trainings(db)
    summarize = SummarizeResults(trainings)
    summarize.run()
