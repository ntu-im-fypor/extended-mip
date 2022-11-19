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
    MAX_MACHINE_NUM = max(MACHINES_NUM)


def transform_parameters_to_instance(parameters: Parameters) -> Instance:
    instance = Instance()
    instance.JOBS_NUM = parameters.Number_of_Jobs
    instance.MAX_MACHINE_NUM = parameters.Max_Number_of_Machines
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

def print_instance(instance):
    print("JOBS_NUM: ", instance.JOBS_NUM)
    print("STAGES_NUMBER: ", instance.STAGES_NUMBER)
    print("MACHINES_NUM: ", instance.MACHINES_NUM)
    print("MAX_MACHINES_NUM: ", instance.MAX_MACHINES_NUM)
    print("DISCOUNT: ", instance.DISCOUNT)
    print("MAINT_LEN: ", instance.MAINT_LEN)
    print("REMAIN: ", instance.REMAIN)
    print("INIT_PROD_TIME: ", instance.INIT_PROD_TIME)
    print("DUE_TIME: ", instance.DUE_TIME)
    print("WEIGHT: ", instance.WEIGHT)
    print("QUEUE_LIMIT: ", instance.QUEUE_LIMIT)

instance = Instance()
# consider all maintenance values exist


def compute_tardiness(current_end_time, instance):
    obj = 0
    for i in range(instance.JOBS_NUM):
        if (current_end_time[i] > instance.DUE_TIME[i]):  # finished after due time
            obj += (current_end_time[i] -
                    instance.DUE_TIME[i]) * instance.WEIGHT[i]
    return obj

# returns a array of job indexes and Maintenance points (-1 表示) for the machine, ex: [-1, 0, 2, 1]


def get_job_maintenance_order_for_machine(machine, schedule, instance):
    # 目前 schedule index 是否為 job
    def isJob(index):
        return True if index < instance.JOBS_NUM else False

    l = []
    for i in range(len(schedule)):
        if math.floor(schedule[i]) == machine:  # 如果是會在此機台上被處裡的 job 或 maintenance
            # append the job being processed, else append -1 to indicate maintenance
            l.append((schedule[i], i)) if isJob(i) else l.append((schedule[i], -1))
    l = sorted(l, key=itemgetter(0))  # sort by first value of tuple

    # get first element using zip, then change data type to list
    return list(list(zip(*l))[1])


def get_stage_and_machine_index(machine_index, instance):
    m = machine_index  # m: 第幾個被處裡的機台
    stage = 0
    while m - instance.MACHINES_NUM[stage] >= 0:
        m -= instance.MACHINES_NUM[stage]
        stage += 1

    return stage, m


# function for computing objective value
# 如果 queue time limit 不滿足，回傳 -1
def calculate_objective_value(schedule, instance) -> float:
    # Array to store the current end time of each job, will update after looping each machine
    current_end_time = [0] * instance.JOBS_NUM

    # Array to store the start time and end time of each maintenance
    total_machines_num = sum(instance.MACHINES_NUM)
    maint_time = [[0, 0] for i in range(total_machines_num)]

    for i in range(total_machines_num):  # loop all machines in order
        # get the stage number and machine index for current stage of current machine
        stage, machine_stage_index = get_stage_and_machine_index(i, instance)

        current_machine_time = 0
        current_machine_time += instance.REMAIN[i]
        has_maintained = False  # 記錄機台上是否已經處理 maintainance

        job_maintenance_order = get_job_maintenance_order_for_machine(
            machine_stage_index+1, schedule[stage], instance)
        for j in range(len(job_maintenance_order)):  # loop all jobs/maintenance in order
            # if currently maintenance is processed, record start and end time of maintenance
            if (job_maintenance_order[j] == -1):
                if (j == len(job_maintenance_order)-1): # maintenance must not be processed last
                    break
                has_maintained = True
                maint_time[i][0] = current_machine_time
                current_machine_time += instance.MAINT_LEN[i]
                maint_time[i][1] = current_machine_time

            else:  # currently processing a job
                # initial production time
                production_time = instance.INIT_PROD_TIME[i][job_maintenance_order[j]]
                if (has_maintained):  # update production time if the job is after maintenance
                    production_time *= instance.DISCOUNT[i]

                production_start_time = max(
                    current_machine_time, current_end_time[job_maintenance_order[j]])
                current_end_time[job_maintenance_order[j]
                                 ] = production_start_time + production_time
                current_machine_time = production_start_time + production_time

    # Check maintenance conflict
    maint_check = [False] * total_machines_num
    maint_end_time = 0
    for i in range(total_machines_num):
        first_false = False
        for j in range(total_machines_num):
            if (maint_check[j] == False and first_false == False):
                min_start = maint_time[j][0]
                min_finish = maint_time[j][1]
                min_index = j
                first_false = True
            if (maint_check[j] == False and maint_time[j][0] < min_start):
                min_start = maint_time[j][0]
                min_finish = maint_time[j][1]
                min_index = j
        maint_check[min_index] = True
        if (min_start < maint_end_time):
            maint_time[min_index][0] = maint_end_time
            maint_time[min_index][1] = maint_end_time + \
                instance.MAINT_LEN[min_index]
        maint_end_time = maint_time[min_index][1]

    print("maintenance time of each machine: ", maint_time)

    # Reset [Array to store the current end time of each job, will update after looping each machine] for re-calculation
    current_end_time = [0] * instance.JOBS_NUM

    # Time re-calculation to eliminate maintenance conflict
    violated = False # whether queue time limit is violated
    for i in range(total_machines_num):  # loop all machines in order
        # get the stage number and machine index for current stage of current machine
        stage, machine_stage_index = get_stage_and_machine_index(i, instance)

        current_machine_time = 0
        current_machine_time += instance.REMAIN[i]
        has_maintained = False  # 記錄機台上是否已經處理 maintainance

        job_maintenance_order = get_job_maintenance_order_for_machine(
            machine_stage_index+1, schedule[stage], instance)
        for j in range(len(job_maintenance_order)):  # loop all jobs/maintenance in order
            # if currently maintenance is processed, record start and end time of maintenance
            if (job_maintenance_order[j] == -1):
                has_maintained = True
                current_machine_time = maint_time[i][1]

            else:  # currently processing a job
                # initial production time
                production_time = instance.INIT_PROD_TIME[i][job_maintenance_order[j]]
                if (has_maintained):  # update production time if the job is after maintenance
                    production_time *= instance.DISCOUNT[i]

                production_start_time = max(
                    current_machine_time, current_end_time[job_maintenance_order[j]])

                if (stage != 0):  # for all the stages excluding first stage, we check jobs que time limit
                    # save the job end time of previous stage
                    prev_stage_end_time = current_end_time[job_maintenance_order[j]]
                    # check if violates queue time limit
                    if (production_start_time - prev_stage_end_time > instance.QUEUE_LIMIT[stage-1][job_maintenance_order[j]]):
                        violated =  True

                current_end_time[job_maintenance_order[j]
                                 ] = production_start_time + production_time
                current_machine_time = production_start_time + production_time
        print("end time of jobs on stage ", stage + 1, "machine ", machine_stage_index+1)
        print(current_end_time)

    if violated:
        return -1
    obj = compute_tardiness(current_end_time, instance)
    return obj
