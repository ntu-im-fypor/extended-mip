from Models import Parameters, SolutionModel
from utils.schedule_objective_value_calculation import calculate_objective_value, transform_parameters_to_instance, print_instance
from utils.generate_population import generate_population
from utils.ga_crossover import ga_crossover
from utils.ga_mutation import ga_mutation
from utils.ga_selection import ga_selection
from utils.generate_shared_job_order import generate_shared_job_order
import numpy as np
import random
import copy
import math
class MetaGAModel(SolutionModel):
    def __init__(self, parameters: Parameters):
        super().__init__(parameters)

    # interation number 待確定
    def run_and_solve(self, population_num: int = 2, iteration_num: int = 60):
        print("Running and solving using GAModel")

        instance = transform_parameters_to_instance(self.parameters)
        print("Running and solving using GAModel")

        shared_job_order_list = generate_shared_job_order(instance)
        # print("shared_job_order_list")
        # print(shared_job_order_list)

        # Generate Population
        init_population = generate_population(self.parameters, population_num, shared_job_order_list)

        # print("finish init. population generation")
        chosen_list = []
        for iter_num in range(iteration_num):


            # Step 1: choose two solution
            # TODO: 補利用 objective value 的情況
            chosen_list = ga_selection(init_population, instance, 'binary')

            # transfer chosen_list from list of array to list of list
            for i in range(len(chosen_list)):
                chosen_list[i] = chosen_list[i].tolist()

            # Step 2: do crossover

            # Step a. Randomly Select job and machine crossover point
            job_point = random.randint(0, instance.JOBS_NUM-1)
            machine_point = random.randint(0, instance.MAX_MACHINES_NUM-1)
            chosen_list = ga_crossover(chosen_list, instance.JOBS_NUM, instance.MAX_MACHINES_NUM, job_point, machine_point)

            # Step 3: do mutation
            job_float_order = []
            for i in chosen_list[0][0][:instance.JOBS_NUM]:
                job_float_order.append(math.modf(i)[0])

            # print("chosen_list = ", chosen_list)
            # print("chosen_list[0] = ", chosen_list[0])
            for i in range(len(chosen_list)):
                # print("chosen_list[i] = ", chosen_list[i])
                chosen_list[i] = ga_mutation(chosen_list[i], 0.01, 0.01, instance.JOBS_NUM, instance.MAX_MACHINES_NUM, iter_num, job_float_order ) # TODO: discuss probability

            '''
            1. 計算所有 population & chosen_list 的 objective value
                a. 從 table 計算出順序 ([0][0][:job_num]小數點從小排到大)
                b. 抓出表現最差的兩個population 中的 item 以及其對應的 index
                c. 跟新的兩個進行比較 -> 如果比較差就被 replace
            '''
            for item in chosen_list:
                expand_item = np.expand_dims(item, axis=0)
                init_population = np.append(init_population, expand_item, axis=0)
            populations_obj = []
            for _ in init_population:
                # TODO: replace with real obj
                cur_obj = random.randint(0, 10000000)
                populations_obj.append(cur_obj)

            # find the two worst index and delete them from init_population
            for _ in range(2):
                min_value_index = populations_obj.index(min(populations_obj))
                del populations_obj[min_value_index]
                init_population = np.delete(init_population, min_value_index, axis=0)

            # print("length of init_population = ", len(init_population))
        # Choose 1 best solution
        populations_obj = []
        for _ in init_population:
            # TODO: replace with real obj
            cur_obj = random.randint(0, 10000000)
            populations_obj.append(cur_obj)
        max_value_index = populations_obj.index(max(populations_obj))
        self.best_schedule = init_population[max_value_index]




    def record_result(self):
        print("self.best_schedule = ", self.best_schedule)
        print("Recording result using GAModel")
        example_schedule = [[1.2, 1.3, 2.5, 0, 2.3], [1.2, 1.5, 1.3, 1.1, 0]]
        instance = transform_parameters_to_instance(self.parameters)
        print("Instance after transformation:")
        # print_instance(instance)
        schedule_obj = calculate_objective_value(self.best_schedule, instance)
        print("Schedule objective value: ", schedule_obj)
