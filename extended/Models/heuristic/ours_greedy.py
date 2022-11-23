from Models import Parameters, SolutionModel
import utils.ours_utils as utils
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
        # run initial job listing with maintenance
        initial_job_listing = self._generate_initial_job_listing()
        
    def _setup(self):
        """
        Setup the data for the model
        """
        self.maintenance_choice = utils.get_maintenance_choice(self.parameters)
        self.real_production_time_matrix = utils.get_real_production_time_matrix(self.parameters, self.maintenance_choice)
        self.WEDD_list = utils.get_WEDD_list(self.parameters)
        self.average_machine_time_for_each_stage = utils.get_average_machine_time_for_each_stage(self.parameters, self.real_production_time_matrix)
    def _generate_initial_job_listing(self):
        """
        Run the initial job listing part\n
        it will return the initial job listing schedule indicating the job order\n
        the shape follows the input format of generate_schedule function written by Hsiao-Li Yeh
        """

        # first create a 3d list to store the job order for every machine in every stage the 3-th dimension is default to an empty list
        job_order_list = []
        for i in range(self.parameters.Number_of_Stages):
            job_order_list.append([])
            for _ in range(self.parameters.Number_of_Machines[i]):
                job_order_list[i].append([])

        # generate the shared job order
        current_job_priority = self._generate_shared_job_order()
        
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

    def _generate_shared_job_order(self) -> dict:
        """
        Generate the shared job order. It will return a dictionary\n
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

    def record_result(self):
        return super().record_result()