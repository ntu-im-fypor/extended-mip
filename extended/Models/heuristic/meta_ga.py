from Models import Parameters, SolutionModel
from utils.schedule_objective_value_calculation import calculate_objective_value, transform_parameters_to_instance, print_instance
from utils.generate_population import generate_population
from utils.ga_crossover import ga_crossover
from utils.ga_mutation import ga_mutation
from utils.ga_selection import ga_selection
import numpy as np
import random
class MetaGAModel(SolutionModel):
    def __init__(self, parameters: Parameters):
        super().__init__(parameters)

    # interation number 待確定
    def run_and_solve(self, population_num: int = 2, iteration_num: int = 60):
        print("Running and solving using GAModel")

        instance = transform_parameters_to_instance(self.parameters)
        print("Running and solving using GAModel")

        # Generate Population
        init_population = generate_population(self.parameters, population_num)
        chosen_list = []
        for iter_num in range(iteration_num):
            # Step 1: choose two solution
            chosen_list = ga_selection(init_population, instance, 'binary')
            # Step 2: do crossover

            # Step a. Randomly Select job and machine crossover point
            job_point = random.randint(0, instance.JOBS_NUM)
            machine_point = random.randint(0, instance.MAX_MACHINE_NUM)
            chosen_list = ga_crossover(chosen_list, instance.JOBS_NUM, instance.MACHINES_NUM, job_point, machine_point)
            # Step 3: do mutation
            chosen_list = ga_mutation(chosen_list, 0.01, 0.01, instance.JOBS_NUM, instance.MAX_MACHINE_NUM) # TODO: discuss probability

            print(iter_num, " = ", chosen_list)
            print("========")
            # Step 4: update solution (delete the two original one) # TODO:

            # Step a. Calculate obj of the whole population

            # Step b. Calculation obj of the two population

        # Choose 1 best solution


    def record_result(self):
        print("Recording result using GAModel")
        example_schedule = [[1.2, 1.3, 2.5, 0, 2.3], [1.2, 1.5, 1.3, 1.1, 0]]
        instance = transform_parameters_to_instance(self.parameters)
        print("Instance after transformation:")
        print_instance(instance)
        schedule_obj = calculate_objective_value(example_schedule, instance)
        print("Schedule objective value: ", schedule_obj)
