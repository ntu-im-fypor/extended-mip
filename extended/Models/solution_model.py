# superclass of all solution models
from Models import Parameters

class SolutionModel:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters

    def run_and_solve(self):
        raise NotImplementedError
    def record_result(self):
        raise NotImplementedError