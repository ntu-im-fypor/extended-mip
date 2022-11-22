from Models import Parameters, SolutionModel
from utils.ours_utils import get_maintenance_choice, get_real_production_time_matrix, get_WEDD_list, get_average_machine_time_for_each_stage
import numpy as np

class GreedyModel(SolutionModel):
    def __init__(self, parameters: Parameters):
        super().__init__(parameters)

    def run_and_solve(self):
        """
        Run and solve the problem using Greedy, and then store the output schedule into self.schedule.
        Then calculate the objective value of the schedule using record_result()
        """
        print("Running and solving using GreedyModel")
        
        # setup
        self._setup()
        # run initial job listing
        self._run_initial_job_listing()
        
    def _setup(self):
        """
        Setup the data for the model
        """
        self.maintenace_choice = get_maintenance_choice(self.parameters)
        self.real_production_time_matrix = get_real_production_time_matrix(self.parameters, self.maintenace_choice)
        self.WEDD_list = get_WEDD_list(self.parameters)
        self.average_machine_time_for_each_stage = get_average_machine_time_for_each_stage(self.parameters, self.real_production_time_matrix)
    def _run_initial_job_olisting(self):
        """
        Run the initial job listing part
        it will return the initial job listing schedule indicating the job order
        the shape of the initial job listing is (number of stages, max number of machines, number of jobs)
        """

        # first create a 3d list to store the job order for every machine in every stage the 3-th dimension is default to an empty list
        job_order_list = []
        for i in range(self.parameters.Number_of_Stages):
            job_order_list.append([])
            for _ in range(self.parameters.Number_of_Machines[i]):
                job_order_list[i].append([])

        current_job_priority = {}
        current_jobs_info = []
        for k in range(self.parameters.Number_of_Jobs):
            current_jobs_info.append((i, self.WEDD_list[k]))
        # sort the current jobs info by the WEDD
        current_jobs_info.sort(key=lambda x: x[1]) # first shared job order is sorted by WEDD, the lower the WEDD, the higher the priority
        # keep this information in a dictionary
        priority_index = 0
        for job_index, _ in current_jobs_info:
            current_job_priority[job_index] = priority_index
            priority_index += 1
        
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
        job_order_list.sort(key=lambda x: x[1]) # x[1] is the current job priority index for this job, and we want lower index to be scheduled first, so we sort in ascending order
        # now we have the initial job listing, we need to flatten the list
        job_order_list_flatten = []
        for i in range(self.parameters.Number_of_Stages):
            for j in range(self.parameters.Number_of_Machines[i]):
                job_order_list_flatten.append(job_order_list[i][j])

        # TODO: till now we have the initial job listing after flattening so that we can put the listing into the generate_schedule function. But the correctness has not been verified yet.

    def record_result(self):
        return super().record_result()