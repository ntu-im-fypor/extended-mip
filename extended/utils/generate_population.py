'''
TODO:
1. 檢查數字有沒有重複（有的話要往後移動） > solve!


'''



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
        self.Tardiness_Penalty = np.random.randint(1, 100, self.Number_of_Jobs)


'''
population_num=n : 對於每個方法的排列組合，都生成 n 個不同數值的解

方法：

1. pick machine
    a. 找讓 initial production time 最短的機器 A[stage][machine][job]
    b. 隨機選一個地方放
    c. 平均分配 (TODO)
    d. 讓每個機器的初始完成時間最平均(TODO)

2. decide job order (deleted)
    a. Random
    b. Weighted Penalty
    c. Due Time
    d. Due Time / Weighted Penalty
    e. Least Slack Time Ratio (先不做)

3. decide maintenance time
    a. 統一不保養
    b. 統一放最前面
    c. random

流程
1. 先決定順序
2. 再決定要放在哪裡
3. 最後放 maintenance

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



def generate_population(instance, population_num, share_job_order_list):
    stage_num = instance.Number_of_Stages
    job_num = instance.Number_of_Jobs
    machine_num = instance.Number_of_Machines
    max_machine  = max(machine_num)
    # weighted_penalty = instance.Tardiness_Penalty
    # due_time = instance.Due_Time
    initial_production_time = instance.Initial_Production_Time

    population = []
    return_value = []

    # machine_method = ['random', 'min_prod_time']
    machine_methods = ['random', 'min_prod_time']
    # maintenance_methods = ['random', 'no_maintain', 'first_place']
    maintenance_methods = ['random', 'no_maintain', 'first_place']

    job_order_dic = {} # to be deleted

    interval = 1/(job_num+1)
    offset = interval * 0.01

    # print("interval = ", interval)
    # print("offset = ", offset )


    for _ in range(population_num):
        # print(num)
        population = []

        # step 1: decide machine arrangement
        for machine_method in machine_methods:
            job_order_dic[machine_method] = []

            if(machine_method == 'random'):
                for s in range(stage_num):
                    job_order_dic[machine_method].append([])
                    for j in range(job_num):
                        chosen_machine_num = random.randint(0,machine_num[s]-1)
                        job_order_dic[machine_method][s].append(chosen_machine_num)

            if(machine_method == 'min_prod_time'):
                for s in range(stage_num):
                    job_order_dic[machine_method].append([])
                    for j in range(job_num):

                        # Step a: iterate all production time of a job in a stage

                        chosen_machine_num = 0
                        for m in range(machine_num[s]):
                            if(initial_production_time[s][m][j] >= initial_production_time[s][chosen_machine_num][j]):
                                chosen_machine_num = m

                        if(chosen_machine_num != -1):
                            job_order_dic[machine_method][s].append(chosen_machine_num)
                        else:
                            print('abnormal')

        # step 2: decide job order of each macine in each stage -> TODO: 直接用 share job order 去做

        # print("share_job_order_list = ", share_job_order_list)
        for machine_method in machine_methods:
            for share_job_order in share_job_order_list:
                # print(share_job_order)
                population.append([])
                cur_population = len(population)-1
                for s in range(stage_num):
                    population[cur_population].append([])
                    # print("share_job_order = ", share_job_order)
                    for j in range(job_num):
                        assigned_machine = job_order_dic[machine_method][s][j] + 1
                        assigned_order = share_job_order.index(j+1)
                        assigned_order_value = interval * (assigned_order+1) + assigned_machine
                        # print("assigned_order_value = ", assigned_order_value)
                        population[cur_population][s].append(assigned_order_value)

        # step 3: decide maintenance order

        for maintenance_method in maintenance_methods:
            for p in population:
                return_value.append(copy.deepcopy(p))
                cur_posi = len(return_value)-1
                if(maintenance_method == 'random'):
                    for s in range(stage_num):
                        for m in range(0, machine_num[s]):
                            cur_machine_value = round(random.uniform(m+1, m+2), 2) - offset
                            return_value[cur_posi][s].append(cur_machine_value)
                        # machine which doesn't appear in that stage
                        for m in range(machine_num[s], max_machine):
                            return_value[cur_posi][s].append(m+2-offset)

                if(maintenance_method == 'no_maintain'):
                    for s in range(stage_num):
                        for m in range(0, machine_num[s]):
                            return_value[cur_posi][s].append(m+2-offset)
                        # machine which doesn't appear in that stage
                        for m in range(machine_num[s], max_machine):
                            return_value[cur_posi][s].append(m+2-offset)


                if(maintenance_method == 'first_place'):
                    for s in range(stage_num):
                        for m in range(0, machine_num[s]):
                            return_value[cur_posi][s].append(m+1)
                        # machine which doesn't appear in that stage
                        for m in range(machine_num[s], max_machine):
                            return_value[cur_posi][s].append(m+2-offset)

    np_result = np.array(return_value)
    for i in range(len(np_result)):
        for s in range(stage_num):
            print(np_result[i][s])

    return np_result


if __name__ == "__main__":


    temp_order = [1,3,2,4]
    # print("order list")
    # print(calculate_job__order_value(temp_order))
    instance = temp()

    # create several share job order
    job_num = instance.Number_of_Jobs
    job_list = [ i+1 for i in range(job_num)]
    # print("job_list = ", job_list)
    temp_share_job_order_list = []
    for i in range(5):
        random.shuffle(job_list)
        temp_shuffle_list = job_list
        # print("temp_shuffle_list = ", temp_shuffle_list)
        temp_share_job_order_list.append(copy.deepcopy(temp_shuffle_list))

    # print("temp_share_job_order_list = ", temp_share_job_order_list)
    ans = generate_population(instance, 2, temp_share_job_order_list)


    # print('FINAL SOLUTION')
    # print("length =", len(ans) )
    # for i in range(len(ans)):
    #     for j in range(len(ans[i])):
    #         print(ans[i][j])
    #         print('\n')
    #     print("=================")
