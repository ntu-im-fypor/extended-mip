from itertools import combinations
import json
from Models import Parameters, SolutionModel
from utils.common import cast_parameters_to_instance
from utils.generate_schedule import generate_schedule
from utils.ga_order_gen_pop import ga_order_gen_pop
from utils.ga_order_crossover import ga_order_crossover
import utils.ours_utils as utils
import numpy as np
import pandas as pd
import copy
import random
import time

class GreedyModel(SolutionModel):
    def __init__(
            self, 
            parameters: Parameters, 
            use_gurobi_order = False, 
            use_ga = False, 
            maintenance_choice_percentage: float = 0.5, 
            file_path: str = None, 
            instance_num: int = 0, 
            job_weight_choice: str = "WEDD",
            merge_step3_to_step2: bool = True,
            combine_maint_and_swap: bool = True
        ):
        """
        Initialize the model with the parameters and the maintenance choice percentage
        #### Parameters
        - `parameters`: the parameters of the problem
        - `maintenance_choice_percentage`: the percentage of the maintenance choice, that is, after calculating maintenance benefit, we choose first `maintenance_choice_percentage` of the machines to do maintenance
        - `file_path`: the file path to store the result
        - `instance_num`: the instance number of the problem
        - `job_weight_choice`: the choice of the job weight method, can be "WEDD", "EDD", or "SPT"
        """
        super().__init__(parameters)
        if file_path is None:
            print("No file path specified!")
            return
        self.use_gurobi_order = use_gurobi_order
        self.use_ga = use_ga
        self.file_path = file_path
        self.maintenance_choice_percentage = maintenance_choice_percentage
        self.instance_num = instance_num
        self.job_weight_choice = job_weight_choice
        self.merge_step3_to_step2 = merge_step3_to_step2
        self.combine_maint_and_swap = combine_maint_and_swap

    def run_and_solve(self):
        """
        Run and solve the problem using Greedy, and then store the output schedule into self.schedule.
        Then calculate the objective value of the schedule using record_result()
        """
        print("Running and solving using GreedyModel")
        start_time = time.time()
        # run initial job listing with maintenance
        initial_job_listing = None
        # get the shared job order for the initial job listing
        initial_shared_job_order = list[int]
        if self.use_gurobi_order:
            initial_shared_job_order = utils.get_shared_job_order_from_Gurobi(self.instance_num)
            initial_job_listing = self.generate_initial_job_listing(initial_shared_job_order)
            initial_job_listing = self._sort_schedule_with_shared_job_order(initial_shared_job_order, initial_job_listing)
        else:
            initial_job_listing = self.generate_initial_job_listing()
            initial_shared_job_order = utils.get_shared_job_order(self.job_weight_list)
        # start to consider the best maintenance position for each machine
        initial_job_schedule, initial_best_objective_value = self._decide_best_maintenance_position(initial_job_listing, initial_shared_job_order, np.inf)
        print(f"Initial Objective Value: {initial_best_objective_value}")
        print(f"Initial Shared Job Order: {initial_shared_job_order}")
        print(f"Initial Schedule: {initial_job_schedule}")
        print("=====")

        # store the initial results for final reference (before swapping shared job order)
        self.initial_result = {
            "schedule": initial_job_schedule,
            "objective_value": initial_best_objective_value,
            "shared_job_order": initial_shared_job_order
        }

        # try swapping shared job order and adjusting maintenance position to see if we can get a better solution
        best_objective_value = initial_best_objective_value
        best_job_schedule = initial_job_schedule
        best_shared_job_order = initial_shared_job_order
        
        # run merge swap and maint first
        for _ in range(self.parameters.Number_of_Jobs):
            # mutate best job schedule inside the function
            cur_best_shared_job_order, cur_best_obj = self._try_swapping_shared_job_order(best_job_schedule, best_shared_job_order, best_objective_value)
            if cur_best_obj < best_objective_value:
                # use best swapped order to generate a new schedule
                best_shared_job_order = cur_best_shared_job_order
                best_objective_value = cur_best_obj
        print(f"Merge Verison Objective Value: {best_objective_value}")
        print(f"Merge Verison Shared Job Order: {best_shared_job_order}")
        print(f"Merge Verison Schedule: {best_job_schedule}")
        print("=====")

        # store the results for final reference (merge version)
        self.merge_result = {
            "schedule": best_job_schedule,
            "objective_value": best_objective_value,
            "shared_job_order": best_shared_job_order
        }

        # switch merge_swap to false to separately run two stages
        self.combine_maint_and_swap = False
        best_objective_value_no_merge = initial_best_objective_value
        best_job_schedule_no_merge = initial_job_schedule
        best_shared_job_order_no_merge = initial_shared_job_order
        has_improved = False
        for _ in range(self.parameters.Number_of_Jobs):
            # try swapping shared job order to see if we can get a better solution
            cur_best_shared_job_order, cur_best_obj = self._try_swapping_shared_job_order(best_job_schedule_no_merge, best_shared_job_order_no_merge, best_objective_value_no_merge)
            if cur_best_obj < best_objective_value_no_merge:
                # use best swapped order to generate a new schedule
                best_shared_job_order_no_merge = cur_best_shared_job_order
                best_job_schedule_no_merge = self._sort_schedule_with_shared_job_order(best_shared_job_order_no_merge, best_job_schedule_no_merge)
                best_objective_value_no_merge = cur_best_obj
            # try adjusting maintenance position to see if we can get a better solution
            cur_best_schedule, cur_best_obj = self._decide_best_maintenance_position(best_job_schedule_no_merge, best_shared_job_order_no_merge, best_objective_value_no_merge)
            if cur_best_obj < best_objective_value_no_merge:
                best_job_schedule_no_merge = cur_best_schedule
                best_objective_value_no_merge = cur_best_obj
                has_improved = True
            else:
                has_improved = False
            if not has_improved:
                break

        print(f"No Merge Version Objective Value: {best_objective_value_no_merge}")
        print(f"No Merge Version Shared Job Order: {best_shared_job_order_no_merge}")
        print(f"No Merge Version Schedule: {best_job_schedule_no_merge}")
        print("=====")

        print("Time before GA:", time.time() - start_time)
        print("=====")

        # store the results for final reference (no merge version)
        self.no_merge_result = {
            "schedule": best_job_schedule_no_merge,
            "objective_value": best_objective_value_no_merge,
            "shared_job_order": best_shared_job_order_no_merge,
            "greedy_time": time.time() - start_time
        }

        # if not self.merge_step3_to_step2:
        #     best_job_schedule, best_objective_value = self._try_swapping_two_jobs_on_same_stage(best_job_schedule, best_shared_job_order, best_objective_value)

        # run ga after heuristic, using WEDD job order, best job order by heuristic, and a randomly generated population
        if self.use_ga:
            population_num = 30
            pick_pop_method = 2 # 1 if weight is [pop_num, pop_num - 1, ..., 1] and 2 if weight is the objective value
            # generate initial population
            ga_int_pop = ga_order_gen_pop(self.parameters.Number_of_Jobs, self.initial_result['shared_job_order'], self.merge_result['shared_job_order'], self.no_merge_result['shared_job_order'], population_num)
            # list of dictionaries, with schedule, objective_value, shared_job_order
            ga_pop = []
            # calculate and record objective value of each order
            for i in range(len(ga_int_pop)):
                job_listing = self.generate_initial_job_listing(ga_int_pop[i])
                job_schedule, objective_value = self._decide_best_maintenance_position(job_listing, ga_int_pop[i], np.inf)
                pop = {
                    "schedule": job_schedule,
                    "objective_value": objective_value,
                    "shared_job_order": ga_int_pop[i]
                }
                ga_pop.append(pop)
            ga_pop = sorted(ga_pop, key=lambda d: d['objective_value'])
            # run ga for 300 iterations
            for i in range(300):
                if ga_pop[0]['objective_value'] == 0:
                    break
                # random choose two in the population to be parents for crossover
                weight_list = []
                if pick_pop_method == 1:
                    weight_list = [x+1 for x in list(range(population_num))]
                    weight_list.reverse()
                elif pick_pop_method == 2:
                    weight_list = [1 / x["objective_value"] for x in ga_pop]
                r1 = random.choices(list(range(population_num)), weights=weight_list, k=1)
                r2 = random.choices(list(range(population_num)), weights=weight_list, k=1)
                while r2 == r1:
                    r2 = random.choices(list(range(population_num)), weights=weight_list, k=1)
                parent = [ga_pop[r1[0]]["shared_job_order"], ga_pop[r2[0]]["shared_job_order"]]
                child = ga_order_crossover(parent)
                for j in range(len(child)):
                    tmp_job_listing = self.generate_initial_job_listing(child[j])
                    tmp_job_schedule, tmp_objective_value = self._decide_best_maintenance_position(tmp_job_listing, child[j], np.inf)
                    pop = {
                        "schedule": tmp_job_schedule,
                        "objective_value": tmp_objective_value,
                        "shared_job_order": child[j]
                    }
                    ga_pop.append(pop)
                ga_pop = sorted(ga_pop, key=lambda d: d['objective_value'])
                ga_pop.pop()
                ga_pop.pop()
            # find best objective value and compare with the objective value before ga
            current_best_index = min(range(len(ga_pop)), key=lambda k: ga_pop[k]['objective_value'])
            current_best_value = ga_pop[current_best_index]["objective_value"]
            if current_best_value < best_objective_value:
                best_objective_value = ga_pop[current_best_index]["objective_value"]
                best_shared_job_order = ga_pop[current_best_index]["shared_job_order"]
                best_job_schedule = ga_pop[current_best_index]["schedule"]
                print(f"GA Objective Value: {best_objective_value}")
                print(f"GA Shared Job Order: {best_shared_job_order}")
                print(f"GA Schedule: {best_job_schedule}")
                print("=====")
            else:
                print("Used GA but no improvement:(")
                print("=====")

        # store the best schedule
        self.final_result = {
            "schedule": best_job_schedule,
            "objective_value": best_objective_value,
            "shared_job_order": best_shared_job_order
        }
    def _setup(self):
        """
        Setup the data for the model
        """
        self.maintenance_choice = utils.get_maintenance_choice(self.parameters, self.maintenance_choice_percentage)
        self.real_production_time_matrix = utils.get_real_production_time_matrix(self.parameters, self.maintenance_choice)
        if self.job_weight_choice == "WEDD":
            self.job_weight_list = utils.get_WEDD_list(self.parameters)
        elif self.job_weight_choice == "EDD":
            self.job_weight_list = utils.get_EDD_list(self.parameters)
        elif self.job_weight_choice == "SPT":
            self.job_weight_list = utils.get_SPT_list(self.parameters, self.real_production_time_matrix)
        # self.average_machine_time_for_each_stage = utils.get_average_machine_time_for_each_stage(self.parameters, self.real_production_time_matrix, 0, 1)
        self.average_machine_time_for_each_stage = np.zeros(self.parameters.Number_of_Stages)
    def generate_initial_job_listing(self, shared_job_order: list[int] = None) -> list[list]:
        """
        Run the initial job listing part\n
        it will return the initial job listing schedule indicating the job order\n
        the shape follows the input format of generate_schedule function written by Hsiao-Li Yeh
        #### Parameters
        - `shared_job_order`: the shared job order where job index starts from 1, if not provided, it will use WEDD list to generate the shared job order
        """

        # setup
        self._setup()

        # first create a 3d list to store the job order for every machine in every stage the 3-th dimension is default to an empty list
        job_order_list = []
        for i in range(self.parameters.Number_of_Stages):
            job_order_list.append([])
            for _ in range(self.parameters.Number_of_Machines[i]):
                job_order_list[i].append([])

        # generate the shared job order
        current_job_priority = {}
        if shared_job_order is None:
            current_job_priority = self._generate_shared_job_order_dict_from_WEDD()
        else:
            for i in range(len(shared_job_order)):
                current_job_priority[shared_job_order[i] - 1] = i
        
        # current machine time for every machine is default to unfinished production time
        current_machine_time = copy.deepcopy(self.parameters.Unfinished_Production_Time)

        # for each stage, we calculate the largest production time difference for each job on different machines
        # larger production time difference means we should schedule the job first
        for i in range(self.parameters.Number_of_Stages):
            production_difference_list = [] # store production time difference for each job, every element is a tuple (job index, production time difference)
            machine_num = self.parameters.Number_of_Machines[i]
            for k in range(self.parameters.Number_of_Jobs):
                production_difference_list.append((k, max(self.real_production_time_matrix[i, :machine_num, k]) - min(self.real_production_time_matrix[i, :machine_num, k])))
            production_difference_list.sort(key=lambda x: x[1], reverse=True) # sort the list by production time difference, descending order
            # start to schedule the job onto the machine
            for job_index, _ in production_difference_list: # here the job index starts from 0, after computing we need to add 1 to the final job listing
                # first find the machine with smallest production time for this job
                best_machine_idx = np.argmin(self.real_production_time_matrix[i, :machine_num, job_index])
                # if schedule the job onto this machine will make current machine time exceed average machine time on this stage, then we need to schedule the job onto another machine
                if current_machine_time[i, best_machine_idx] + self.real_production_time_matrix[i, best_machine_idx, job_index] > self.average_machine_time_for_each_stage[i]:
                    # we try to find another machine that have smallest current machine time
                    secondary_machine_idx = 0
                    smallest_current_machine_time = current_machine_time[i, 0] + self.real_production_time_matrix[i, 0, job_index]
                    # calculate the current machine time for all machines on this stage to find the machine with smallest current machine time
                    for j in range(1, machine_num):
                        current_machine_time_for_this_machine = current_machine_time[i, j] + self.real_production_time_matrix[i, j, job_index]
                        if current_machine_time_for_this_machine < smallest_current_machine_time:
                            secondary_machine_idx = j
                            smallest_current_machine_time = current_machine_time_for_this_machine
                    best_machine_idx = secondary_machine_idx
                # schedule the job onto the machine
                job_order_list[i][best_machine_idx].append((job_index, current_job_priority[job_index]))
                # update the current machine time
                current_machine_time[i, best_machine_idx] += self.real_production_time_matrix[i, best_machine_idx, job_index]

        # sort the job order for each machine in each stage, the order should follow the current job priority
        for i in range(self.parameters.Number_of_Stages):
            for j in range(self.parameters.Number_of_Machines[i]):
                job_order_list[i][j].sort(key=lambda x: x[1])
        # now we have the initial job listing, we need to flatten the list
        job_order_list_flatten = []
        for i in range(self.parameters.Number_of_Stages):
            for j in range(self.parameters.Number_of_Machines[i]):
                # if machine j has maintenance, we need to add a 'M' to the head of the job order list for this machine
                job_order_for_this_machine = []
                if self.maintenance_choice[i, j] == 1:
                    job_order_for_this_machine.append('M')
                for job_index, _ in job_order_list[i][j]:
                    job_order_for_this_machine.append(job_index + 1)
                if self.maintenance_choice[i, j] == 0:
                    job_order_for_this_machine.append('M')
                job_order_list_flatten.append(job_order_for_this_machine)
        # complete the initial job listing
        return job_order_list_flatten

    def _generate_shared_job_order_dict_from_WEDD(self) -> dict:
        """
        Generate the shared job order from WEDD list. It will return a dictionary\n
        `Key`: job index, `Value`: job priority index (the smaller the index, the higher the priority)
        """
        current_job_priority = {}
        current_jobs_info = []
        for k in range(self.parameters.Number_of_Jobs):
            current_jobs_info.append((k, self.job_weight_list[k]))
        # sort the current jobs info by the WEDD
        current_jobs_info.sort(key=lambda x: x[1]) # first shared job order is sorted by WEDD, the lower the WEDD, the higher the priority
        # keep this information in a dictionary
        priority_index = 0
        for job_index, _ in current_jobs_info:
            current_job_priority[job_index] = priority_index
            priority_index += 1
        return current_job_priority

    def _decide_best_maintenance_position(self, job_order_on_machines: list[list], shared_job_order: list[int], initial_best_obj: float) -> tuple[list[list], float]:
        """
        Decide the best maintenance position for each machine on each stage\n
        For every machine with maintenance, we will try to find the best position for the maintenance\n
        Return a list of list, each list indicates the job order for each machine on each stage and the best objective value for this job order
        #### Parameters\n
        `job_order_on_machines`: the job order on machines for each stage, it should be a list of list\n
        `shared_job_order`: the shared job order, it should be a list, every element is a job index
        `initial_best_obj`: the initial best objective value
        """

        # do a deep copy of the job order on machines
        instances = cast_parameters_to_instance(self.parameters)
        job_order_on_machines_copy = copy.deepcopy(job_order_on_machines)
        best_objective_value = initial_best_obj
        # calculate the number of machines with maintenance
        machines_with_maintenance_num = len(job_order_on_machines)

        accumulated_no_improvement_count = 0
        # while True: # stopping crietria: no improvement for the number of machines with maintenance
        #     is_best_schedule_found = False
        for machine_index, job_order in enumerate(job_order_on_machines_copy):
            # if the job order contains 'M', it means this machine has maintenance, so we need to find the best position for the maintenance
            if 'M' in job_order:
                has_improved_on_this_machine = False
                # do a deep copy of the job order
                job_order_copy = copy.deepcopy(job_order)
                best_job_order_on_this_machine = copy.deepcopy(job_order)
                # first we get the job order list without 'M', and insert 'M' into every possible position to find the best position
                for i in range(len(job_order_copy)):
                    job_order_copy.remove('M')
                    job_order_copy.insert(i, 'M')
                    # replace the job order on this machine with the new job order
                    job_order_on_machines_copy[machine_index] = job_order_copy
                    # calculate the objective value for this job order under the situation that other machines maintain the same job order
                    cur_objective_value = generate_schedule(shared_job_order, job_order_on_machines_copy, instances, self.instance_num, best_objective_value)
                    if cur_objective_value < best_objective_value:
                        best_job_order_on_this_machine = copy.deepcopy(job_order_copy)
                        best_objective_value = cur_objective_value
                        has_improved_on_this_machine = True
                if not has_improved_on_this_machine:
                    accumulated_no_improvement_count += 1
                else:
                    accumulated_no_improvement_count = 1
                # replace the job order on this machine with the best job order
                job_order_on_machines_copy[machine_index] = best_job_order_on_this_machine
                if accumulated_no_improvement_count >= machines_with_maintenance_num:
                    is_best_schedule_found = True
                    break
            # if is_best_schedule_found:
            #     break
        return job_order_on_machines_copy, best_objective_value

    def _try_swapping_shared_job_order(self, job_order_on_machines: list[list], shared_job_order: list[int], initial_best_obj: float) -> tuple[list[int], float]:
        """
        Try swapping shared job order to find the best job order\n
        Return a list of int that indciates the best shared job order after swapping and the best objective value for this job order
        #### Parameters\n
        `job_order_on_machines`: the job order on machines for each stage, it should be a list of list\n
        `shared_job_order`: the shared job order, it should be a list, every element is a job index
        `initial_best_obj`: the initial best objective value, used to see whether there is any swap that can improve the objective value
        """
        # do a deep copy of the job order on machines
        instances = cast_parameters_to_instance(self.parameters)
        job_order_on_machines_copy = copy.deepcopy(job_order_on_machines)
        shared_job_order_copy = copy.deepcopy(shared_job_order)
        best_objective_value = initial_best_obj
        accumulated_no_improvement_count = 0
        # use combinations to generate all possible pairs of jobs to swap
        for i, j in combinations(range(len(shared_job_order_copy)), 2):
            shared_job_order_copy[i], shared_job_order_copy[j] = shared_job_order[j], shared_job_order[i]
            # sort job order on machines according to the new shared job order
            job_order_on_machines_copy = self._sort_schedule_with_shared_job_order(shared_job_order_copy, job_order_on_machines_copy)
            # swap two jobs on the same stage for better performance
            if self.merge_step3_to_step2:
                job_order_on_machines_copy, cur_objective_value = self._try_swapping_two_jobs_on_same_stage(job_order_on_machines_copy, shared_job_order_copy, best_objective_value)
                if cur_objective_value < best_objective_value:
                    best_objective_value = cur_objective_value
                    shared_job_order = copy.deepcopy(shared_job_order_copy)
                    job_order_on_machines = copy.deepcopy(job_order_on_machines_copy)
                    accumulated_no_improvement_count = 1
            if self.combine_maint_and_swap:
                job_order_on_machines_copy, cur_best_objective_value = self._decide_best_maintenance_position(job_order_on_machines_copy, shared_job_order, best_objective_value)
                if cur_best_objective_value < best_objective_value:
                    best_objective_value = cur_objective_value
                    job_order_on_machines = copy.deepcopy(job_order_on_machines_copy)
                    accumulated_no_improvement_count = 1
            # calculate the objective value for this job order under the situation that other machines maintain the same job order
            cur_objective_value = generate_schedule(shared_job_order_copy, job_order_on_machines_copy, instances, self.instance_num, best_objective_value)
            if cur_objective_value < best_objective_value:
                best_objective_value = cur_objective_value
                shared_job_order = copy.deepcopy(shared_job_order_copy)
                job_order_on_machines = copy.deepcopy(job_order_on_machines_copy)
                accumulated_no_improvement_count = 1
            else:
                shared_job_order_copy[i], shared_job_order_copy[j] = shared_job_order_copy[j], shared_job_order_copy[i] # swap back because this swap doesn't improve
                accumulated_no_improvement_count += 1
            if accumulated_no_improvement_count >= len(shared_job_order_copy) * (len(shared_job_order_copy) - 1) / 2: # stopping criteria: no improvement for the number of possible swaps
                break
        return shared_job_order, best_objective_value

    def _try_swapping_two_jobs_on_same_stage(self, job_order_on_machines: list[list], shared_job_order: list[int], initial_best_obj: float) -> tuple[list[list], float]:
        """
        Try swapping two jobs on the same stage to find the best job order\n
        Return a list of list that indciates the best job order schedule after swapping and the best objective value for this schedule
        #### Parameters\n
        `job_order_on_machines`: the job order on machines for each stage, it should be a list of list\n
        `shared_job_order`: the shared job order, it should be a list, every element is a job index
        `initial_best_obj`: the initial best objective value, used to see whether there is any swap that can improve the objective value
        """
        instances = cast_parameters_to_instance(self.parameters)
        best_objective_value = initial_best_obj
        # do a deep copy of the job order on machines
        job_order_on_machines_copy = copy.deepcopy(job_order_on_machines)
        # for each stage, we try swapping two jobs between machines on that stage to find the best job order
        
        # first we need to figure out the number of stages and which machines are on the same stage
        machine_index = 0
        all_stages_machines_job_order = []
        for i in range(self.parameters.Number_of_Stages):
            all_stages_machines_job_order.append([])
            for _ in range(self.parameters.Number_of_Machines[i]):
                all_stages_machines_job_order[i].append(job_order_on_machines_copy[machine_index])
                machine_index += 1
        # then we try swapping two jobs between two machines on the same stage
        with open("extended/swap-2-jobs-on-same-stage/no_maint_inf_queue_time.txt", 'w') as f:
            completed_machines_count = 0
            for cur_stage_index, machines_on_this_stage in enumerate(all_stages_machines_job_order):
                # if there is only one machine on this stage, we don't need to swap
                if len(machines_on_this_stage) == 1:
                    completed_machines_count += 1
                    continue
                # use combinations to generate all possible pairs of machines to swap
                for machine1_index, machine2_index in combinations(range(len(machines_on_this_stage)), 2):
                    # generate a list of pairs, first element is the job index on machine1, second element is the job index on machine2
                    machine1_indexes_have_jobs = [i for i in range(len(machines_on_this_stage[machine1_index])) if machines_on_this_stage[machine1_index][i] != 'M']
                    machine2_indexes_have_jobs = [i for i in range(len(machines_on_this_stage[machine2_index])) if machines_on_this_stage[machine2_index][i] != 'M']
                    swaps = [[machine1_job_index, machine2_job_index] for machine1_job_index in machine1_indexes_have_jobs for machine2_job_index in machine2_indexes_have_jobs]
                    for swap in swaps:
                        # do a deep copy of the two machines's original job order
                        machine1_job_order_copy = copy.deepcopy(machines_on_this_stage[machine1_index])
                        machine2_job_order_copy = copy.deepcopy(machines_on_this_stage[machine2_index])
                        job_order_on_machines_before_swap = copy.deepcopy(job_order_on_machines_copy)
                        # swap the two jobs
                        machine1_job_order_copy[swap[0]], machine2_job_order_copy[swap[1]] = machine2_job_order_copy[swap[1]], machine1_job_order_copy[swap[0]]
                        # update the job order on job schedule
                        job_order_on_machines_copy[completed_machines_count + machine1_index] = machine1_job_order_copy
                        job_order_on_machines_copy[completed_machines_count + machine2_index] = machine2_job_order_copy
                        # sort job order after swapping two jobs
                        job_order_on_machines_copy = self._sort_schedule_with_shared_job_order(shared_job_order, job_order_on_machines_copy)
                        # calculate the objective value for this job order under the situation that other machines maintain the same job order
                        cur_objective_value = generate_schedule(shared_job_order, job_order_on_machines_copy, instances, self.instance_num, best_objective_value)
                        f.write(f"Stage {cur_stage_index + 1}, Machine {machine1_index + 1} and Machine {machine2_index + 1}, Swap {machine1_job_order_copy[swap[0]]} and {machine2_job_order_copy[swap[1]]}, Objective Value {cur_objective_value} | ")
                        if cur_objective_value < best_objective_value:
                            f.write("improved!\n")
                            best_objective_value = cur_objective_value
                            machines_on_this_stage[machine1_index] = machine1_job_order_copy
                            machines_on_this_stage[machine2_index] = machine2_job_order_copy
                        else:
                            f.write("not improved!\n")
                            job_order_on_machines_copy = job_order_on_machines_before_swap
                completed_machines_count += len(machines_on_this_stage)
            return job_order_on_machines_copy, best_objective_value

    def _sort_schedule_with_shared_job_order(self, shared_job_order: list[int], schedule: list[list]) -> list[list]:
        """
        Generate the schedule with the shared job order\n
        Return a list of list, each list indicates the job order for each machine on each stage
        #### Parameters\n
        `shared_job_order`: the shared job order, it should be a list, every element is a job index
        `schedule`: the schedule, it should be a list of list, each list indicates the job order for each machine on each stage, notice that the job index starts from 1
        """
        # sort job order on machines according to the shared job order
        job_priority = {}
        for priority, job_index in enumerate(shared_job_order):
            job_priority[job_index] = priority

        # do a deep copy of the schedule
        schedule_copy = copy.deepcopy(schedule)
        for machine_job_order in schedule_copy:
            # if the job order contains 'M', we cannot directly sort it, so we need to store the index of 'M' and remove it first
            if 'M' in machine_job_order:
                # find the index of 'M'
                m_index = machine_job_order.index('M')
                # remove 'M'
                machine_job_order.remove('M')
                # sort the job order
                machine_job_order.sort(key=lambda x: job_priority[x])
                # insert 'M' back to the original position
                machine_job_order.insert(m_index, 'M')
            else:
                machine_job_order.sort(key=lambda x: job_priority[x])
        return schedule_copy
    
    
    def record_result(self, df: pd.DataFrame, num: int):
        """
        Record the result of the algorithm
        """
        # shared job order is a list of int, so store it to json file
        print(f"Final Objective Value: {self.final_result['objective_value']}")
        print(f"Final Shared Job Order: {self.final_result['shared_job_order']}")
        print(f"Final Schedule: {self.final_result['schedule']}")
        print("=====")

        df.iloc[num]["initial objective value"] = self.initial_result['objective_value']
        df.iloc[num]["initial shared job order"] = self.initial_result['shared_job_order']
        df.iloc[num]["initial schedule"] = self.initial_result['schedule']
        df.iloc[num]["merge objective value"] = self.merge_result['objective_value']
        df.iloc[num]["merge shared job order"] = self.merge_result['shared_job_order']
        df.iloc[num]["merge schedule"] = self.merge_result['schedule']
        df.iloc[num]["no merge objective value"] = self.no_merge_result['objective_value']
        df.iloc[num]["no merge shared job order"] = self.no_merge_result['shared_job_order']
        df.iloc[num]["no merge schedule"] = self.no_merge_result['schedule']
        df.iloc[num]["greedy time"] = self.no_merge_result['greedy_time']
        df.iloc[num]["final objective value"] = self.final_result['objective_value']
        df.iloc[num]["final shared job order"] = self.final_result['shared_job_order']
        df.iloc[num]["final schedule"] = self.final_result['schedule']

        return df
        # with open(self.file_path, 'w+') as f:
        #     json.dump(self.final_result, f)

    def run_initial_and_save_result(self, file_path) -> None:
        """
        Run the initial job listing function and save the result, which is list of list, each list indicates the job order for each machine on each stage
        """
        initial_job_listing = self.generate_initial_job_listing()
        df = pd.DataFrame({'output': initial_job_listing})
        df.to_csv(file_path, index=False)
