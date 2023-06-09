import math
import pandas as pd
from operator import itemgetter


def compute_tardiness(current_end_time, instance):
    obj = 0
    for i in range(instance.JOBS_NUM):
        if (current_end_time[i] > instance.DUE_TIME[i]):  # finished after due time
            obj += (current_end_time[i] -
                    instance.DUE_TIME[i]) * instance.WEIGHT[i]
    return obj





# function for generating schedule and computing objective value
def generate_schedule(shared_job_order, order_on_machines, instance, instance_num, best_objective_value = 0) -> float:

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
    
    def insert_new_maintenance(current_machine_time, maintenance_length, maint_time_list):
        if (maint_time_list == []):
            maint_time_list.append([current_machine_time, current_machine_time + maintenance_length])
            return current_machine_time, maint_time_list
        if (maint_time_list[0][0] >= current_machine_time + maintenance_length): # insert to head of maint_time
            maint_time_list = [[current_machine_time, current_machine_time + maintenance_length]] + maint_time_list 
            return current_machine_time, maint_time_list
        for i in range(len(maint_time_list)-1): # insert to middle of maint_time
            if maint_time_list[i+1][0] - max(current_machine_time, maint_time_list[i][1]) >= maintenance_length:
                start_time = max(current_machine_time, maint_time_list[i][1])
                maint_time_list = maint_time_list[:i+1] + [[start_time, start_time + maintenance_length]] + maint_time_list[i+1:]
                return start_time, maint_time_list
        start_time = max(current_machine_time, maint_time_list[len(maint_time_list)-1][1]) # insert to tail of maint_time
        maint_time_list.append([start_time, start_time + maintenance_length])
        return start_time, maint_time_list
    
    current_end_time = [0] * instance.JOBS_NUM
    total_machines_num = sum(instance.MACHINES_NUM)
    current_machine_time = [0] * total_machines_num
    current_machine_index = [0] * total_machines_num
    machine_has_maintained = [False] * total_machines_num

    for i in range(total_machines_num): # initialize current machine time
        current_machine_time[i] = instance.REMAIN[i]

    maint_time_list = [] # sorted list containing the current [maintenance_start_time, maintenanace_end_time]'s
    for i in range(len(shared_job_order)):  # loop all jobs in shared job order
        maint_order = [] # store the maintenance order
        for j in range(total_machines_num): # mark all machines that need maintenance
            if (current_machine_index[j] != len(order_on_machines[j])):
                if (order_on_machines[j][current_machine_index[j]] == 'M' and current_machine_index[j] != len(order_on_machines[j])-1):
                    maint_order.append(j) # append the machine that needs maintenance
        sorted_maintenance_order = sort_maintenance(maint_order) # sort the maintenance order
        for j in range(len(sorted_maintenance_order)): # append maintenance to schedule
            maint_start_time, maint_time_list = insert_new_maintenance(current_machine_time[sorted_maintenance_order[j]], instance.MAINT_LEN[sorted_maintenance_order[j]], maint_time_list)
            current_machine_time[sorted_maintenance_order[j]] = maint_start_time + instance.MAINT_LEN[sorted_maintenance_order[j]]
            current_machine_index[sorted_maintenance_order[j]] += 1
            machine_has_maintained[sorted_maintenance_order[j]] = True
        current_job_time = [[0, 0] for i in range(instance.STAGES_NUMBER)] # initialize current job time
        
        current_job_machines = [] # get the machines job j work on
        for j in range(total_machines_num):
            if (current_machine_index[j] != len(order_on_machines[j])):
                if order_on_machines[j][current_machine_index[j]] == shared_job_order[i]: # if the machine processes the job
                    current_machine_index[j] += 1
                    current_job_machines.append(j)
        for j in range(instance.STAGES_NUMBER): 
            machine = current_job_machines[j] # get machine no, production time of current job current stage
            production_time = instance.INIT_PROD_TIME[machine][shared_job_order[i]-1]
            if machine_has_maintained[machine]:
                production_time = instance.DISCOUNT[machine] * production_time
            if j == 0: # append job j's as close to previous job as possible
                current_job_time[j][0] = current_machine_time[machine] 
            else:
                current_job_time[j][0] = max(current_machine_time[machine], current_job_time[j-1][1])
            current_job_time[j][1] = current_job_time[j][0] + production_time
            for k in range(j, 0, -1): # check previous stages violate queue time limit
                queue_limit = instance.QUEUE_LIMIT[k-1][shared_job_order[i]-1]
                shift = (current_job_time[k][0] - current_job_time[k-1][1]) - queue_limit
                if shift > 0:
                    current_job_time[k-1][0] += shift
                    current_job_time[k-1][1] += shift
                else:
                    break
        for j in range(instance.STAGES_NUMBER): # update current machine time
            current_machine_time[current_job_machines[j]] = current_job_time[j][1]
        current_end_time[shared_job_order[i]-1] = current_job_time[instance.STAGES_NUMBER-1][1]
    obj = compute_tardiness(current_end_time, instance)
    return obj
    