from operator import itemgetter
import model_cls as model
from alg_joblisting import InitSchedule
from alg_tabu import JointScheduleProb, TabuSearch

import numpy as np
import pandas as pd
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn')
# plt.switch_backend('agg')

def output_message(tabu_search):
    # print(f'=====Itieration {tabu_search.iter}=====')
    print(f'Best Solution: {tabu_search.best_sol}')
    print(f'Best MaintPos Solution: {tabu_search.best_maint_sol}')
    print(f'Best Value: {tabu_search.best_val: .4f}')

factors_key = ['init_prod_time', 'prod_discount', 'weight', 'due_time', 'maint_len']

scenario_list = ['benchmark']
# for key in factors_key:
#     for level in ['L', 'H']:
#         scenario_list.append(key + '_' + level)

# read data
# data_path = 'code/scenario/'
# num = 1
# scenario = scenario_list[0]
# print(scenario + '_' + str(num))
# full_path = data_path + scenario + '/' + scenario + '_' + str(num) + '.txt'

def run_scen(
    title, jobinit_mode='due_sort', instance_num=10, scenario_list=scenario_list,
    tabu_size=5, iter_num=20, maint_iter_num=10, maint_mode='rij_insert_maint',
    data_path='experiment/scenario/final(6,100)/', save_path='code/record/tabu/', discount_reverse=None,
    use_tabu=True) -> None:

    obj_df = pd.DataFrame(index=range(1, instance_num+1))
    runtime_df = pd.DataFrame(index=range(1, instance_num+1))
    sol_df = pd.DataFrame(index=range(1, instance_num+1))
    maint_sol_df = pd.DataFrame(index=range(1, instance_num+1))
    iter_df = pd.DataFrame(index=range(1, instance_num+1))
    history_best_df = pd.DataFrame(index=range(1, instance_num+1))

    for scenario in scenario_list:
        obj_list = []
        runtime_list = []
        sol_list = []
        maint_sol_list = []
        iter_list = []
        history_best_list = []
        for num in range(1, instance_num+1):
            # if num in [18]:
            #     obj_list.append(-1)
            #     runtime_list.append(-1)
            #     sol_list.append(-1)
            #     maint_sol_list.append(-1)
            #     iter_list.append([])
            #     history_best_list.append([])
            #     continue
            print('='*100)
            print('='*100)
            if discount_reverse != None:
                if discount_reverse:
                    print('upstreamdiscount_L' + '_' + str(num))
                else:
                    print('upstreamdiscount_H' + '_' + str(num))
            else:
                print(scenario + '_' + str(num))

            full_path = data_path + scenario + '/' + scenario + '_' + str(num) + '.txt'
            # 讀資料
            data = model.Data()
            data.read_data(in_path=full_path, discount_reverse=discount_reverse)

            # init job schedule
            sched_init = InitSchedule(data)
            if jobinit_mode == 'due_weight_sort':
                sched_init.due_weight_sort()
            elif jobinit_mode == 'init_prod_time_sort':
                sched_init.init_prod_time_sort()
            elif jobinit_mode == 'due_sort':
                sched_init.due_sort()
            else:
                sched_init.due_initprodtime_sort()

            # 初始化問題
            sched = JointScheduleProb(sched_init)
            obj_value = sched.obj_value(num)
            # print(obj_value)
            if use_tabu:
                start_time = time.time()
                tabu = TabuSearch(
                    prob=sched, tabu_size=tabu_size, iter_num=iter_num,
                    after_iter=output_message, maint_iter_num=maint_iter_num, maint_mode=maint_mode, instance_num=num)

                tabu.run_with_maint(instance_num=num)

                obj_list.append(tabu.best_val)
                runtime_list.append(time.time() - start_time)
                sol_list.append(tabu.best_sol)
                maint_sol_list.append(tabu.best_maint_sol)
                iter_list.append([tabu.best_value_in_iteration])
                history_best_list.append([tabu.best_value_in_history])
            else:
                obj_list.append(obj_value)

            # plt.figure(figsize=(8, 6))
            # plt.plot(tabu.best_value_in_iteration, marker='o')
            # plt.plot(tabu.best_value_in_history, marker='o')
            # plt.legend(['Best In Iteration', 'Best In History'], loc='upper right')
            # plt.xlabel('Iteration', fontsize=16)
            # plt.ylabel('Objective Value', fontsize=16)
            # plt.title(title, fontsize=22)
            # plt.savefig(save_path + title + f'_{num}.png')
            # plt.show(block=False)
            # plt.pause(1)
            # plt.close()
        if discount_reverse != None:
            if discount_reverse:
                scenario = 'upstreamdiscount_L' # True 老在上
            else:
                scenario = 'upstreamdiscount_H'

        obj_df[scenario] = obj_list
        if use_tabu:
            runtime_df[scenario] = runtime_list
            sol_df[scenario] = sol_list
            maint_sol_df[scenario] = maint_sol_list
            iter_df[scenario] = iter_list
            history_best_df[scenario] = history_best_list

    obj_df.to_csv(save_path + title + '_obj.csv', index=False)
    if use_tabu:
        runtime_df.to_csv(save_path + title + '_runtime.csv', index=False)
        sol_df.to_csv(save_path + title + '_sol.csv', index=False)
        maint_sol_df.to_csv(save_path + title + '_maint_sol.csv', index=False)
        iter_df.to_csv(save_path + title + '_iter.csv', index=False)
        history_best_df.to_csv(save_path + title + '_history_best.csv', index=False)

'''
jobinit_mode: due_sort, dueweight_sort, dueinitprodtime_sort, init_prod_time_sort
maint_mode: greedy_maint, rij_insert_maint, random_maint, distributed_maint, all_maint
'''


save_path='experiment/record/heuristic_update/final/'
# scenario_list = ['prod_discount_H']



# run_scen(title='init_prod_time_notabu', jobinit_mode='init_prod_time_sort', instance_num=30, \
#     scenario_list=scenario_list[:1], tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='all_maint', use_tabu=False)
# run_scen(title='due_weight_notabu', jobinit_mode='due_weight_sort', instance_num=30, \
#     scenario_list=scenario_list[:1], tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='all_maint', use_tabu=False)
# run_scen(title='due_notabu', jobinit_mode='due_sort', instance_num=30, \
#     scenario_list=scenario_list[:1], tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='all_maint', use_tabu=False)
# run_scen(title='dueinitprodtime_notabu', jobinit_mode='dueinitprodtime_sort', instance_num=30, \
#     scenario_list=scenario_list[:1], tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='all_maint', use_tabu=False)


# run_scen(title='dueweight_greedy_noswapping', jobinit_mode='due_weight_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='greedy_maint', use_tabu=True, save_path=save_path)

run_scen(
    title='single_machine_inf_queue_time', jobinit_mode='due_weight_sort', instance_num=30,
    scenario_list=['queue_time_H'], tabu_size=5, iter_num=20, maint_iter_num=10,
    maint_mode='greedy_maint', use_tabu=True, discount_reverse=True,
    data_path="transformed_params/",
    save_path="code-before-single-machine-inf-queue-time/"
    )
# run_scen(title='due_greedy_upstream_L', jobinit_mode='due_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='greedy_maint', use_tabu=True, save_path=save_path, discount_reverse=True)
# run_scen(title='dueinitprodtime_greedy_upstream_L', jobinit_mode='dueinitprodtime_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='greedy_maint', use_tabu=True, save_path=save_path, discount_reverse=True)

# run_scen(title='dueweight_random_upstream_L', jobinit_mode='due_weight_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='random_maint', use_tabu=True, save_path=save_path, discount_reverse=True)
# run_scen(title='due_random_upstream_L', jobinit_mode='due_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='random_maint', use_tabu=True, save_path=save_path, discount_reverse=True)
# run_scen(title='dueinitprodtime_random_upstream_L', jobinit_mode='dueinitprodtime_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='random_maint', use_tabu=True, save_path=save_path, discount_reverse=True)

# run_scen(title='dueweight_rij_upstream_L', jobinit_mode='due_weight_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='rij_insert_maint', use_tabu=True, save_path=save_path, discount_reverse=True)
# run_scen(title='due_rij_upstream_L', jobinit_mode='due_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='rij_insert_maint', use_tabu=True, save_path=save_path, discount_reverse=True)
# run_scen(title='dueinitprodtime_rij_upstream_L', jobinit_mode='dueinitprodtime_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='rij_insert_maint', use_tabu=True, save_path=save_path, discount_reverse=True)

# run_scen(title='dueweight_distributed_upstream_L', jobinit_mode='due_weight_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='distributed_maint', use_tabu=True, save_path=save_path, discount_reverse=True)
# run_scen(title='due_distributed_upstream_L', jobinit_mode='due_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='distributed_maint', use_tabu=True, save_path=save_path, discount_reverse=True)
# run_scen(title='dueinitprodtime_distributed_upstream_L', jobinit_mode='dueinitprodtime_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='distributed_maint', use_tabu=True, save_path=save_path, discount_reverse=True)

# run_scen(title='dueweight_all_upstream_L', jobinit_mode='due_weight_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='all_maint', use_tabu=True, save_path=save_path, discount_reverse=True)
# run_scen(title='due_all_upstream_L', jobinit_mode='due_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='all_maint', use_tabu=True, save_path=save_path, discount_reverse=True)
# run_scen(title='dueinitprodtime_all_upstream_L', jobinit_mode='dueinitprodtime_sort', instance_num=30, \
#     scenario_list=scenario_list, tabu_size=5, iter_num=20, maint_iter_num=10,
#     maint_mode='all_maint', use_tabu=True, save_path=save_path, discount_reverse=True)