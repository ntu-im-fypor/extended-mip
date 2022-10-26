from Models import Parameters, SolutionModel

class HeuristicModel(SolutionModel):
    def __init__(self, parameters: Parameters):
        super().__init__(parameters)

    def run_and_solve(self):
        print("Running and solving using HeuristicModel")

    def record_result(self):
        print("Recording result using HeuristicModel")