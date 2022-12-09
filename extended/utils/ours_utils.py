import numpy as np
from Models import Parameters

def get_maintenance_choice(parameters: Parameters, percent: float) -> np.ndarray:
    """
    Get the maintenance benefit for each machine
    maintenance benefit = average discounted time - maintenance length
    return a 2d array of shape (Number_of_Stages, max_machine_num)
    every element is the maintenance benefit for that machine
    """
    max_machine_num = np.max(parameters.Number_of_Machines)
    maintenance_benefit = np.zeros((parameters.Number_of_Stages, max_machine_num))
    for i in range(parameters.Number_of_Stages):
        # calculate average discounted time base value
        base_value = 0
        for j in range(parameters.Number_of_Machines[i]):
            for k in range(parameters.Number_of_Jobs):
                base_value += parameters.Initial_Production_Time[i][j][k]
        base_value /= parameters.Number_of_Machines[i] * parameters.Number_of_Jobs

        # for each machine, times the base value by the discount ratio
        for j in range(parameters.Number_of_Machines[i]):
            maintenance_benefit[i][j] = base_value * parameters.Production_Time_Discount[i][j] - parameters.Maintenance_Length[i][j]
    
    # create a list of tuples (benefit, (stage, machine)) and sort it by benefit to get the highest benefit first
    benefit_list = []
    for i in range(parameters.Number_of_Stages):
        for j in range(parameters.Number_of_Machines[i]):
            benefit_list.append((maintenance_benefit[i][j], (i, j)))

    benefit_list.sort(key=lambda x: x[0], reverse=True)
    
    # create a 2d array of shape (Number_of_Stages, max_machine_num)
    # every element indicates whether that machine is chosen to do maintenance
    # 1 means chosen, 0 means not chosen
    maintenance_choice = np.zeros((parameters.Number_of_Stages, max_machine_num))
    # choose the top `percent` percent of machines to do maintenance
    for i in range(int(len(benefit_list) * percent)):
        maintenance_choice[benefit_list[i][1][0]][benefit_list[i][1][1]] = 1
    return maintenance_choice

def get_real_production_time_matrix(parameters: Parameters, maintenance_choice: np.ndarray):
    """
    Get the real production time matrix
    return a 3d array of shape (Number_of_Stages, max_machine_num, Number_of_Jobs)
    each element is the real production time for that job on that machine
    """
    max_machine_num = np.max(parameters.Number_of_Machines)
    production_time_matrix = np.zeros((parameters.Number_of_Stages, max_machine_num, parameters.Number_of_Jobs))
    for i in range(parameters.Number_of_Stages):
        for j in range(parameters.Number_of_Machines[i]):
            # if the machine is not chosen to do maintenance, set the production time to the initial production time
            # else set the production time to the initial production time times the production time discount
            if maintenance_choice[i][j] == 0:
                for k in range(parameters.Number_of_Jobs):
                    production_time_matrix[i][j][k] = parameters.Initial_Production_Time[i][j][k]
            elif maintenance_choice[i][j] == 1:
                for k in range(parameters.Number_of_Jobs):
                    production_time_matrix[i][j][k] = parameters.Initial_Production_Time[i][j][k] * parameters.Production_Time_Discount[i][j]
    return production_time_matrix

def get_WEDD_list(parameters: Parameters):
    """
    Get the WEDD list for each job
    WEDD = due time of the job / tardiness penalty of the job

    return a 1d array of shape `Number_of_Jobs`
    every element is the WEDD for that job
    """
    WEDD_list = np.zeros(parameters.Number_of_Jobs)
    for k in range(parameters.Number_of_Jobs):
        WEDD_list[k] = parameters.Due_Time[k] / parameters.Tardiness_Penalty[k]
    return WEDD_list

def get_average_machine_time_for_each_stage(parameters: Parameters, production_time_matrix: np.ndarray, method_choice: int) -> np.ndarray:
    """
    Get the average machine time for each stage\n
    method_choice:
    0: origin method, choose by time difference for each job on different machines,
       if schedule the job onto this machine will make current machine time exceed average machine time on this stage,
       we try to find another machine that have smallest current machine time
    1: very large average_machine_time, for each job, just choose the smallest production time on different machines
    2: very small average_machine_time, for each job, choose the machine that can make the smallest current machine time
    """
    average_machine_time = np.zeros(parameters.Number_of_Stages)
    if method_choice == 0:
        for i in range(parameters.Number_of_Stages):
            for j in range(parameters.Number_of_Machines[i]):
                # need to add unfinished production time for that machine
                average_machine_time[i] += parameters.Unfinished_Production_Time[i][j]
                for k in range(parameters.Number_of_Jobs):
                    average_machine_time[i] += production_time_matrix[i][j][k]
            average_machine_time[i] /= parameters.Number_of_Machines[i] # divide by the square of the number of machines
    elif method_choice == 1:
        for i in range(parameters.Number_of_Stages):
            for j in range(parameters.Number_of_Machines[i]):
                average_machine_time[i] += parameters.Unfinished_Production_Time[i][j]
                for k in range(parameters.Number_of_Jobs):
                    average_machine_time[i] += production_time_matrix[i][j][k]
    else:
        for i in range(parameters.Number_of_Stages):
            average_machine_time[i] == -1 
    return average_machine_time

def get_shared_job_order_from_WEDD_list(WEDD_list):
    """
    Get the shared job order from the WEDD list\n
    Return a 1d array of shape `Number_of_Jobs`, every element is the job index, the job index starts from 1
    """
    job_order = []
    for job_index in range(1, len(WEDD_list) + 1):
        job_order.append(job_index)
    job_order.sort(key=lambda x: WEDD_list[x - 1]) 
    return job_order