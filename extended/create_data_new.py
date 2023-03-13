from platform import machine
from random import sample
from numpy import random
import numpy as np
from scipy import stats
import os


def pos_normal(mu, sigma):
    x = np.random.normal(mu, sigma, 1)
    return (x if x > 0 else pos_normal(mu, sigma))


class Create:
    def __init__(self, factors: dict) -> None:
        self.factors = factors
        self.init_prod_time_set = factors['init_prod_time']
        self.weight_set = factors['weight']['M']
        self.prod_discount_set = factors['prod_discount']
        self.maint_len_set = factors['maint_len']
        self.due_time_set = factors['due_time']['M']
        self.remain = self.factors['remain']
        self.queue_time_set = self.factors['queue_time']
        self.file = 'base'

    def sample(self):
        # self.STAGE_NUM = random.randint(3, 6)
        # self.JOB_NUM = random.randint(5, 10)
        # self.MACHINE_NUM = random.randint(1, 4, size=self.STAGE_NUM)
        self.STAGE_NUM = 2
        self.JOB_NUM = 10
        self.MACHINE_NUM = [2, 2]
        self.TOTAL_MACHINE_NUM = np.sum(self.MACHINE_NUM)

        # self.INIT_PROD_TIME = random.randint(self.init_prod_time_set[0], self.init_prod_time_set[1], size=(self.TOTAL_MACHINE_NUM, self.JOB_NUM))
        bottleneck = np.array([0, 1]*10)[:self.TOTAL_MACHINE_NUM]
        random.shuffle(bottleneck)
        # np.array([stats.mode(random.choice([0, 1], 10))[0][0] for x in range(10)])
        self.INIT_PROD_TIME = np.array(
            [random.randint(self.init_prod_time_set[b][0], self.init_prod_time_set[b][1], size=self.JOB_NUM)
            for b in bottleneck])
        self.PROD_DISCOUNT = random.uniform(self.prod_discount_set[0], self.prod_discount_set[1], size=self.TOTAL_MACHINE_NUM)
        self.MAINT_LEN = random.uniform(self.maint_len_set[0], self.maint_len_set[1], size=self.TOTAL_MACHINE_NUM)
        self.REMAIN = np.array(random.randint(self.remain[0], self.remain[1], size=self.TOTAL_MACHINE_NUM))
        self.QUEUE_TIME_LIMIT = np.array(random.randint(self.queue_time_set[0], self.queue_time_set[1], size=(self.STAGE_NUM, self.JOB_NUM)))

        # DUE_TIME
        self.tmp_state = np.zeros((self.STAGE_NUM, self.JOB_NUM))
        machine_count = 0
        # Use average time on a stage as the production time
        # for i in range(self.STAGE_NUM):
        #     tmp = np.zeros(self.JOB_NUM)
        #     for j in range(self.MACHINE_NUM[i]):
        #         for k in range(self.JOB_NUM):
        #             tmp[k] += self.INIT_PROD_TIME[machine_count][k]
        #         machine_count += 1
        #     for j in range(self.JOB_NUM):
        #         tmp[j] /= self.MACHINE_NUM[i]
        #     self.tmp_state[i] = tmp
        # Use min time on a stage as the production time
        for i in range(self.STAGE_NUM):
            tmp = np.zeros(self.JOB_NUM)
            for j in range(self.MACHINE_NUM[i]):
                for k in range(self.JOB_NUM):
                    if (self.INIT_PROD_TIME[machine_count][k] < tmp[k] or tmp[k] == 0):
                        tmp[k] = self.INIT_PROD_TIME[machine_count][k]
                machine_count += 1
            for j in range(self.JOB_NUM):
                tmp[j] /= self.MACHINE_NUM[i]
            self.tmp_state[i] = tmp

        self.state = np.zeros((self.STAGE_NUM, self.JOB_NUM))
        self.state[0] = np.cumsum(self.tmp_state[0])
        self.state[:, 0] = np.cumsum(self.tmp_state[:,0])

        for i in range(1, self.STAGE_NUM):
            for j in range(1, self.JOB_NUM):
                self.state[i][j] = max(self.state[i][j-1], self.state[i-1][j]) + self.tmp_state[i][j]

        self.due_mu = np.mean(self.state[:, -1]) * self.due_time_set + np.average(self.REMAIN)
        self.due_sigma = self.due_mu * self.factors['due_time']['sig_ratio']

        self.DUE_TIME = np.array([pos_normal(self.due_mu, self.due_sigma) for j in range(self.JOB_NUM)]).reshape(-1)
        self.WEIGHT = random.uniform(self.weight_set[0], self.weight_set[1], size=self.JOB_NUM)


    def run(self, instance_num=10, start_instance_num=1):
        folder_name = 'tests/'
        path = folder_name + 'significant_bottleneck_0314'
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
    'init_prod_time': [[5, 30], [5, 30]],
    'prod_discount': [0.8, 0.9],
    'weight': {'L': [1, 1], 'M': [0.8, 1.2], 'H': [0.6, 1.4]},
    'due_time': {'L': 0.4, 'M': 0.6, 'H': 0.8, 'sig_ratio': 0.25},
    'maint_len': [5, 30],
	'remain': [0, 20],
    'stage_num': [1, 5],
    'machine_num': [1, 5],
    'queue_time': [0, 20],
  }
factors_key = factors.keys()


def main(instance_num=10, start_instance_num=1):
    create_cls = Create(factors)
    create_cls.run(instance_num=instance_num, start_instance_num=start_instance_num)

main(instance_num=50)