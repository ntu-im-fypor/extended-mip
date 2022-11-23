import numpy as np
from Models import Parameters

def get_maintenance_choice(parameters: Parameters) -> np.ndarray:
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
    for i in range(len(benefit_list) // 2):
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

def get_average_machine_time_for_each_stage(parameters: Parameters, production_time_matrix: np.ndarray) -> np.ndarray:
    """
    production_time_matrix: a 3d array of shape `(Number_of_Stages, max_machine_num, Number_of_Jobs)`
    each element is the real production time for that job on that machine.
    You can get this matrix by calling `get_real_production_time_matrix(parameters, maintenance_choice)`
    #### 這裡的 production_time_matrix 就是 1121_會議簡報 p.18 的 production time table, 會考慮 maintenance 後的時間
    Get the average machine time for each stage
    return a 1d array of shape (Number_of_Stages)
    every element is the average machine time for that stage
    """
    average_machine_time = np.zeros(parameters.Number_of_Stages)
    for i in range(parameters.Number_of_Stages):
        for j in range(parameters.Number_of_Machines[i]):
            # need to add unfinished production time for that machine
            average_machine_time[i] += parameters.Unfinished_Production_Time[i][j]
            for k in range(parameters.Number_of_Jobs):
                average_machine_time[i] += production_time_matrix[i][j][k]
        average_machine_time[i] /= parameters.Number_of_Machines[i] * parameters.Number_of_Machines[i] # divide by the square of the number of machines
    return average_machine_time