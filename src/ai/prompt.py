class Prompt:
    def __init__(self, task, test_list, errors=[], details=[]):
        self.task = task
        self.errors = errors
        self.test_list = test_list
        self.details = details
