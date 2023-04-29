from platform import machine
from random import sample
from numpy import random
import numpy as np
from scipy import stats
import os
import copy


def pos_normal(mu, sigma):
    x = np.random.normal(mu, sigma, 1)
    return (x if x > 0 else pos_normal(mu, sigma))


class Create:
    def __init__(self, factors: dict) -> None:
        self.factors = factors
        self.init_prod_time_set = factors['init_prod_time']
        self.weight_set = factors['weight']
        self.prod_discount_set = factors['prod_discount']
        self.maint_len_set = factors['maint_len']['M']
        self.due_time_set = factors['due_time']['M']
        self.remain = self.factors['remain']
        self.queue_time_set = self.factors['queue_time']['M']
        self.bottleneck = self.factors['bottleneck']['M']
        self.file = 'base'

    def scenario(self, factor_name: str, level='M') -> str:
        self.file = str(factor_name) + '_' + level

        self.maint_len_set = factors['maint_len']['M']
        self.due_time_set = factors['due_time']['M']
        self.queue_time_set = self.factors['queue_time']['M']
        self.bottleneck = self.factors['bottleneck']['M']

        if factor_name == 'maint_len':
            self.maint_len_set = self.factors['maint_len'][level]
        elif factor_name == 'due_time':
            self.due_time_set = self.factors['due_time'][level]
        elif factor_name == 'queue_time' and level != 'H':
            self.queue_time_set = self.factors['queue_time'][level]
        elif factor_name == 'bottleneck':
            self.bottleneck = self.factors['bottleneck'][level]

    def sample(self):
        self.STAGE_NUM = 3
        self.JOB_NUM = 15
        self.MACHINE_NUM = [2, 2, 2]
        self.TOTAL_MACHINE_NUM = np.sum(self.MACHINE_NUM)

        # INIT_PROD_TIME
        machine_status = random.uniform(0.7, 1, size=self.TOTAL_MACHINE_NUM)
        tmp_prod_time = random.randint(self.init_prod_time_set[0], self.init_prod_time_set[1], size=(self.STAGE_NUM, self.JOB_NUM))
        self.INIT_PROD_TIME = []
        for i in range(self.STAGE_NUM):
            for j in range(self.MACHINE_NUM[i]):
                self.INIT_PROD_TIME.append(tmp_prod_time[i]*machine_status[i+j])

        # TODO: Consider bottleneck, 目前寫死在只有三個 stage & 調整中間 stage
        for i in range(self.MACHINE_NUM[0], self.MACHINE_NUM[0] + self.MACHINE_NUM[1]):
            for j in range(self.JOB_NUM):
                self.INIT_PROD_TIME[i][j] *= self.bottleneck

        # TODO: One stage, bottleneck on first stage
        # for i in range(self.MACHINE_NUM[0]):
        #     for j in range(self.JOB_NUM):
        #         self.INIT_PROD_TIME[i][j] *= self.bottleneck

        # TODO: Four or five stages, bottleneck on third stage
        # for i in range(self.MACHINE_NUM[0] + self.MACHINE_NUM[1], self.MACHINE_NUM[0] + self.MACHINE_NUM[1] + self.MACHINE_NUM[2]):
        #     for j in range(self.JOB_NUM):
        #         self.INIT_PROD_TIME[i][j] *= self.bottleneck

        self.PROD_DISCOUNT = random.uniform(self.prod_discount_set[0], self.prod_discount_set[1], size=self.TOTAL_MACHINE_NUM)
        self.MAINT_LEN = random.uniform(self.maint_len_set[0], self.maint_len_set[1], size=self.TOTAL_MACHINE_NUM)
        self.REMAIN = np.array(random.randint(self.remain[0], self.remain[1], size=self.TOTAL_MACHINE_NUM))
        # TODO: the line below is for creating normal queue time limits
        self.QUEUE_TIME_LIMIT = np.array(random.randint(self.queue_time_set[0], self.queue_time_set[1], size=(self.STAGE_NUM, self.JOB_NUM)))
        # TODO: the line below is for creating queue time limits that can be considered as inf in the case
        # self.QUEUE_TIME_LIMIT = [[np.sum(self.INIT_PROD_TIME) for i in range(self.JOB_NUM)] for j in range(self.STAGE_NUM-1)]

        # DUE_TIME
        # record the current finish time of the job
        self.tmp_job_time = np.zeros(self.JOB_NUM)
        # record the current finish time of each machine, using REMAIN
        self.tmp_machine_time = copy.deepcopy(self.REMAIN)
        # Create a schedule with "job listing = job index", not considering any maintenance/ queue time limit
        machine_count = 0
        for i in range(self.STAGE_NUM):
            for j in range(self.JOB_NUM):
                best_machine = min(range(machine_count, machine_count + self.MACHINE_NUM[i]),
                                   key=lambda k: max(self.tmp_machine_time[k], self.tmp_job_time[j]) + self.INIT_PROD_TIME[k][j])
                current_time = max(self.tmp_machine_time[best_machine], self.tmp_job_time[j]) + self.INIT_PROD_TIME[best_machine][j]
                self.tmp_job_time[j] = current_time
                self.tmp_machine_time[best_machine] = current_time
            machine_count += self.MACHINE_NUM[i]

        self.due_mu = np.mean(self.tmp_job_time) * self.due_time_set
        self.due_sigma = self.due_mu * self.factors['due_time']['sig_ratio']
        self.DUE_TIME = np.array([pos_normal(self.due_mu, self.due_sigma) for j in range(self.JOB_NUM)]).reshape(-1)
        self.WEIGHT = random.uniform(self.weight_set[0], self.weight_set[1], size=self.JOB_NUM)

    def run(self, instance_num=10, start_instance_num=1):
        folder_name = 'tests/multiple_machine/'
        path = folder_name + self.file
        print(f'scenario: {self.file}')
        if not os.path.isdir(path):
            os.makedirs(path)

        for num in range(start_instance_num, start_instance_num+instance_num):
            Create.sample(self)
            print(f'- num: {num}')

            file = open(path + '/' + self.file + '_' + str(num) + '.txt', 'w+')
            
            # # of stages, # of jobs
            file.write(f'{self.STAGE_NUM} {self.JOB_NUM}\n')
            
            # # of machines in each stage
            for i in range(self.STAGE_NUM):
                if (i != 0):
                    file.write(' ')
                file.write(f'{self.MACHINE_NUM[i]}')
            file.write('\n')

            # details of each machine
            # discount, maintenance length, remain, initial production time
            for i in range(self.TOTAL_MACHINE_NUM):
                INIT_PROD_TIME_STR = ''
                for j in range(self.JOB_NUM):
                    INIT_PROD_TIME_STR += str(self.INIT_PROD_TIME[i][j]) + ' '
                file.write(f'{self.PROD_DISCOUNT[i]} {self.MAINT_LEN[i]} {self.REMAIN[i]} {INIT_PROD_TIME_STR.strip()}\n')

            for i in range(self.JOB_NUM):
                file.write(f'{self.DUE_TIME[i]} {self.WEIGHT[i]}\n')
            
            for i in range(self.STAGE_NUM - 1):
                for j in range(self.JOB_NUM):
                    if (j != 0):
                        file.write(' ')
                    file.write(f'{self.QUEUE_TIME_LIMIT[i][j]}')
                file.write('\n')


            file.close()



factors = {
    'init_prod_time': [5, 30],
    'prod_discount': [0.8, 0.9],
    'weight': [0.8, 1.2],
    'due_time': {'L': 0.4, 'M': 0.6, 'H': 0.8, 'sig_ratio': 0.25},
    'maint_len': {'L': [0, 0], 'M': [5, 30], 'H': [20, 45]},
	'remain': [0, 20],
    # Need to fix code directly if want to create inf queue time
    'queue_time': {'L': [0, 10], 'M': [10, 20]},
    'bottleneck': {'L': 1, 'M': 1.2, 'H': 2}
  }
# factors_key = factors.keys()
factors_key = ['maint_len', 'queue_time', 'bottleneck']


def main(instance_num=10, start_instance_num=1):
    # base
    create_cls = Create(factors)
    create_cls.run(instance_num=instance_num, start_instance_num=start_instance_num)

    # other scenarios
    for key in factors_key:
        if key != 'queue_time':
            for level in ['L', 'H']:
                create_cls.scenario(key, level=level)
                create_cls.run(instance_num=instance_num, start_instance_num=start_instance_num)
        # TODO: queue_time_H uses inf as queue time, need to fix code directly
        else:
            create_cls.scenario(key, level='L')
            create_cls.run(instance_num=instance_num, start_instance_num=start_instance_num)

    # # queue_time_H, need to fix code, can't run together with other scenarios
    # create_cls = Create(factors)
    # create_cls.scenario('queue_time', level='H')
    # create_cls.run(instance_num=instance_num, start_instance_num=start_instance_num)

main(instance_num=30)