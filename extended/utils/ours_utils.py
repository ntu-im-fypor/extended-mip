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

def get_EDD_list(parameters: Parameters):
    """
    Get the EDD list for each job
    EDD = due time of the job

    return a 1d array of shape `Number_of_Jobs`
    every element is the EDD for that job
    """
    EDD_list = np.zeros(parameters.Number_of_Jobs)
    for k in range(parameters.Number_of_Jobs):
        EDD_list[k] = parameters.Due_Time[k]
    return EDD_list

def get_SPT_list(parameters: Parameters, production_time_matrix: np.ndarray):
    """
    Get the SPT list for each job
    SPT = shortest production time of the job on stage 1
    """
    SPT_list = np.zeros(parameters.Number_of_Jobs)
    for k in range(parameters.Number_of_Jobs):
        SPT_list[k] = np.min(production_time_matrix[0][:, k])
    return SPT_list
def get_average_machine_time_for_each_stage(parameters: Parameters, production_time_matrix: np.ndarray, method_choice: int, sensitive_denominator: float) -> np.ndarray:
    """
    Get the average machine time for each stage\n
    method_choice:
    0: origin method, choose by time difference for each job on different machines,
       if schedule the job onto this machine will make current machine time exceed average machine time on this stage,
       we try to find another machine that have smallest current machine time
    1: very large average_machine_time, for each job, just choose the smallest production time on different machines
    2: very small average_machine_time, for each job, choose the machine that can make the smallest current machine time
    3: half of average_machine_time
    4: average = all values' Q2 value * number of jobs
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
    elif method_choice == 2:
        for i in range(parameters.Number_of_Stages):
            average_machine_time[i] = -1 
    elif method_choice == 3:
        for i in range(parameters.Number_of_Stages):
            for j in range(parameters.Number_of_Machines[i]):
                # need to add unfinished production time for that machine
                average_machine_time[i] += parameters.Unfinished_Production_Time[i][j]
                for k in range(parameters.Number_of_Jobs):
                    average_machine_time[i] += production_time_matrix[i][j][k]
            average_machine_time[i] /= (parameters.Number_of_Machines[i]*sensitive_denominator) # divide by the square of the number of machines
    else:
        for i in range(parameters.Number_of_Stages):
            values = []
            for j in range(parameters.Number_of_Machines[i]):
                for k in range(parameters.Number_of_Jobs):
                    values.append(production_time_matrix[i][j][k])
            q2_value = np.quantile(values, .50)

            for j in range(parameters.Number_of_Machines[i]):
                average_machine_time[i] += parameters.Unfinished_Production_Time[i][j]
                for k in range(parameters.Number_of_Jobs):
                    average_machine_time[i] += q2_value
            average_machine_time[i] /= parameters.Number_of_Machines[i] # divide by the square of the number of machines

    return average_machine_time

def get_shared_job_order(weight_list):
    """
    Get the shared job order from the weight list, the weight list can be WEDD, EDD, SPT.
    Return a 1d array of shape `Number_of_Jobs`, every element is the job index, the job index starts from 1
    """
    job_order = []
    for job_index in range(1, len(weight_list) + 1):
        job_order.append(job_index)
    job_order.sort(key=lambda x: weight_list[x - 1]) 
    return job_order

def get_shared_job_order_from_Gurobi(instance_num: int) -> list[int]:
    """
    Get shared job order from files generated by Gurobi
    """
    gurobi_order_dict = get_Gurobi_order_dict()
    print("gurobi order: ", gurobi_order_dict[instance_num])
    # get the job order with row index = instance_num
    return gurobi_order_dict[instance_num]


def get_Gurobi_order_dict() -> dict:
        # The 30 lists as strings
    lists = [
        "4,1,2,10,6,7,8,9,5,3",
        "6,5,7,10,9,2,1,4,3,8",
        "5,1,2,7,3,6,4,10,9,8",
        "7,9,10,6,1,5,4,8,3,2",
        "5,7,6,4,10,9,3,8,1,2",
        "9,10,1,2,3,4,7,5,6,8",
        "10,6,9,7,4,2,8,1,5,3",
        "2,10,3,5,4,1,6,8,9,7",
        "7,4,1,6,8,2,3,9,5,10",
        "1,2,3,9,4,5,6,7,8,10",
        "10,5,2,1,3,9,6,8,4,7",
        "7,9,3,5,1,2,4,8,6,10",
        "1,2,5,4,10,9,6,3,8,7",
        "2,7,8,9,3,1,6,10,4,5",
        "9,8,6,1,4,7,3,10,2,5",
        "2,9,10,5,7,1,8,6,3,4",
        "5,2,8,6,1,7,10,4,9,3",
        "7,5,1,10,2,4,6,8,9,3",
        "8,10,9,5,6,1,4,3,2,7",
        "10,8,6,3,9,5,1,7,2,4",
        "8,6,10,7,4,1,2,3,9,5",
        "9,10,4,6,1,5,7,8,3,2",
        "7,4,10,5,1,6,2,8,9,3",
        "5,7,2,4,9,3,6,10,8,1",
        "1,8,10,5,2,7,9,3,6,4",
        "7,9,6,1,3,8,4,10,2,5",
        "1,2,10,4,5,9,3,6,7,8",
        "9,10,6,5,3,7,2,1,4,8",
        "3,5,7,1,10,6,9,4,8,2",
        "10,2,4,1,8,9,3,7,5,6"
    ]

    # Convert the strings to lists of integers
    lists_of_ints = [list(map(int, lst.split(","))) for lst in lists]

    # Create the dictionary with 1-indexed keys
    return {i+1: lst for i, lst in enumerate(lists_of_ints)}