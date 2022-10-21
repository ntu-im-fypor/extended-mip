import numpy as np
class Parameters:
    def __init__(self) -> None:
        # n^I: Number of stages
        self.Number_of_Stages = 0
        # n^J: Number of jobs
        self.Number_of_Jobs = 0
        # n_i^M: Number of machines in stage i
        self.Number_of_Machines = []
        # Q_ij: Queue time limit of job j in stage i, except for stage 1
        self.Queue_Time_Limit = np.array([])
        # A_imj: Initial production time of job j on machine m in stage i
        self.Initial_Production_Time = np.array([])
        # B_im: Production time discount after maintenance of machine m in stage i
        self.Production_Time_Discount = np.array([])
        # U_im: Unfinished production time from the previous day for machine m in stage i
        self.Unfinished_Production_Time = np.array([])
        # F_im: Maintenance length of machine m in stage i
        self.Maintenance_Length = np.array([])
        # D_j: Due time of job j
        self.Due_Time = np.array([])
        # W_j: Tardiness penalty of job j
        self.Tardiness_Penalty = np.array([])
        # K: A very large positive number
        # TODO: 這邊要討論 K 的值應該設多少比較好
        self.Very_Large_Positive_Number = 0
    
    def read_parameters(self, file_name: str) -> None:
        with open(file_name, 'r') as f:
            # first line: n^I, n^J
            self.Number_of_Stages, self.Number_of_Jobs = map(int, f.readline().split())
            # second line: n_i^M
            self.Number_of_Machines = list(map(int, f.readline().split()))
            max_machine_num = max(self.Number_of_Machines)
            # initialize lists for other parameters
            self.Queue_Time_Limit = np.zeros((self.Number_of_Stages, self.Number_of_Jobs))
            self.Initial_Production_Time = np.zeros((self.Number_of_Stages, max_machine_num, self.Number_of_Jobs))
            self.Production_Time_Discount = np.zeros((self.Number_of_Stages, max_machine_num))
            self.Unfinished_Production_Time = np.zeros((self.Number_of_Stages, max_machine_num))
            self.Maintenance_Length = np.zeros((self.Number_of_Stages, max_machine_num))
            self.Due_Time = np.zeros(self.Number_of_Jobs)
            self.Tardiness_Penalty = np.zeros(self.Number_of_Jobs)

            # for every stage, every row is information of a machine on that stage
            for i in range(self.Number_of_Stages):
                # the following n_i^M lines are information of machines
                for m in range(self.Number_of_Machines[i]):
                    # every row is discount, maintenance length, unfinished production time, initial production time for n^J jobs
                    tokens = list(map(float, f.readline().split()))
                    self.Production_Time_Discount[i][m] = tokens[0]
                    self.Maintenance_Length[i][m] = tokens[1]
                    self.Unfinished_Production_Time[i][m] = tokens[2]
                    for j in range(self.Number_of_Jobs):
                        self.Initial_Production_Time[i][m][j] = tokens[3 + j]
            # following n^J lines are (due time, tardiness penalty) for n^J jobs
            for j in range(self.Number_of_Jobs):
                self.Due_Time[j], self.Tardiness_Penalty[j] = map(float, f.readline().split())
            
            # following n^I - 1 lines are queue time limit for n^J jobs in n^I - 1 stages
            for i in range(1, self.Number_of_Stages):
                tokens = list(map(int, f.readline().split()))
                for j in range(self.Number_of_Jobs):
                    self.Queue_Time_Limit[i][j] = tokens[j]

        print("Parameters read from file successfully.")

        """
        range definition for sets
        i = 1, 2, ..., n^I
        m = 1, 2, ..., n_i^M
        j = 1, 2, ..., n^J
        """
        self.I = list(range(1, self.Number_of_Stages + 1))
        self.M = []
        for machine_num in self.Number_of_Machines:
            self.M.append(list(range(1, machine_num + 1)))
        self.J = list(range(1, self.Number_of_Jobs + 1))

        # set very large positive number
        for i in range(self.Number_of_Stages):
            for m in range(self.Number_of_Machines[i]):
                for j in range(self.Number_of_Jobs):
                    self.Very_Large_Positive_Number += (
                        self.Initial_Production_Time[i][m][j] +
                        self.Maintenance_Length[i][m] +
                        self.Unfinished_Production_Time[i][m]
                    )