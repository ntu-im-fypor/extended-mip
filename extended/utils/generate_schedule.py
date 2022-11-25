import math
from operator import itemgetter
# from Models import Parameters

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


# Order On Machines:
# Order of jobs and maintenance on a Machine, ex:
# ex: [[3,1], [4,2,5], [M,4,2,3,5,1], [M,4,2,3,5,1]]

# Shared Job Order
# ex: [4,2,3,5,1]

# Initializa an instance and solution
class Instance:
    JOBS_NUM = 8
    STAGES_NUMBER = 3
    MACHINES_NUM = [1, 1, 1]
    DISCOUNT = [0.8976129930150941, 0.8810900058491944, 0.8070112615378183]
    MAINT_LEN = [26.886434421662717, 24.605185592139204, 27.026819567803]
    REMAIN = [2, 14, 0]
    INIT_PROD_TIME = [[18, 5, 29, 26, 8, 14, 12, 22], [21, 23, 10, 18, 29, 18, 5, 13], [15, 18, 29, 17, 8, 12, 21, 25]]
    DUE_TIME = [149.07383907299263, 101.29023952518345, 80.29088167978276, 73.63473424011333, 119.91225978166554, 128.19439549338392, 125.35327253440184, 121.49742279836815]
    WEIGHT = [1.0894125775069705, 0.9436711936056963, 0.9396820198071156, 0.9097654816906069, 1.176964048797249, 0.9840779030753487, 1.1502149340402437, 0.9577260790261988]
    QUEUE_LIMIT = [[1, 12, 15, 4, 8, 1, 8, 1], [13, 1, 14, 16, 11, 17, 9, 1]]


# def transform_parameters_to_instance(parameters: Parameters) -> Instance:
#     instance = Instance()
#     instance.JOBS_NUM = parameters.Number_of_Jobs
#     instance.STAGES_NUMBER = parameters.Number_of_Stages
#     instance.MACHINES_NUM = parameters.Number_of_Machines
#     instance.DISCOUNT = []
#     for i in range(parameters.Number_of_Stages):
#         for m in range(parameters.Number_of_Machines[i]):
#             instance.DISCOUNT.append(parameters.Production_Time_Discount[i][m])

#     instance.MAINT_LEN = []
#     for i in range(parameters.Number_of_Stages):
#         for m in range(parameters.Number_of_Machines[i]):
#             instance.MAINT_LEN.append(parameters.Maintenance_Length[i][m])

#     instance.REMAIN = []
#     for i in range(parameters.Number_of_Stages):
#         for m in range(parameters.Number_of_Machines[i]):
#             instance.REMAIN.append(parameters.Unfinished_Production_Time[i][m])
        
#     instance.INIT_PROD_TIME = []
#     for i in range(parameters.Number_of_Stages):
#         for m in range(parameters.Number_of_Machines[i]):
#             machine_prod_list = []
#             for j in range(parameters.Number_of_Jobs):
#                 machine_prod_list.append(parameters.Initial_Production_Time[i][m][j])
#             instance.INIT_PROD_TIME.append(machine_prod_list)
#     instance.DUE_TIME = parameters.Due_Time.tolist()
#     instance.WEIGHT = parameters.Tardiness_Penalty.tolist()
#     instance.QUEUE_LIMIT = []
#     for i in range(1, parameters.Number_of_Stages):
#         instance.QUEUE_LIMIT.append(parameters.Queue_Time_Limit[i].tolist())
#     return instance

# def print_instance(instance):
#     print("JOBS_NUM: ", instance.JOBS_NUM)
#     print("STAGES_NUMBER: ", instance.STAGES_NUMBER)
#     print("MACHINES_NUM: ", instance.MACHINES_NUM)
#     print("DISCOUNT: ", instance.DISCOUNT)
#     print("MAINT_LEN: ", instance.MAINT_LEN)
#     print("REMAIN: ", instance.REMAIN)
#     print("INIT_PROD_TIME: ", instance.INIT_PROD_TIME)
#     print("DUE_TIME: ", instance.DUE_TIME)
#     print("WEIGHT: ", instance.WEIGHT)
#     print("QUEUE_LIMIT: ", instance.QUEUE_LIMIT)

instance = Instance()
order_on_machines = [[2, 4, 3, 5, 7, 6, 1, 8], [2, 4, 3, 5, 7, 6, 1, 8], ['M', 2, 4, 3, 5, 7, 6, 1, 8]]
shared_job_order = [2, 4, 3, 5, 7, 6, 1, 8]


def compute_tardiness(current_end_time, instance):
    obj = 0
    for i in range(instance.JOBS_NUM):
        if (current_end_time[i] > instance.DUE_TIME[i]):  # finished after due time
            obj += (current_end_time[i] -
                    instance.DUE_TIME[i]) * instance.WEIGHT[i]
    return obj





# function for generating schedule and computing objective value
def generate_schedule(shared_job_order, order_on_machines, instance) -> float:

    def sort_maintenance(maint_order): # TODO: sort maintenance order according to stage and machine length
        # print('maint_order', maint_order)
        job_priority = [[0, 0] for i in range(len(maint_order))]
        for i in range(len(maint_order)):
            job_priority[i][0] = maint_order[i]
            job_after_maintenance = order_on_machines[maint_order[i]][current_machine_index[maint_order[i]]+1]
            job_priority[i][1] = shared_job_order.index(job_after_maintenance) # sorting criteria: next job in shared job order
        job_priority = sorted(job_priority, key=itemgetter(1))  # sort by first value of tuple
        
        if job_priority != []: # get first element using zip, then change data type to list
            maint_order = list(list(zip(*job_priority))[0])
        
        return maint_order
    
    current_end_time = [0] * instance.JOBS_NUM
    total_machines_num = sum(instance.MACHINES_NUM)
    current_machine_time = [0] * total_machines_num
    current_machine_index = [0] * total_machines_num
    machine_has_maintained = [False] * total_machines_num

    for i in range(total_machines_num): # initialize current machine time
        current_machine_time[i] = instance.REMAIN[i]

    current_maint_time = 0
    for i in range(len(shared_job_order)):  # loop all jobs in shared job order
        maint_order = [] # store the maintenance order
        for j in range(total_machines_num): # mark all machines that need maintenance
            if (current_machine_index[j] != len(order_on_machines[j])):
                if (order_on_machines[j][current_machine_index[j]] == 'M' and current_machine_index[j] != len(order_on_machines[j])-1):
                    maint_order.append(j) # append the machine that needs maintenance
        sorted_maintenance_order = sort_maintenance(maint_order) # sort the maintenance order
        # print(sorted_maintenance_order)
        for j in range(len(sorted_maintenance_order)): # append maintenance to schedule
            maint_start_time = max(current_machine_time[sorted_maintenance_order[j]], current_maint_time)
            current_machine_time[sorted_maintenance_order[j]] = maint_start_time + instance.MAINT_LEN[sorted_maintenance_order[j]]
            current_maint_time = maint_start_time + instance.MAINT_LEN[sorted_maintenance_order[j]]
            current_machine_index[sorted_maintenance_order[j]] += 1
            machine_has_maintained[sorted_maintenance_order[j]] = True
            # print("current maint time", current_maint_time)
        # print(machine_has_maintained)
        current_job_time = [[0, 0] for i in range(instance.STAGES_NUMBER)] # initialize current job time
        
        current_job_machines = [] # get the machines job j work on
        for j in range(total_machines_num):
            if (current_machine_index[j] != len(order_on_machines[j])):
                if order_on_machines[j][current_machine_index[j]] == shared_job_order[i]: # if the machine processes the job
                    current_machine_index[j] += 1
                    current_job_machines.append(j)
        # print(current_job_machines)
        for j in range(instance.STAGES_NUMBER): # append job j's schedule together without interval
            if (j != 0):
                current_job_time[j][0] = current_job_time[j-1][1]
            machine = current_job_machines[j]
            production_time = instance.INIT_PROD_TIME[machine][shared_job_order[i]-1]
            if machine_has_maintained[machine]:
                production_time = instance.DISCOUNT[machine] * production_time
            current_job_time[j][1] = current_job_time[j][0] + production_time
        # print(current_job_time)
        overlap = current_machine_time[current_job_machines[0]]
        for j in range(instance.STAGES_NUMBER): # append (*) to stage 1 machine m 
            current_job_time[j][0] += overlap
            current_job_time[j][1] += overlap
        # print(current_job_time)
        for j in range(1, instance.STAGES_NUMBER):
            overlap = current_machine_time[current_job_machines[j]] - current_job_time[j][0]
            pushback = -1
            # print("overlap = ", overlap)
            if overlap > 0:
                pushback = min(overlap, instance.QUEUE_LIMIT[j-1][shared_job_order[i]-1])
                for k in range(j, instance.STAGES_NUMBER): # push back after stage j
                    current_job_time[k][0] += pushback
                    current_job_time[k][1] += pushback
            # print("pushback = ", pushback)
            # print(current_job_time)
            if pushback != -1 and pushback < overlap:
                pushback = overlap - pushback
                for k in range(instance.STAGES_NUMBER): # push back from stage 0
                    current_job_time[k][0] += pushback
                    current_job_time[k][1] += pushback
        # print(current_job_time)
        for j in range(instance.STAGES_NUMBER): # update current machine time
            current_machine_time[current_job_machines[j]] = current_job_time[j][1]
        current_end_time[shared_job_order[i]-1] = current_job_time[instance.STAGES_NUMBER-1][1]
    # print(current_end_time)
    obj = compute_tardiness(current_end_time, instance)
    return obj


# print(generate_schedule(shared_job_order, order_on_machines, instance))
    