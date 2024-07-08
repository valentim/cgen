class SolutionResult:
    def __init__(self, task: str, code: str, score: float, errors: list[str] = []):
        self.task = task
        self.code = code
        self.score = score
        self.errors = errors

    def __repr__(self):
        return f"SolutionResult(task={self.task}, code={self.code}, score={self.score}, errors={self.errors})"
