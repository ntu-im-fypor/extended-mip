from Models import Parameters, SolutionModel
from utils.schedule_objective_value_calculation import calculate_objective_value, transform_parameters_to_instance, print_instance

class MetaPSOModel(SolutionModel):
    def __init__(self, parameters: Parameters):
        super().__init__(parameters)

    def run_and_solve(self):
        print("Running and solving using PSOModel")

    def record_result(self):
        print("Recording result using PSOModel")
        example_schedule = [[1.2, 1.3, 2.5, 0, 2.3], [1.2, 1.5, 1.3, 1.1, 0]]
        instance = transform_parameters_to_instance(self.parameters)
        print("Instance after transformation:")
        print_instance(instance)
        schedule_obj = calculate_objective_value(example_schedule, instance)
        print("Schedule objective value: ", schedule_obj)