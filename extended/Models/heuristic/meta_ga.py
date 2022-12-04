from Models import Parameters, SolutionModel
from utils.generate_schedule import generate_schedule
from utils.common import cast_parameters_to_instance, calculate_objective_value
from utils.generate_population import generate_population
from utils.ga_crossover import ga_crossover
from utils.ga_mutation import ga_mutation
from utils.ga_selection import ga_selection
from utils.schedule_to_order import generate_shared_job_order, schedule_to_share_job_order_list
import numpy as np
import random
import copy
import math
import matplotlib.pyplot as plt

class MetaGAModel(SolutionModel):
    def __init__(self, parameters: Parameters):
        super().__init__(parameters)

    # interation number 待確定
    def run_and_solve(self, job_mutation_rate: int = 0.05, machine_mutation_rate: int = 0.05, population_num: int = 30, iteration_num: int = 6000, instance_num: int = 1):


        self.iter_best_obj = []
        # print("Running and solving using GAModel")

        instance = cast_parameters_to_instance(self.parameters)
        # print("Running and solving using GAModel")

        # Generate Population
        init_population = generate_population(self.parameters, population_num, instance_num)

        chosen_list = []
        for iter_num in range(iteration_num):
            # print("iter_num = ", iter_num)

            # Step 1: choose two solution
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

            for i in range(len(chosen_list)):
                chosen_list[i] = ga_mutation(chosen_list[i], job_mutation_rate, machine_mutation_rate, instance.JOBS_NUM, instance.MAX_MACHINES_NUM, iter_num, job_float_order ) # TODO: discuss probability

            for item in chosen_list:
                expand_item = np.expand_dims(item, axis=0)
                init_population = np.append(init_population, expand_item, axis=0)
            populations_obj = []
            for solution in init_population:
                cur_share_job_order_list = schedule_to_share_job_order_list(solution, instance.MAX_MACHINES_NUM)
                cur_order_list = generate_shared_job_order(solution, instance.MAX_MACHINES_NUM, instance.MACHINES_NUM)
                cur_obj = generate_schedule(cur_share_job_order_list, cur_order_list, instance)
                populations_obj.append(cur_obj)

            # find the two worst index and delete them from init_population
            for _ in range(2):
                max_value_index = populations_obj.index(max(populations_obj))
                del populations_obj[max_value_index]
                init_population = np.delete(init_population, max_value_index, axis=0)
            # get current best solution
            self.iter_best_obj.append(min(populations_obj))
            if(iter_num == 0):
                self.init_obj = min(populations_obj)



        # Choose 1 best solution
        populations_obj = []
        for solution in init_population:
            cur_share_job_order_list = schedule_to_share_job_order_list(solution, instance.MAX_MACHINES_NUM)
            cur_order_list = generate_shared_job_order(solution, instance.MAX_MACHINES_NUM, instance.MACHINES_NUM)
            cur_obj = generate_schedule(cur_share_job_order_list, cur_order_list, instance)
            populations_obj.append(cur_obj)
        min_value_index = populations_obj.index(min(populations_obj))
        # store best schedule
        self.best_schedule = init_population[min_value_index]
        # store best share job order




    def record_result(self):
        # print("self.best_schedule = ", self.best_schedule)
        # print("Recording result using GAModel")
        instance = cast_parameters_to_instance(self.parameters)
        # print("Instance after transformation:")
        # print_instance(instance)
        share_job_order_list = schedule_to_share_job_order_list(self.best_schedule, instance.MAX_MACHINES_NUM)
        order_list = generate_shared_job_order(self.best_schedule, instance.MAX_MACHINES_NUM, instance.MACHINES_NUM)
        schedule_obj = generate_schedule(share_job_order_list, order_list, instance)
        # print("Schedule objective value: ", schedule_obj)
        # print("objective value for each iteration")
        # print(self.iter_best_obj)
        # plt.plot(self.iter_best_obj,'ro--', linewidth=2, markersize=6)  # 簡化後的程式碼
        # plt.show()
        return schedule_obj, share_job_order_list, order_list, self.init_obj

