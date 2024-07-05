class SolutionResult:
    def __init__(self, task: str, code: str, score: float):
        self.task = task
        self.code = code
        self.score = score

    def __repr__(self):
        return f"SolutionResult(task={self.task}, code={self.code}, score={self.score})"
