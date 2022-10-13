from random import sample
from numpy import random
import numpy as np
from scipy import stats
import os


def pos_normal(mu, sigma):
    x = np.random.normal(mu, sigma, 1)
    return (x if x > 0 else pos_normal(mu, sigma))


class Create:
    def __init__(self, factors: dict, machine_num=5, job_num=15) -> None:
        self.factors = factors
        self.init_prod_time_set = factors['init_prod_time']['M']
        self.weight_set = factors['weight']['M']
        self.prod_discount_set = factors['prod_discount']['M']
        self.maint_len_set = factors['maint_len']['M']
        self.due_time_set = factors['due_time']['M']
        self.remain = self.factors['remain']
        self.file = 'benchmark'
        self.n_i = machine_num
        self.n_j = job_num

    def scenario(self, factor_name: str, level='M') -> str:
        self.file = str(factor_name) + '_' + level

        self.init_prod_time_set = self.factors['init_prod_time']['M']
        self.weight_set = self.factors['weight']['M']
        self.prod_discount_set = self.factors['prod_discount']['M']
        self.maint_len_set = self.factors['maint_len']['M']
        self.due_time_set = self.factors['due_time']['M']

        if factor_name == 'init_prod_time':
            self.init_prod_time_set = self.factors['init_prod_time'][level]
        elif factor_name == 'weight':
            self.weight_set = self.factors['weight'][level]
        elif factor_name == 'prod_discount':
            self.prod_discount_set = self.factors['prod_discount'][level]
        elif factor_name == 'maint_len':
            self.maint_len_set = self.factors['maint_len'][level]
        elif factor_name == 'due_time':
            self.due_time_set = self.factors['due_time'][level]

    def sample(self):
        bottleneck = np.array([0, 1]*10)[:self.n_i]
        random.shuffle(bottleneck)
        # np.array([stats.mode(random.choice([0, 1], 10))[0][0] for x in range(10)])
        self.INIT_PROD_TIME = np.array(
            [random.randint(self.init_prod_time_set[b][0], self.init_prod_time_set[b][1], size=self.n_j)
            for b in bottleneck])
        self.PROD_DISCOUNT = random.uniform(self.prod_discount_set[0], self.prod_discount_set[1], size=self.n_i)
        self.maint_len_mu = self.factors['maint_len']['mu']
        self.MAINT_LEN = random.uniform(
            self.maint_len_mu * self.maint_len_set[0], self.maint_len_mu * self.maint_len_set[1], size=self.n_i)
        self.REMAIN = np.array(
            sorted(random.randint(
                self.remain[0], self.remain[1], size=self.n_i)
                )
            )

        # DUE_TIME
        self.state = np.zeros((self.n_i, self.n_j))
        self.state[0] = np.cumsum(self.INIT_PROD_TIME[0])
        self.state[:, 0] = np.cumsum(self.INIT_PROD_TIME[:,0])

        for i in range(1, self.n_i):
            for j in range(1, self.n_j):
                self.state[i][j] = max(self.state[i][j-1], self.state[i-1][j]) + self.INIT_PROD_TIME[i][j]

        self.due_mu = np.mean(self.state[:, -1]) * self.due_time_set + np.average(self.REMAIN)  # self.REMAIN[-1]
        self.due_sigma = self.due_mu * self.factors['due_time']['sig_ratio']

        self.DUE_TIME = np.array([pos_normal(self.due_mu, self.due_sigma) for j in range(self.n_j)]).reshape(-1)
        self.WEIGHT = random.uniform(self.weight_set[0], self.weight_set[1], size=self.n_j)


    def run(self, instance_num=10, start_instance_num=1):
        folder_name = 'code/scenario/'
        path = folder_name + self.file
        print(f'scenario: {self.file}')
        if not os.path.isdir(path):
            os.makedirs(path)

        for num in range(start_instance_num, start_instance_num+instance_num):
            Create.sample(self)
            print(f'- num: {num}')

            file = open(path + '/' + self.file + '_' + str(num) + '.txt', 'w+')

            file.write(f'{self.n_i} {self.n_j}\n')
            for i in range(self.n_i):
                INIT_PROD_TIME_STR = ''  # A_{ij}
                for j in range(self.n_j):
                    INIT_PROD_TIME_STR += str(self.INIT_PROD_TIME[i][j]) + ' '
                file.write(f'{self.PROD_DISCOUNT[i]} {self.MAINT_LEN[i]} {self.REMAIN[i]} {INIT_PROD_TIME_STR.strip()}\n')  # B_i F_i A_ij

            for j in range(self.n_j):
                file.write(f'{self.DUE_TIME[j]} {self.WEIGHT[j]}\n')  # D_j W_j

            file.close()



factors = {
	'init_prod_time': {
        'L': [[60, 100], [60, 100]],
        'M': [[60, 100], [100, 140]],
        'H': [[60, 100], [140, 180]]
    },
    'prod_discount': {'L': [0.85, 0.85], 'M': [0.8, 0.9], 'H': [0.75, 0.95]},
    'weight': {'L': [1, 1], 'M': [0.8, 1.2], 'H': [0.6, 1.4]},
    'due_time': {'L': 0.4, 'M': 0.6, 'H': 0.8, 'sig_ratio': 0.25},
    'maint_len': {'L': [1, 1], 'M': [0.8, 1.2], 'H': [0.6, 1.4], 'mu': 150},
	'remain': [500, 1000],
  }
factors_key = factors.keys()


def main(instance_num=10, machine_num=5, job_num=20, all=True, start_instance_num=1):
    create_cls = Create(factors, machine_num=machine_num, job_num=job_num)
    create_cls.run(instance_num=instance_num, start_instance_num=start_instance_num)

    if all:
        for key in list(factors_key)[:-1]:
            for level in ['L', 'H']:
                create_cls.scenario(key, level=level)
                create_cls.run(instance_num=instance_num, start_instance_num=start_instance_num)

# main(instance_num=1, machine_num=5, job_num=20, all=False)  # 只跑 M
main(instance_num=5, machine_num=5, job_num=20, all=True, start_instance_num=31)  # 只跑 M