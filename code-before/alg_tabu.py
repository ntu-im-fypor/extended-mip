import pandas as pd
import numpy as np
import math
import copy
from tqdm import tqdm, trange
from collections import namedtuple
from itertools import combinations

from alg_joblisting import InitSchedule

scenario_list = ['benchmark']
stage_list = ['stage1_start', 'stage1_end', 'stage2_start', 'stage2_end', 'stage3_start', 'stage3_end',
              'stage4_start', 'stage4_end', 'stage5_start', 'stage5_end']
index_thirty = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
index_tewnty = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]

# Create empty dataframes to store maint_time
maint_df = pd.DataFrame(columns=stage_list, index=index_thirty)
job_df = pd.DataFrame(columns=stage_list, index=index_tewnty)

class JointScheduleProb:
    def __init__(self, initSched: InitSchedule) -> None:
        self.Data = initSched.Data
        self.scheduled_job_id = initSched.scheduled_job  # n_j: 1-n_j
        # self.scheduled_maint_pos = np.ones(self.Data.n_i) * (self.Data.n_j)  # n_i: 0 在第一個工作前 初始為最後才維修
        self.scheduled_maint_pos = np.zeros(self.Data.n_i)  # 初始為一開始就維修
        # self.duration = np.zeros((self.Data.n_i, self.Data.n_j+1))  # 有考慮是否維修 [:, -1] 為 F_i
        # self.shift = np.zeros(self.Data.n_i)

    def cal_time_state(self) -> None:
        '''
        按順序排列出每個工作所需時間
        '''
        self.time_state = np.zeros((self.Data.n_i, self.Data.n_j+1))  # [:, -1] 為維修後時間
        self.time_state_start = np.zeros((self.Data.n_i, self.Data.n_j+1))
        if self.first_check == True:
            self.maint_period = np.zeros((self.Data.n_i, 2))  # 記錄維修開始與結束
        for machine_order, maint_pos in enumerate(self.scheduled_maint_pos):
            maint = False
            for job_pos, job_id in enumerate(self.scheduled_job_id):
                # check duration
                if maint_pos > job_pos:  # 沒維修
                    duration = self.Data.INIT_PROD_TIME[machine_order+1, job_id]
                else:  # 維修
                    duration = self.Data.AFTER_DIS_PROD_TIME[machine_order+1, job_id]
                    if maint_pos == job_pos:
                        if self.maint_period[machine_order][0] < self.time_state[machine_order][job_pos-1] and self.first_check == False and maint_pos != 0:
                            self.fix_maint = True
                            self.maint_period[machine_order][0] = self.time_state[machine_order][job_pos-1]
                            self.maint_period[machine_order][1] = self.time_state[machine_order][job_pos-1] + self.Data.MAINT_LEN[machine_order+1]
                            return
                        elif self.maint_period[machine_order][0] < self.Data.REMAIN[machine_order+1] and maint_pos == 0:
                            self.fix_maint = True
                            self.maint_period[machine_order][0] = self.Data.REMAIN[machine_order+1]
                            self.maint_period[machine_order][1] = self.Data.REMAIN[machine_order+1] + self.Data.MAINT_LEN[machine_order+1]
                            return
                        maint = True  # 轉成維修點

                # check before state
                if job_pos == 0:  # 各機台第一個 job
                    if machine_order == 0:
                        if maint:  # 若剛修 maint = T
                            if self.first_check == True:
                                self.time_state[machine_order][-1] = self.Data.REMAIN[machine_order+1] + self.Data.MAINT_LEN[machine_order+1]
                                start_maint = self.Data.REMAIN[machine_order+1]
                            else:
                                self.time_state[machine_order][-1] = self.maint_period[machine_order][1]
                            before_state = self.time_state[machine_order][-1]
                        else:
                            before_state = self.Data.REMAIN[machine_order+1]
                    else:
                        if maint:  # 若剛修 maint = T
                            if self.first_check == True:
                                self.time_state[machine_order][-1] = self.Data.REMAIN[machine_order+1] + self.Data.MAINT_LEN[machine_order+1]
                                start_maint = self.Data.REMAIN[machine_order+1]
                            else:
                                self.time_state[machine_order][-1] = self.maint_period[machine_order][1]
                            before_state = max(self.time_state[machine_order][-1], self.time_state[machine_order-1][job_pos])
                        else:
                            before_state = max(self.Data.REMAIN[machine_order+1], self.time_state[machine_order-1][job_pos])
                elif machine_order == 0:  # 第一個機台
                    if maint:  # 若剛修 maint = T
                        if self.first_check == True:
                            self.time_state[machine_order][-1] = self.time_state[machine_order][job_pos-1] + self.Data.MAINT_LEN[machine_order+1]
                            start_maint = self.time_state[machine_order][job_pos-1]
                        else:
                            self.time_state[machine_order][-1] = self.maint_period[machine_order][1]
                        before_state = self.time_state[machine_order][-1]
                    else:  # 前個 state 為維修後的時間
                        before_state = self.time_state[machine_order][job_pos-1]
                else:
                    if maint:  # 若剛修 維修後的時間 和上個機台 job 結束時間比較
                        if self.first_check == True:
                            self.time_state[machine_order][-1] = self.time_state[machine_order][job_pos-1] + self.Data.MAINT_LEN[machine_order+1]
                            start_maint = self.time_state[machine_order][job_pos-1]
                        else:
                            self.time_state[machine_order][-1] = self.maint_period[machine_order][1]
                        before_state = max(self.time_state[machine_order][-1], self.time_state[machine_order-1][job_pos])
                    else:
                        before_state = max(self.time_state[machine_order][job_pos-1], self.time_state[machine_order-1][job_pos])

                self.time_state_start[machine_order][job_pos] = before_state
                self.time_state[machine_order][job_pos] = before_state + duration

                if maint and self.first_check == True:
                    self.maint_period[machine_order][0] = start_maint
                    self.maint_period[machine_order][1] = self.time_state[machine_order][-1]

                maint = False

                # print(self.time_state)

    def check_maint_one_at_a_time(self) -> None:
        # 機台與機台間 維修的先後順序
        maint_seq = np.argsort(self.maint_period[:, 0])
        # maint_seq[rank] 第 rank-1 名的 index = machine_order
        for rank in range(self.Data.n_i - 1):
            # 第二名開始 小於（更改維修時間）/大於等於（正常） 第一名結束
            if self.maint_period[maint_seq[rank+1]][0] < self.maint_period[maint_seq[rank]][1]:
                self.fix_maint = True
                self.maint_period[maint_seq[rank+1]][0] = self.maint_period[maint_seq[rank]][1]
                self.maint_period[maint_seq[rank+1]][1] = self.maint_period[maint_seq[rank+1]][1] + self.Data.MAINT_LEN[maint_seq[rank+1]+1]
        while self.fix_maint == True:
            self.fix_maint = False
            maint_seq = np.argsort(self.maint_period[:, 0])
            for rank in range(self.Data.n_i - 1):
                if self.maint_period[maint_seq[rank+1]][0] < self.maint_period[maint_seq[rank]][1]:
                    self.maint_period[maint_seq[rank+1]][0] = self.maint_period[maint_seq[rank]][1]
                    self.maint_period[maint_seq[rank+1]][1] = self.maint_period[maint_seq[rank+1]][1] + self.Data.MAINT_LEN[maint_seq[rank+1]+1]
            self.cal_time_state()

        # print(self.time_state)

        # 確認一個時間點只能一個機台維修 self.check_maint = T 為正確
        # for machine_order in range(self.Data.n_i):
        #     self.check_maint = ((self.maint_period[machine_order][0] <= self.maint_period[machine_order+1:]) == (
        #         self.maint_period[machine_order][1] <= self.maint_period[machine_order+1:])).all()
        #     if not self.check_maint:
        #         break

    def obj_value(self, instance_num) -> float:
        self.first_check = True
        self.fix_maint = False
        self.cal_time_state()
        self.first_check = False
        self.check_maint_one_at_a_time()
        value = 0
        for job_pos, job_id in enumerate(self.scheduled_job_id):
            value += max(self.time_state[-1][job_pos] - self.Data.DUE_TIME[job_id], 0) * self.Data.WEIGHT[job_id]

        # 若要紀錄 schedule 可以使用
    
        # for i in range(5):
        #     maint_df[stage_list[2*i]][instance_num] = self.maint_period[i][0]
        #     maint_df[stage_list[2*i+1]][instance_num] = self.maint_period[i][1]

        # for i in range(5):
        #     for j in range(20):
        #         job_df[stage_list[2*i]][j+1] = self.time_state_start[i][j]
        #         job_df[stage_list[2*i+1]][j+1] = self.time_state[i][j]
        
        # maint_df.to_csv('experiment/record/heuristic_update_test/maint_time_benchmarks.csv')
        # job_df.to_csv('experiment/record/heuristic_update_test/job_time_benchmark_' + str(instance_num) + '.csv')

        return value

Move = namedtuple('Tabu', ['job_pos1', 'job_id1', 'job_pos2', 'job_id2'])

class TabuSearch:
    def __init__(
        self, prob: JointScheduleProb, tabu_size,
        iter_num=50, after_iter=None, maint_iter_num=10, maint_mode='rij_insert_maint', instance_num=0) -> None:

        self.prob = prob
        self.Data = prob.Data
        # self.scheduled_job_id = prob.scheduled_job_id
        # self.scheduled_maint_pos = prob.scheduled_maint_pos
        self.iter_num = iter_num
        self.tabu_size = tabu_size
        self.after_iter = after_iter
        self.maint_iter_num = maint_iter_num
        self.maint_mode = maint_mode
        self.instance_num = instance_num

        self.reset()


    def reset(self):
        self.iter = 0
        self.tabu_list = []

        # all combination of swapped index
        self.candidate_swapped_index = list(combinations(list(range(self.Data.n_j)), 2))
        self.candidate_count = len(self.candidate_swapped_index)

        # initialize solution
        self.current_sol = copy.deepcopy(self.prob.scheduled_job_id)
        self.best_sol = copy.deepcopy(self.current_sol)
        self.best_val = self.prob.obj_value(self.instance_num)
        self.best_maint_sol = copy.deepcopy(self.prob.scheduled_maint_pos)

        self.scheduled_maint_pos = copy.deepcopy(self.prob.scheduled_maint_pos)

        # record best value for plot
        self.best_value_in_iteration = []
        self.best_value_in_history = []



    def swap_move(self, sol, move):
        # swap index
        sol[move.job_pos1], sol[move.job_pos2] = sol[move.job_pos2], sol[move.job_pos1]
        self.prob.scheduled_job_id = copy.deepcopy(sol)
        return

    def run_with_maint(self, instance_num):
        # !0808
        self.run()
        self.last_best_val = copy.deepcopy(self.best_val)
        same_val_count = 0
        print(self.best_val, self.last_best_val, same_val_count)

        # for iter in range(self.maint_iter_num):
        while same_val_count < self.maint_iter_num:
            if self.maint_mode == 'greedy_maint':
                self.greedy_maint(instance_num)
            elif self.maint_mode == 'rij_insert_maint':
                self.rij_insert_maint()
            elif self.maint_mode == 'random_maint':
                self.random_maint()
            elif self.maint_mode == 'distributed_maint':
                self.distributed_maint()
            elif self.maint_mode == 'all_maint':
                self.all_maint()
            print(f'- Try MaintPos: {self.scheduled_maint_pos}')

            # !0808
            self.run()

            if (self.best_val == self.last_best_val):
                same_val_count += 1
            else:
                self.last_best_val = copy.deepcopy(self.best_val)
                same_val_count = 0
            print(self.best_val, self.last_best_val, same_val_count)


    def run(self):
        # 記錄上一個最佳解
        last_best_sol = copy.deepcopy(self.best_sol)
        for iter in range(self.iter_num):
            self.run_one_iter(iter, self.instance_num)
            # !
            # if self.best_val == 0:
            #     break
        if (self.best_sol == last_best_sol).all():
            # 分前半後半 shuffle
            np.random.shuffle(last_best_sol[:int(self.Data.n_j/2)])
            np.random.shuffle(last_best_sol[int(self.Data.n_j/2):])
            self.prob.scheduled_job_id = copy.deepcopy(last_best_sol)
        else:
            self.prob.scheduled_job_id = copy.deepcopy(self.best_sol)



    def run_one_iter(self, iter, instance_num):
        self.current_sol = copy.deepcopy(self.prob.scheduled_job_id)
        neighbor_best_val = math.inf
        neighbor_best_sol = None
        neighbor_best_move = None

        non_tabu_neighbor_best_val = math.inf
        non_tabu_neighbor_best_move = None

        candidate_swapped_pbar = tqdm(self.candidate_swapped_index, position=0, leave=True)

        for swapped_index in candidate_swapped_pbar:
            job_pos1, job_pos2 = swapped_index
            move = Move(job_pos1, self.current_sol[job_pos1], job_pos2, self.current_sol[job_pos2])

            neighbor_sol = copy.deepcopy(self.current_sol)
            self.swap_move(neighbor_sol, move)
            neighbor_value = self.prob.obj_value(instance_num)


            #check if it is in tabu
            violated = False
            for tabu_move in self.tabu_list:
                if (tabu_move.job_pos1 == job_pos1 and tabu_move.job_id1 == neighbor_sol[job_pos1] and \
                    tabu_move.job_pos2 == job_pos2 and tabu_move.job_id2 == neighbor_sol[job_pos2]):
                    violated = True
                    break

            if neighbor_value < neighbor_best_val:
                neighbor_best_val = neighbor_value
                neighbor_best_sol = copy.deepcopy(neighbor_sol)
                neighbor_best_move = move

            if not violated and neighbor_value < non_tabu_neighbor_best_val:
                non_tabu_neighbor_best_val = neighbor_value
                non_tabu_neighbor_best_move = move

            candidate_swapped_pbar.set_description(f'Iter {iter+1}/{self.iter_num}')
            candidate_swapped_pbar.set_postfix({'best_val': f'{neighbor_best_val:.4f}'})

        # udpate
        # better than aspiration level
        if (neighbor_best_val < self.best_val):
            self.best_val = neighbor_best_val
            self.best_sol = neighbor_best_sol
            self.best_maint_sol = copy.deepcopy(self.prob.scheduled_maint_pos)

            # udpate move
            self.swap_move(self.current_sol, neighbor_best_move)

            # remove if it is in tabu list
            if move in self.tabu_list:
                self.tabu_list.remove(move)
            # insert to head
            self.tabu_list.insert(0, neighbor_best_move)

        else :
            # udpate move
            self.swap_move(self.current_sol, non_tabu_neighbor_best_move)
            self.tabu_list.append(non_tabu_neighbor_best_move)

        # save best value
        self.best_value_in_iteration.append(neighbor_best_val)
        self.best_value_in_history.append(self.best_val)

        if len(self.tabu_list) > self.tabu_size:
            self.tabu_list.pop()

        self.iter += 1

        if self.after_iter:
            self.after_iter(self)

    def greedy_maint(self, instance_num):
        count, no_change = 0, 0

        # for machine_order, maint_pos in enumerate(self.scheduled_maint_pos):
        min_temp_value, temp_value, temp_scheduled_maint_pos = math.inf, math.inf, copy.deepcopy(self.scheduled_maint_pos)
        origin_scheduled_maint_pos = copy.deepcopy(self.scheduled_maint_pos)
        while no_change != self.Data.n_i:
            machine_order = count % self.Data.n_i
            last_origin_scheduled_maint_pos = copy.deepcopy(temp_scheduled_maint_pos)
            for pos in range(self.Data.n_j):
                self.scheduled_maint_pos[machine_order] = pos
                self.prob.scheduled_maint_pos = copy.deepcopy(self.scheduled_maint_pos)
                temp_value = self.prob.obj_value(instance_num)
                # print(machine_order, pos, temp_value)
                if temp_value < min_temp_value:
                    min_temp_value = temp_value
                    temp_scheduled_maint_pos = copy.deepcopy(self.scheduled_maint_pos)
            self.scheduled_maint_pos = copy.deepcopy(temp_scheduled_maint_pos)
            self.prob.scheduled_maint_pos = copy.deepcopy(self.scheduled_maint_pos)
            # self.best_val = min_temp_value
            if (last_origin_scheduled_maint_pos == temp_scheduled_maint_pos).all():
                no_change += 1
            else:
                no_change = 0
            count += 1

        if (origin_scheduled_maint_pos == temp_scheduled_maint_pos).all() or (self.best_maint_sol == temp_scheduled_maint_pos).all():
            try:
                if (self.best_sol == self.last_scheduled_job_id).all():
                    self.scheduled_maint_pos = np.random.randint(self.Data.n_j+1, size=self.Data.n_i)
                    self.prob.scheduled_maint_pos = copy.deepcopy(self.scheduled_maint_pos)
            except:
                pass
        self.last_scheduled_job_id = copy.deepcopy(self.best_sol)



    def rij_insert_maint(self):  # 0309 插入維修方法
        for machine_order, maint_pos in enumerate(self.scheduled_maint_pos):
            # 0,1,2 machine id-1 / 3,2,6 maint 位置
            # 最大化 m_profit R_ij, 插入位置
            max_temp_value, temp_value, temp_pos = -math.inf, 0, self.Data.n_j
            for job_back_pos, job_id in enumerate(self.current_sol[::-1]):
                # 0,1,2 job 位置 / 3,2,7 job id
                temp_value += self.Data.M_PROFIT[machine_order+1, job_id]
                # avg_temp_value = temp_value/(job_back_pos+1)
                # self.Data.AFTER_DIS_SAVE_TIME[machine_order+1, job_id] / self.Data.MAINT_LEN[machine_order+1]
                if temp_value > max_temp_value:
                    max_temp_value = temp_value
                    temp_pos = self.Data.n_j - 1 - job_back_pos
            self.scheduled_maint_pos[machine_order] = temp_pos
            self.prob.scheduled_maint_pos = copy.deepcopy(self.scheduled_maint_pos)


    def random_maint(self):  # 0325 隨機插入維修 / 新 benchmark
        self.scheduled_maint_pos = np.random.randint(self.Data.n_j+1, size=self.Data.n_i)
        self.prob.scheduled_maint_pos = copy.deepcopy(self.scheduled_maint_pos)

    def distributed_maint(self):  # 0325 根據 \sum_{j \in J} A_{ij}*B_i / F_i 決定三角分佈
        self.scheduled_maint_pos = np.round_(np.random.triangular(
            left=0, mode=list(self.Data.MODE_AFTER_DIS_SAVE_TIME_DIV_MAINT.values()), right=self.Data.n_j))
        self.prob.scheduled_maint_pos = copy.deepcopy(self.scheduled_maint_pos)


    def all_maint(self):
        self.scheduled_maint_pos = np.zeros(self.Data.n_i)
        self.prob.scheduled_maint_pos = copy.deepcopy(self.scheduled_maint_pos)