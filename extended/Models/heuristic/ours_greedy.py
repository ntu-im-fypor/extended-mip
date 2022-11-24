from Models import Parameters, SolutionModel
from utils.common import cast_parameters_to_instance
from utils.generate_schedule import generate_schedule
import utils.ours_utils as utils
import numpy as np
import copy

class GreedyModel(SolutionModel):
    def __init__(self, parameters: Parameters):
        super().__init__(parameters)

    def run_and_solve(self):
        """
        Run and solve the problem using Greedy, and then store the output schedule into self.schedule.
        Then calculate the objective value of the schedule using record_result()
        """
        print("Running and solving using GreedyModel")
        # run initial job listing with maintenance
        initial_job_listing = self.generate_initial_job_listing()
        # get the shared job order for the initial job listing
        initial_shared_job_order = utils.get_shared_job_order_from_WEDD_list(self.WEDD_list)
        # start to consider the best maintenance position for each machine
        initial_job_schedule = self._decide_best_maintenance_position(initial_job_listing, initial_shared_job_order)
        
    def _setup(self):
        """
        Setup the data for the model
        """
        self.maintenance_choice = utils.get_maintenance_choice(self.parameters)
        self.real_production_time_matrix = utils.get_real_production_time_matrix(self.parameters, self.maintenance_choice)
        self.WEDD_list = utils.get_WEDD_list(self.parameters)
        self.average_machine_time_for_each_stage = utils.get_average_machine_time_for_each_stage(self.parameters, self.real_production_time_matrix)
    def generate_initial_job_listing(self, shared_job_order: list[int] = None) -> list[list]:
        """
        Run the initial job listing part\n
        it will return the initial job listing schedule indicating the job order\n
        the shape follows the input format of generate_schedule function written by Hsiao-Li Yeh
        #### Parameters
        - `shared_job_order`: the shared job order, if not provided, it will use WEDD list to generate the shared job order
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
            current_job_priority = self._generate_shared_job_order_from_WEDD()
        else:
            for i in range(len(shared_job_order)):
                current_job_priority[shared_job_order[i]] = i
        
        # current machine time for every machine is default to unfinished production time
        current_machine_time = self.parameters.Unfinished_Production_Time

        # for each stage, we calculate the largest production time difference for each job on different machines
        # larger production time difference means we should schedule the job first
        for i in range(self.parameters.Number_of_Stages):
            production_difference_list = [] # store production time difference for each job, every element is a tuple (job index, production time difference)
            machine_num = self.parameters.Number_of_Machines[i]
            for k in range(self.parameters.Number_of_Jobs):
                production_difference_list.append((k, max(self.real_production_time_matrix[i, :machine_num, k]) - min(self.real_production_time_matrix[i, :machine_num, k])))
            production_difference_list.sort(key=lambda x: x[1], reverse=True) # sort the list by production time difference, descending order
            # start to schedule the job onto the machine
            for job_index, _ in production_difference_list:
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
                    # if the current machine time for the machine with smallest current machine time is still larger than average machine time on this stage, then we need to schedule the job onto the machine with smallest production time
                    if smallest_current_machine_time <= self.average_machine_time_for_each_stage[i]:
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
                    job_order_for_this_machine.append(job_index)
                job_order_list_flatten.append(job_order_for_this_machine)
        # complete the initial job listing
        return job_order_list_flatten

    def _generate_shared_job_order_from_WEDD(self) -> dict:
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

    def _decide_best_maintenance_position(self, job_order_on_machines: list[list], shared_job_order: list[int]) -> list[list]:
        """
        Decide the best maintenance position for each machine on each stage\n
        For every machine with maintenance, we will try to find the best position for the maintenance\n
        Return a list of list, each list indicates the job order for each machine on each stage
        #### Parameters\n
        `job_order_on_machines`: the job order on machines for each stage, it should be a list of list\n
        `shared_job_order`: the shared job order, it should be a list, every element is a job index
        """

        # do a deep copy of the job order on machines
        instances = cast_parameters_to_instance(self.parameters)
        job_order_on_machines_copy = copy.deepcopy(job_order_on_machines)
        best_objective_value = np.inf
        # calculate the number of machines with maintenance
        machines_with_maintenance_num = 0
        for job_order in job_order_on_machines_copy:
            if job_order[0] == 'M':
                machines_with_maintenance_num += 1
        while True: # stopping crietria: no improvement for the number of machines with maintenance
            accumulated_no_improvement_count = 0
            for machine_index, job_order in enumerate(job_order_on_machines_copy):
                # if the job order contains 'M', it means this machine has maintenance, so we need to find the best position for the maintenance
                if 'M' in job_order:
                    has_improved_on_this_machine = False
                    # do a deep copy of the job order
                    job_order_copy = copy.deepcopy(job_order)
                    # first we get the job order list without 'M', and insert 'M' into every possible position to find the best position
                    for i in range(len(job_order_copy) + 1):
                        job_order_copy.remove('M')
                        job_order_copy.insert(i, 'M')
                        # replace the job order on this machine with the new job order
                        job_order_on_machines_copy[machine_index] = job_order_copy
                        # calculate the objective value for this job order under the situation that other machines maintain the same job order
                        cur_objective_value = generate_schedule(shared_job_order, job_order_on_machines_copy, instances)
                        if cur_objective_value < best_objective_value:
                            best_objective_value = cur_objective_value
                            has_improved_on_this_machine = True
                        else:
                            # replace the job order on this machine with the original job order
                            job_order_on_machines_copy[machine_index] = job_order
                    if not has_improved_on_this_machine:
                        accumulated_no_improvement_count += 1
            if accumulated_no_improvement_count == machines_with_maintenance_num:
                break
        return job_order_on_machines_copy

    def record_result(self):
        return super().record_result()