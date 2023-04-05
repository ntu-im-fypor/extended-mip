from itertools import combinations
import json
from Models import Parameters, SolutionModel
from utils.common import cast_parameters_to_instance
from utils.generate_schedule import generate_schedule
import utils.ours_utils as utils
import numpy as np
import pandas as pd
import copy

class GreedyModel(SolutionModel):
    def __init__(self, parameters: Parameters, use_gurobi_order = False, maintenance_choice_percentage: float = 0.5, file_path: str = None, instance_num: int = 0):
        """
        Initialize the model with the parameters and the maintenance choice percentage
        #### Parameters
        - `parameters`: the parameters of the problem
        - `maintenance_choice_percentage`: the percentage of the maintenance choice, that is, after calculating maintenance benefit, we choose first `maintenance_choice_percentage` of the machines to do maintenance
        - `file_path`: the file path to store the result
        """
        super().__init__(parameters)
        if file_path is None:
            print("No file path specified!")
            return
        self.use_gurobi_order = use_gurobi_order
        self.file_path = file_path
        self.maintenance_choice_percentage = maintenance_choice_percentage
        self.instance_num = instance_num

    def run_and_solve(self):
        """
        Run and solve the problem using Greedy, and then store the output schedule into self.schedule.
        Then calculate the objective value of the schedule using record_result()
        """
        print("Running and solving using GreedyModel")
        # run initial job listing with maintenance
        initial_job_listing = self.generate_initial_job_listing()
        # get the shared job order for the initial job listing
        initial_shared_job_order = list[int]
        if self.use_gurobi_order:
            initial_shared_job_order = utils.get_shared_job_order_from_Gurobi(self.instance_num)
            initial_job_listing = self._sort_schedule_with_shared_job_order(initial_shared_job_order, initial_job_listing)
        else:
            initial_shared_job_order = utils.get_shared_job_order_from_WEDD_list(self.WEDD_list)
        # start to consider the best maintenance position for each machine
        initial_job_schedule, initial_best_objective_value = self._decide_best_maintenance_position(initial_job_listing, initial_shared_job_order, np.inf)
        print(f"Initial Objective Value: {initial_best_objective_value}")
        print(f"Initial Shared Job Order: {initial_shared_job_order}")
        print(f"Initial Schedule: {initial_job_schedule}")
        print("=====")

        # store the initial results for final reference (after swapping shared job order)
        self.initial_result = {
            "schedule": initial_job_schedule,
            "objective_value": initial_best_objective_value,
            "shared_job_order": initial_shared_job_order
        }

        # try swapping shared job order and adjusting maintenance position to see if we can get a better solution
        best_objective_value = initial_best_objective_value
        best_job_schedule = initial_job_schedule
        best_shared_job_order = initial_shared_job_order
        has_improved = False
        while True:
            # try swapping shared job order to see if we can get a better solution
            cur_best_shared_job_order, cur_best_obj = self._try_swapping_shared_job_order(best_job_schedule, best_shared_job_order, best_objective_value)
            if cur_best_obj < best_objective_value:
                # use best swapped order to generate a new schedule
                best_shared_job_order = cur_best_shared_job_order
                best_job_schedule = self._sort_schedule_with_shared_job_order(best_shared_job_order, best_job_schedule)
                best_objective_value = cur_best_obj
            # try adjusting maintenance position to see if we can get a better solution
            cur_best_schedule, cur_best_obj = self._decide_best_maintenance_position(best_job_schedule, best_shared_job_order, best_objective_value)
            if cur_best_obj < best_objective_value:
                best_job_schedule = cur_best_schedule
                best_objective_value = cur_best_obj
                has_improved = True
            else:
                has_improved = False
            if not has_improved:
                break
        print(f"Objective Value: {best_objective_value}")
        print(f"Shared Job Order: {best_shared_job_order}")
        print(f"Schedule: {best_job_schedule}")
        print("=====")

        # store the current results for final reference (after swapping shared job order)
        self.process_result = {
            "schedule": best_job_schedule,
            "objective_value": best_objective_value,
            "shared_job_order": best_shared_job_order
        }

        best_job_schedule, best_objective_value = self._try_swapping_two_jobs_on_same_stage(best_job_schedule, best_shared_job_order, best_objective_value)

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
        self.WEDD_list = utils.get_WEDD_list(self.parameters)
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
            current_jobs_info.append((k, self.WEDD_list[k]))
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
        while True: # stopping crietria: no improvement for the number of machines with maintenance
            is_best_schedule_found = False
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
            if is_best_schedule_found:
                break
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
        # keep writing the shared job order and current best objective value into a file
        with open('extended/swap-job-records/no_maint_inf_queue_time.txt', 'a') as f:
            while True:
                # use combinations to generate all possible pairs of jobs to swap
                for i, j in combinations(range(len(shared_job_order_copy)), 2):
                    shared_job_order_copy[i], shared_job_order_copy[j] = shared_job_order[j], shared_job_order[i]
                    # sort job order on machines according to the new shared job order
                    job_order_on_machines_copy = self._sort_schedule_with_shared_job_order(shared_job_order_copy, job_order_on_machines_copy)
                    # calculate the objective value for this job order under the situation that other machines maintain the same job order
                    cur_objective_value = generate_schedule(shared_job_order_copy, job_order_on_machines_copy, instances, self.instance_num, best_objective_value)
                    if cur_objective_value < best_objective_value:
                        f.write(f"best obj value: [{best_objective_value}] shared job order: " + str(shared_job_order_copy) + "; objective value: " + str(cur_objective_value) + "\n")
                        best_objective_value = cur_objective_value
                        shared_job_order = copy.deepcopy(shared_job_order_copy)
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
        df.iloc[num]["process objective value"] = self.process_result['objective_value']
        df.iloc[num]["process shared job order"] = self.process_result['shared_job_order']
        df.iloc[num]["process schedule"] = self.process_result['schedule']
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
