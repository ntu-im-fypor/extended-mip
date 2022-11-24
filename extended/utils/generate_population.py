# from Models import Parameters
import random
import numpy as np
import copy


def print_job_order_method(job_order_dic, stage_num, job_num):
    for i in job_order_dic:
        print(i)
        print('==================')
        print(job_order_dic[i])
        print('==================')
        for j in range(stage_num):
            print("stage = ", j)
            for k in range(job_num):
                print("job num = ", k)
                print("arranged machine = ", job_order_dic[i][j][k])
                print('------------')

    print('END JOB MACHINE ARRANGEMENT PRINT')


class temp():
    def __init__(self):
        self.Number_of_Stages = 5
        self.Number_of_Jobs = 4
        self.Number_of_Machines = [3,5,6,3,5]
        self.max_machine_num = max(self.Number_of_Machines)
        self.Initial_Production_Time = np.random.randint(1, 100, size=((self.Number_of_Stages, self.max_machine_num, self.Number_of_Jobs)))
        self.Due_Time = np.random.randint(1, 100, self.Number_of_Jobs)
        self.WEIGHT = np.random.randint(1, 100, self.Number_of_Jobs)


'''
population_num=n : 對於每個方法的排列組合，都生成 n 個不同數值的解

方法：
2: determined method
- 找讓 initial production time 最短的機器 A[stage][machine][job]
- WEDD
- 兩種 maintenance 方法
    統一部保養
    統一放最前面
1: greedy method (tbd)
27: random


'''

# TODO: add input: n * job_num

# 將 job 順序轉換成小數點 array
def calculate_job__order_value(order_array):
    interval = 1/ (len(order_array)+1)
    result = []
    for i in range(len(order_array)):
        cur_index = order_array.index(i+1)
        result.append(interval * (cur_index+1))
    return result



def generate_population(instance, population_num = 30):

    # population number has to be greater than or euqal to 3
    if(population_num < 3):
        return 0

    # =================== Get parameters from instance ===================
    stage_num = instance.Number_of_Stages
    job_num = instance.Number_of_Jobs
    machine_num = instance.Number_of_Machines
    max_machine  = max(machine_num)
    initial_production_time = instance.Initial_Production_Time
    weight = instance.WEIGHT
    due_time = instance.Due_Time

    interval = 1/(job_num+1)
    offset = interval * 0.000001

    return_value = []

    # =================== calculate WEDD ===================
    WEDD = []
    sorted_WEDD = []
    for i in range(len(due_time)):
        WEDD.append(due_time[i]/weight[i])
        sorted_WEDD.append(due_time[i]/weight[i])
    sorted_WEDD.sort()
    job_order = []
    for i in sorted_WEDD:
        job_order.append(WEDD.index(i)+1)


    # =================== generate two determined solution ===================

    # a. 計算 min production time machine arrangement
    machine_assignment = []
    for s in range(stage_num):
        machine_assignment.append([])
        for j in range(job_num):
            chosen_machine_num = 0
            for m in range(machine_num[s]):
                if(initial_production_time[s][m][j] >= initial_production_time[s][chosen_machine_num][j]):
                    chosen_machine_num = m
            machine_assignment[s].append(chosen_machine_num)



    # b. 以 WEDD 作為順序依據
    designated_job_schedule = []
    for s in range(stage_num):
        designated_job_schedule.append([])
        for j in range(job_num):
            assigned_machine = machine_assignment[s][j] + 1
            assigned_order = job_order.index(j+1)
            assigned_order_value = interval * (assigned_order+1) + assigned_machine
            designated_job_schedule[s].append(assigned_order_value)


    # c. 加入 maintenance schedule (都在最前面做 & 都不做)
    maintenance_methods = ['no_maintain', 'first_place']
    for maintenance_method in maintenance_methods:
        return_value.append(copy.deepcopy(designated_job_schedule))
        cur_posi = len(return_value)-1
        if(maintenance_method == 'no_maintain'):
            for s in range(stage_num):
                for m in range(0, max_machine):
                    return_value[cur_posi][s].append(m+2-offset)


        if(maintenance_method == 'first_place'):
            for s in range(stage_num):
                for m in range(0, machine_num[s]):
                    return_value[cur_posi][s].append(m+1)
                # machine which doesn't appear in that stage
                for m in range(machine_num[s], max_machine):
                    return_value[cur_posi][s].append(m+2-offset)


    # =================== append greedy solution into population: TODO ===================

    # =================== generate random population ===================

    for _ in range(population_num-2):
        # assign machine to each job in each stage
        machine_assignment = []
        for s in range(stage_num):
            machine_assignment.append([])
            for j in range(job_num):
                chosen_machine_num = random.randint(0,machine_num[s]-1)
                machine_assignment[s].append(chosen_machine_num)

        # decide the order by WEDD
        job_schedule = []
        for s in range(stage_num):
            job_schedule.append([])
            for j in range(job_num):
                assigned_machine = machine_assignment[s][j] + 1
                assigned_order = job_order.index(j+1)
                assigned_order_value = interval * (assigned_order+1) + assigned_machine
                job_schedule[s].append(assigned_order_value)

        # decide the maintenance schedile randomly
        for s in range(stage_num):
            for m in range(0, machine_num[s]):
                cur_machine_value = random.uniform(m+1, m+2)
                job_schedule[s].append(cur_machine_value)
            # machine which doesn't appear in that stage
            for m in range(machine_num[s], max_machine):
                job_schedule[s].append(m+2-offset)
        return_value.append(copy.deepcopy(job_schedule))




    np_result = np.array(return_value)

    return np_result


if __name__ == "__main__":


    temp_order = [1,3,2,4]
    instance = temp()

    # create several share job order
    job_num = instance.Number_of_Jobs
    job_list = [ i+1 for i in range(job_num)]

    ans = generate_population(instance, 5)


    print('FINAL SOLUTION')
    print("length =", len(ans) )
    for i in range(len(ans)):
        for j in range(len(ans[i])):
            print(ans[i][j])
            print('\n')
        print("=================")
