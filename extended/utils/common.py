import math
from operator import itemgetter
from Models import Parameters

# Instance:
# JOBS_NUM: number of jobs, ex: 3
# STAGES_NUMBER: number of stages, ex: 2
# MACHINES_NUM: list of number of machines for each stage, ex: [2, 1]
# DISCOUNT: list of discount for each machine, ex: [0.8, 0.7, 0.9]
# MAINT_LEN: list of maintenance length for each machine, ex: [5, 4, 6]
# REMAIN: list of unfinished production on each machine, ex: [3, 6, 0]
# INIT_PROD_TIME: MACHINES_NUM * JOBS_NUM array of the initial production time per job per machine, ex: [[10, 15, 13],[12, 17, 15],[8, 15, 12]]
# DUE_TIME: list of due times of each job, ex: [30, 40, 30]
# WEIGHT: list of penalty of each job, ex: [100, 200, 100]
# QUEUE_LIMIT: list of queue time limit of each job, assumeing the value doesn't change across different stages, ex: [10, 10, 0]


# Sol:
# STAGES_NUMBER * (JOBS_NUM + max(MACHINES_NUM)) array of the job & maintainance schedule,
# ex: [[1.2, 1.3, 2.5, 0, 2.3], [1.2, 1.5, 1.3, 1.1, 0]]

# Initializa an instance and solution
class Instance:
    JOBS_NUM = 3
    STAGES_NUMBER = 2
    MACHINES_NUM = [2, 1]
    DISCOUNT = [0.8, 0.7, 0.9]
    MAINT_LEN = [5, 4, 6]
    REMAIN = [3, 6, 0]
    INIT_PROD_TIME = [[10, 15, 13], [12, 17, 15], [8, 15, 12]]
    DUE_TIME = [30, 40, 30]
    WEIGHT = [100, 200, 200]
    QUEUE_LIMIT = [10, 10, 0]
    MAX_MACHINES_NUM = max(MACHINES_NUM)


def cast_parameters_to_instance(parameters: Parameters) -> Instance:
    instance = Instance()
    instance.JOBS_NUM = parameters.Number_of_Jobs
    instance.MAX_MACHINES_NUM = parameters.Max_Number_of_Machines
    instance.STAGES_NUMBER = parameters.Number_of_Stages
    instance.MACHINES_NUM = parameters.Number_of_Machines
    instance.DISCOUNT = []
    for i in range(parameters.Number_of_Stages):
        for m in range(parameters.Number_of_Machines[i]):
            instance.DISCOUNT.append(parameters.Production_Time_Discount[i][m])

    instance.MAINT_LEN = []
    for i in range(parameters.Number_of_Stages):
        for m in range(parameters.Number_of_Machines[i]):
            instance.MAINT_LEN.append(parameters.Maintenance_Length[i][m])

    instance.REMAIN = []
    for i in range(parameters.Number_of_Stages):
        for m in range(parameters.Number_of_Machines[i]):
            instance.REMAIN.append(parameters.Unfinished_Production_Time[i][m])

    instance.INIT_PROD_TIME = []
    for i in range(parameters.Number_of_Stages):
        for m in range(parameters.Number_of_Machines[i]):
            machine_prod_list = []
            for j in range(parameters.Number_of_Jobs):
                machine_prod_list.append(parameters.Initial_Production_Time[i][m][j])
            instance.INIT_PROD_TIME.append(machine_prod_list)
    instance.DUE_TIME = parameters.Due_Time.tolist()
    instance.WEIGHT = parameters.Tardiness_Penalty.tolist()
    instance.QUEUE_LIMIT = []
    for i in range(1, parameters.Number_of_Stages):
        instance.QUEUE_LIMIT.append(parameters.Queue_Time_Limit[i].tolist())
    return instance