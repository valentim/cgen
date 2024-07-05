from .code_executor import CodeExecutor


class CodeEvaluator:
    def __init__(self, code_executor: CodeExecutor):
        self.code_executor: CodeExecutor = code_executor

    def evaluate_solution(self, code, test_list):
        expected_results = len(test_list)
        errors = []
        results = 0
        for test_case in test_list:
            is_sucess, error = self.code_executor.execute_test(code, test_case)
            if not is_sucess:
                errors.append(error)
                continue

            results += 1

        score = (results / expected_results) * 100
        return (score, errors)
