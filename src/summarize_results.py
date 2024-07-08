import os
import csv
from evaluation.solution_result import SolutionResult
from db.session import get_db
from db.trainings import get_all_trainings
from tabulate import tabulate

class SummarizeResults:
    def __init__(self):
        self.db = next(get_db())

    def process_data(self):
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        csv_file_path = os.path.join(output_dir, 'results.csv')

        results = []
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Case #", "Task Description", "Code Solution", "Score"])

        data = get_all_trainings(self.db)
        for use_case in data:
            task_id = use_case.task_id
            problem = use_case.problem

            score = use_case.score
            solution = use_case.solution
   
            results.append(SolutionResult(task=problem, code=solution, score=score))

            with open(csv_file_path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([
                    task_id,
                    problem,
                    solution,
                    score
                ])
            
        return results


    def display_results(self, results):
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
        results = self.process_data()
        self.display_results(results)


if __name__ == "__main__":
    summarize = SummarizeResults()
    summarize.run()
