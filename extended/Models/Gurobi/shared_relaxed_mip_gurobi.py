import gurobipy as gp
from gurobipy import *
from Models import Parameters
import xlsxwriter

class SharedRelaxedMIPModel:
    def __init__(self, parameters: Parameters, run_time_limit=1800, mip_gap=0.01) -> None:
        self.gp_model = gp.Model("Relaxed_MIP")
        self.gp_model.Params.LogToConsole = 0
        self.parameters = parameters
        self.I = self.parameters.I
        self.M = self.parameters.M
        self.J = self.parameters.J
        self.gp_model.setParam('TimeLimit', run_time_limit)
        self.gp_model.setParam('MIPGap', mip_gap)
        # restrict binary variables to be 0 or 1
        self.__add_variables()
        self.__add_constraints()
        self.__set_objective()
    def __add_variables(self) -> None:
        # define decision variables
        # r_imj: 1 if job j is completed on machine m in stage i or 0, otherwise
        self.r_imj = {}
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.r_imj[i, m, j] = self.gp_model.addVar(vtype=GRB.BINARY, name=f'r_{i}_{m}_{j}')
        # z_ij: completion time of job j in stage i
        self.z_ij = self.gp_model.addVars(self.I, self.J, vtype=GRB.CONTINUOUS, name="z")
        # p_imj = effective production time of job j on machine m in stage i
        self.p_imj = {}
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.p_imj[i, m, j] = self.gp_model.addVar(vtype=GRB.CONTINUOUS, name=f'p_{i}_{m}_{j}')
        # x_imj_1j_2 = 1 if job j_1 precedes job j_2 on machine m in stage i or 0, otherwise
        self.x = {}
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    for k in self.J:
                        if j != k:
                            self.x[i, m, j, k] = self.gp_model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{m}_{j}_{k}")
        # s_j_1j_2 = 1 if job j_1 precedes job j_2 or 0, otherwise
        self.s = {}
        for j in self.J:
            for k in self.J:
                if j != k:
                    self.s[j, k] = self.gp_model.addVar(vtype=GRB.BINARY, name=f"s_{j}_{k}")
        # q_j fake time for ensuring shared job order
        self.q = {}
        for j in self.J:
            self.q[j] = self.gp_model.addVar(vtype=GRB.CONTINUOUS, name=f"q_{j}")
        # need to define tardiness for job j because gurobi objective function needs to use it
        self.tardiness = {}
        for j in self.J:
            self.tardiness[j] = self.gp_model.addVar(vtype=GRB.CONTINUOUS, name=f"tardiness_{j}")
    def __add_constraints(self) -> None:
        
        # constraint1
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.gp_model.addConstr(
                        self.z_ij[i, j] - (self.parameters.Unfinished_Production_Time[i - 1][m - 1] + self.p_imj[i, m, j]) >= -1 * self.parameters.Very_Large_Positive_Number * (1 - self.r_imj[i, m, j])
                    )
        # constraint2
        for i in self.I[:-1]:
            M_i_plus_1 = self.M[i]
            for m in M_i_plus_1:
                for j in self.J:
                    self.gp_model.addConstr(
                        self.z_ij[i + 1, j] - (self.z_ij[i, j] + self.p_imj[i + 1, m, j]) >= -1 * self.parameters.Very_Large_Positive_Number * (1 - self.r_imj[i + 1, m, j])
                    )
        # constraint3
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j1 in self.J:
                    for j2 in self.J:
                        if j1 != j2:
                            self.gp_model.addConstr(
                                self.z_ij[i, j1] + self.p_imj[i, m, j2] - self.z_ij[i, j2] <= self.parameters.Very_Large_Positive_Number * (1 - self.x[i, m, j1, j2])
                            )
        # constraint7
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.gp_model.addConstr(
                        self.p_imj[i, m, j] >= self.parameters.Initial_Production_Time[i - 1][m - 1][j - 1] * self.parameters.Production_Time_Discount[i - 1][m - 1]
                    )
        # constraint9
        for i in self.I:
            M_i = self.M[i - 1]
            for j in self.J:
                self.gp_model.addConstr(
                    quicksum(self.r_imj[i, m, j] for m in M_i) == 1
                )
        # constraint10
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j1 in self.J:
                    for j2 in self.J:
                        if j1 < j2:
                            self.gp_model.addConstr(
                                self.x[i, m, j1, j2] + self.x[i, m, j2, j1] >= self.r_imj[i, m, j1] + self.r_imj[i, m, j2] - 1
                            )
        # constraint new 1 (shared job order)
        for j1 in self.J:
            for j2 in self.J:
                if j1 < j2:
                    self.gp_model.addConstr(
                        self.s[j1, j2] + self.s[j2, j1] == 1
                    )
        # constraint new 2 (follow shared job order)
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j1 in self.J:
                    for j2 in self.J:
                        if j1 != j2:
                            self.gp_model.addConstr(
                                self.x[i, m, j1, j2] + 2 >= self.s[j1, j2] + self.r_imj[i, m, j1] + self.r_imj[i, m, j2]
                            )
        # constraint new 3 (ensure a complete order)
        for j1 in self.J:
            for j2 in self.J:
                if j1 < j2:
                    self.gp_model.addConstr(
                        self.q[j1] - self.q[j2] - 1 >=  -1 * self.parameters.Very_Large_Positive_Number * (1 - self.s[j1, j2])
                    )
                    self.gp_model.addConstr(
                        self.q[j2] - self.q[j1] - 1 >=  -1 * self.parameters.Very_Large_Positive_Number * (1 - self.s[j2, j1])
                    )
        # tardiness for each job
        for j in self.J:
            self.gp_model.addConstr(
                self.tardiness[j] >= self.z_ij[self.parameters.Number_of_Stages, j] - self.parameters.Due_Time[j - 1]
            )
            self.gp_model.addConstr(
                self.tardiness[j] >= 0
            )

    def __set_objective(self) -> None:
        # define objective function
        #TODO: rewrite the objective function!!

        self.gp_model.setObjective(
            quicksum(self.tardiness[j] * self.parameters.Tardiness_Penalty[j - 1] for j in self.J), GRB.MINIMIZE
        )

    def run_and_solve(self, result_path) -> None:
        print("Start solving relaxed...")
        # run Gurobi
        self.gp_model.optimize()
        return self.__record_result(result_path)
    
    def __record_result(self, result_path) -> None:
        # record the result
        print("Runtime: ", self.gp_model.Runtime)
        print("Best objective value: ", self.gp_model.objVal)
        print("Best MIP gap: ", self.gp_model.MIPGap)
        print("Best bound: ", self.gp_model.ObjBound)
        # for v in self.gp_model.getVars():
        #     print(v.varName, v.x)
        workbook = xlsxwriter.Workbook(result_path)
        worksheet = workbook.add_worksheet()
        for j in self.J:
            worksheet.write(j, 0, j)
        for i in self.I:
            worksheet.write(0, -2 + 3 * i, "stage" + str(i) + "_machine")
            worksheet.write(0, -1 + 3 * i, "stage" + str(i) + "_start")
            worksheet.write(0, 3 * i, "stage" + str(i) + "_end")
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    if self.r_imj[i, m, j].X == 1:
                        worksheet.write(j, -2 + 3 * i, m)
                        worksheet.write(j, -1 + 3 * i, self.z_ij[i, j].X - self.p_imj[i, m, j].X)
                    worksheet.write(j, 3 * i, self.z_ij[i, j].X)
        worksheet.write(len(self.J) + 1, 0, "shared job order")
        precedeCnt = [0] * len(self.J)
        for j in self.J:
            for k in self.J:
                if j != k:
                    precedeCnt[j - 1] += self.s[j, k].X
        for j in self.J:
            for k in self.J:
                if precedeCnt[k - 1] > len(self.J) - j - 0.2 and precedeCnt[k - 1] < len(self.J) - j + 0.2:
                    worksheet.write(len(self.J) + 1, j, k)
        workbook.close()

        # for j in self.J:
        #     for k in self.J:
        #         if j != k:
        #             print("job " + str(j) + " job " + str(k), self.s[j, k].X)

        return [self.gp_model.Runtime, self.gp_model.objVal, self.gp_model.ObjBound]
        # print out all decision variables
        
        # with open(result_path, 'w') as f:
        #     f.write(str(self.gp_model.objVal))
        #     f.write('\n')
        #     for i in self.I:
        #         M_i = self.M[i - 1]
        #         for m in M_i:
        #             for j in self.J:
        #                 f.write(str(self.r_imj[i, m, j].X))
        #                 f.write(" ")
        #             f.write('\n')
            
        #     for i in self.I:
        #         for j in self.J:
        #             f.write(str(self.z_ij[i, j].X))
        #             f.write(" ")
        #         f.write('\n')

        #     for i in self.I:
        #         M_i = self.M[i - 1]
        #         for m in M_i:
        #             f.write(str(self.z_imR[i, m].X))
        #             f.write(" ")
        #         f.write('\n')
        #     f.close()
            
    
    def plot_result(self) -> None:
        """
        1. you can access every variable by passing its index
        e.g. you can access completion time of job 1 in stage 1 using self.z_ij[1, 1].x (Note: z_ij[1, 1] is a gurobi variable, but its value needs to be accessed by .x)
        2. you can access every parameter by using the property self.parameters
        e.g. you can access the due time of job 1 using self.parameters.Due_Time[0]

        What should be noticed is that the index of every parameter starts from 0, while the index of every variable starts from 1
        """
        # print("Plotting...")
        # print(f"z_11: {self.z_ij[1, 1].x}")
        # print(f"due time of job 1: {self.parameters.Due_Time[0]}")

