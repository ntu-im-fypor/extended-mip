import gurobipy as gp
from gurobipy import *

class Data:
    def __init__(self) -> None:
        # A_{ij}: The initial production time of job $j$ on machine $i$.
        self.INIT_PROD_TIME = {}  # i*j
        # B_i: The production time discount after maintenance on machine $i$, $B_i \in [0,1]$.
        self.PROD_DISCOUNT = {}  # i
        # F_i: Maintenance lengths of machine $i$.
        self.MAINT_LEN = {}  # i
        # D_j: Due time of job $j$.
        self.DUE_TIME = {}  # j
        # W_j: Tardiness penalties of job $j$.
        self.WEIGHT = {}
        # M: \displaystyle\sum_{j \in J} A_{ij} + F_i
        self.M = {}


    def read_data(self, in_path: str) -> None:
        # in_path = 'code/small_case'
        self.in_path = in_path
        f = open(self.in_path, 'r')

        self.n_i, self.n_j = [int(x) for x in f.readline().split()]
        # n_I: Number of machines.
        self.N_MACHINE = range(1, self.n_i + 1)
        # n_J: Number of jobs.
        self.N_JOB = range(1, self.n_j + 1)

        for i in range(1, self.n_i+1):
            line = f.readline().split()
            self.PROD_DISCOUNT[i] = float(line[0])
            self.MAINT_LEN[i] = float(line[1])
            m_temp = self.MAINT_LEN[i]
            for j in range(1, self.n_j+1):
                self.INIT_PROD_TIME[i, j] = float(line[1+j])
                m_temp += float(line[1+j])
            self.M[i] = m_temp

        for j in range(1, self.n_j+1):
            line = f.readline().split()
            self.DUE_TIME[j] = float(line[0])
            self.WEIGHT[j] = float(line[1])


class MaintModel:
    def __init__(self, Data, name='model', run_time=300, mipgap=0.01) -> None:
        # 建立模型
        self.model_maint = Model(name)
        # 設定時間
        self.model_maint.setParam('TimeLimit', run_time) # second
        self.run_time_limit = run_time
        # 設定 gap
        self.model_maint.setParam('MIPGap', mipgap)

        self.Data = Data
        self.add_var()
        self.set_obj()
        self.add_constr()

    def add_var(self) -> None:
        print(type(self.Data))
        # 定義決策變數
        # z_{ij}: Completion time of job $j$ on machine $i$
        self.job_cmpl_time = self.model_maint.addVars(self.Data.N_MACHINE, self.Data.N_JOB, vtype=GRB.CONTINUOUS, lb=0)
        # z_i^R: Completion time of maintenance on machine $i$
        self.maint_cmpl_time = self.model_maint.addVars(self.Data.N_MACHINE, vtype=GRB.CONTINUOUS, lb=0)
        # p_{ij}: Effective production time of job $j$ on machine $i$.
        self.prod_time = self.model_maint.addVars(self.Data.N_MACHINE, self.Data.N_JOB, vtype=GRB.CONTINUOUS, lb=0)
        # x_{jk}: $1$ if job $j$ precedes job $k$ or 0 otherwise. % job j 先，job k 後
        self.job_order = self.model_maint.addVars(self.Data.N_JOB, self.Data.N_JOB, vtype=GRB.BINARY)
        # 改 y_ij 為連續
        # y_{ij}: $1$ if maintenance precedes job $j$ on machine $i$ or 0 otherwise.
        self.maint_order = self.model_maint.addVars(self.Data.N_MACHINE, self.Data.N_JOB, vtype=GRB.CONTINUOUS, lb=0)
        # 為了判斷有沒有修 有修為 1
        self.maint = self.model_maint.addVars(self.Data.N_MACHINE, vtype=GRB.BINARY)
        # lateness_j 有 可能負
        self.lateness = self.model_maint.addVars(self.Data.N_JOB, vtype=GRB.CONTINUOUS)
        # tardiness_j max(0, num)
        self.tardiness = self.model_maint.addVars(self.Data.N_JOB, vtype=GRB.CONTINUOUS, lb=0)

    def set_obj(self) -> None:
        # 定義目標變數
        self.model_maint.setObjective((
                quicksum(self.tardiness[j] * self.Data.WEIGHT[j] for j in self.Data.N_JOB)
            ), GRB.MINIMIZE)

    def add_constr(self) -> None:
        # 定義限制式
        # add constraints defining z_{n_i,j} - D_j = lateness_j
        self.model_maint.addConstrs((
                self.job_cmpl_time[self.Data.N_MACHINE[-1], j] -
                self.Data.DUE_TIME[j] - self.lateness[j] == 0 for j in self.Data.N_JOB
            ), name='lateness')
        # add constraints defining tardiness_j = max(lateness_j, 0)
        self.model_maint.addConstrs((
                self.tardiness[j] == gp.max_([self.lateness[j], 0.0])
                for j in self.Data.N_JOB
            ), name='tardiness')

        # nextMachineCompletionTime z_{i+1,j} >= z_{ij} + p_{i+1,j}
        self.model_maint.addConstrs((
                self.job_cmpl_time[i+1, j] >= self.job_cmpl_time[i, j] + self.prod_time[i+1, j]
                for i in self.Data.N_MACHINE[:-1] for j in self.Data.N_JOB
            ), name='nextMachineCmplTime')

        # firstMachineCompletionTime z_{1,j} >= p_{1,j}
        self.model_maint.addConstrs((
                self.job_cmpl_time[self.Data.N_MACHINE[0], j] >= self.prod_time[self.Data.N_MACHINE[0], j]
                for j in self.Data.N_JOB
            ), name='firstMachineCmplTime')

        # jobjPrecedesJobk z_{ik} + p_{ij} - z_{ij} <=  M_{ijk}^{(1)}  x_{jk}
        self.model_maint.addConstrs((
                self.job_cmpl_time[i, k] + self.prod_time[i, j] - self.job_cmpl_time[i, j] <= self.Data.M[i] * self.job_order[j, k]
                for i in self.Data.N_MACHINE for j in self.Data.N_JOB for k in self.Data.N_JOB if j != k
            ), name='jobjPrecedesJobk')

        # jobkPrecedesJobj z_{ij} + p_{ik} - z_{ik} <=  M_{ijk}^{(2)}  (1-x_{jk})
        self.model_maint.addConstrs((
                self.job_cmpl_time[i, j] + self.prod_time[i, k] - self.job_cmpl_time[i, k] <= self.Data.M[i] * (1-self.job_order[j, k])
                for i in self.Data.N_MACHINE for j in self.Data.N_JOB for k in self.Data.N_JOB if j != k
            ), name='jobjPrecedesJobk')

        # maintenancePrecedesJobj z_{ij} + F_i - z_i^R <=  M_{ij}^{(3)}  y_{ij}
        self.model_maint.addConstrs((
                self.job_cmpl_time[i, j] + self.Data.MAINT_LEN[i] - self.maint_cmpl_time[i] <= self.Data.M[i] * self.maint_order[i, j]
                for i in self.Data.N_MACHINE for j in self.Data.N_JOB
            ), name='maintPrecedesJobj')

        # jobjPrecedesMaintenance z_i^R + p_{ij} - z_{ij} <=  M_{ij}^{(4)} (1-y_{ij})
        self.model_maint.addConstrs((
                self.maint_cmpl_time[i] + self.prod_time[i, j] - self.job_cmpl_time[i, j] <= self.Data.M[i] * (1-self.maint_order[i, j])
                for i in self.Data.N_MACHINE for j in self.Data.N_JOB
            ), name='jobjPrecedesMaint')

        # maintenanceFirst z_i^R >= F_i y_{i, 1}
        self.model_maint.addConstrs((
                self.maint_cmpl_time[i] >= self.Data.MAINT_LEN[i] * self.maint_order[i, 1]
                for i in self.Data.N_MACHINE
            ), name='maintenanceFirst')

        # 為了好判斷而增加 若 yij 皆為 0 則 沒有修理
        self.model_maint.addConstrs((
                self.maint[i] * quicksum(self.maint_order[i, j] for j in self.Data.N_JOB) == 0
                for i in self.Data.N_MACHINE
            ), name='maintenanceZero')


        # afterMaintenance p_{ij} >= A_{ij} - A_{ij}(1-B_i)y_{ij}
        self.model_maint.addConstrs((
                self.prod_time[i, j] >= self.Data.INIT_PROD_TIME[i, j] -
                self.Data.INIT_PROD_TIME[i, j] * (1-self.Data.PROD_DISCOUNT[i]) * self.maint_order[i, j]
                for i in self.Data.N_MACHINE for j in self.Data.N_JOB
            ), name='afterMaint')

    def run(self) -> None:
        # run Gurobi
        self.model_maint.optimize()
        if self.model_maint.Runtime > self.run_time_limit:
            print("Final MIP gap value: %f" % self.model_maint.MIPGap)

    def record(self) -> str:

        ## objective value
        print('objective value')
        print('obj = ', self.model_maint.objVal)
        print('The run time is %f' % self.model_maint.Runtime)

        # '''
        ## x_it 對角線不用看
        print('x_jk', 'job_order', sep='\t')   # head of the result table
        for j in self.Data.N_JOB:
            print('JOB' + str(j), '\t', end='') # mark which item is printed now
            for k in self.Data.N_JOB:
                try:
                    print(abs(round(self.job_order[j, k].x, 5)), ' ', end='') # print qty of each kind of item
                except:
                    print(0, ' ', end='')
            print('')  # use for change line
        print('\n')

        ## maint_order y_ij
        print('y_ij', 'maint_order', sep='\t')   # head of the result table
        for i in self.Data.N_MACHINE:
            print('MACHINE' + str(i), ' ', end='') # mark which item is printed now
            for j in self.Data.N_JOB:
                try:
                    print(abs(round(self.maint_order[i, j].x, 5)), ' ', end='') # print qty of each kind of item
                except:
                    print(0, ' ', end='')
            print('')  # use for change line
        print('\n')

        ## maint_cmpl_time z_iR
        print('z_iR', 'maint_cmpl_time', sep='\t')
        print('MACHINE', ' ', end='')
        for i in self.Data.N_MACHINE:
            try:
                print('Y:' if self.maint[i].x > 0 else 'N:', '', end='')
                print(round(self.maint_cmpl_time[i].x, 5), ' ', end='') # print qty of each kind of item
            except:
                print(0, ' ', end='')
        print('\n')

        ## job_cmpl_time z_ij
        print('z_ij', 'job_cmpl_time', sep='\t')   # head of the result table
        for j in self.Data.N_JOB:
            print('JOB' + str(j), ' ', end='') # mark which item is printed now
            for i in self.Data.N_MACHINE:
                try:
                    print(round(self.job_cmpl_time[i, j].x, 5), ' ', end='') # print qty of each kind of item
                except:
                    print(0, ' ', end='')
            print(f'due: {self.Data.DUE_TIME[j]}, tardiness: {self.tardiness[j].x}')
            # print('')  # use for change line
        # print('\n')
        # '''
        return self.model_maint.objVal, self.model_maint.Runtime, self.model_maint.MIPGap, self.model_maint.ObjBoundC

def test():
    path = 'code/scenario/'
    full_path = path + '/small_case.txt'
    data = Data()
    data.read_data(in_path=full_path)
    model = MaintModel(data)
    model.run()
    obj, runtime = model.record()
    print(f'obj: {obj}, runtime: {runtime: .6f}')

# test()

