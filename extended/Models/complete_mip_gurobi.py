import gurobipy as gp
from gurobipy import *
from Models.Parameters import Parameters

class CompleteMIPModel:
    def __init__(self, parameters: Parameters, run_time_limit=300, mip_gap=0.01) -> None:
        self.gp_model = gp.Model("Complete_MIP")
        self.parameters = parameters
        self.I = self.parameters.I
        self.M = self.parameters.M
        self.J = self.parameters.J
        self.model.setParam('TimeLimit', run_time_limit)
        self.model.setParam('MIPGap', mip_gap)
        self.add_variables()
        self.add_constraints()
        self.set_objective()
    def add_variables(self) -> None:
        # define decision variables
        # r_imj: 1 if job j is completed on machine m in stage i or 0, otherwise
        self.r_imj = self.gp_model.addVars(self.I, self.M, self.J, vtype=GRB.BINARY, name="r")
        # v_im: 1 if machine m is maintained in stage i or 0, otherwise
        self.v_im = self.gp_model.addVars(self.I, self.M, vtype=GRB.BINARY, name="v")
        # z_im^R: completion time of maintenance of machine m in stage i
        self.z_imR = self.gp_model.addVars(self.I, self.M, vtype=GRB.CONTINUOUS, name="z^R")
        # z_ij: completion time of job j in stage i
        self.z_ij = self.gp_model.addVars(self.I, self.J, vtype=GRB.CONTINUOUS, name="z")
        # p_imj = effective production time of job j on machine m in stage i
        self.p_imj = self.gp_model.addVars(self.I, self.M, self.J, vtype=GRB.CONTINUOUS, name="p")
        # x_imj_1j_2 = 1 if job j_1 precedes job j_2 on machine m in stage i or 0, otherwise
        self.x = {}
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    for k in self.J:
                        if j != k:
                            self.x[i, m, j, k] = self.gp_model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{m}_{j}_{k}")
        # y_imj^Before = 1 if maintenance precedes job j on machine m in stage i or 0, otherwise
        self.y_imj_before = self.gp_model.addVars(self.I, self.M, self.J, vtype=GRB.BINARY, name="y_before")
        # y_imj^After = 1 if job j precedes maintenance on machine m in stage i or 0, otherwise
        self.y_imj_after = self.gp_model.addVars(self.I, self.M, self.J, vtype=GRB.BINARY, name="y_after")
        # w_i1_m1_i2_m2 = 1 if maintenance timing of machine m1 in stage i1 precedes maintenance timing of machine m2 in stage i2 or 0, otherwise, (i1, m1) != (i2, m2)
        self.w = {}
        for i1 in self.I:
            M_i1 = self.M[i1 - 1]
            for m1 in M_i1:
                for i2 in self.I:
                    M_i2 = self.M[i2 - 1]
                    for m2 in M_i2:
                        if (i1, m1) != (i2, m2):
                            self.w[i1, m1, i2, m2] = self.gp_model.addVar(vtype=GRB.BINARY, name=f"w_{i1}_{m1}_{i2}_{m2}")

    def add_constraints(self) -> None:
        
        # constraint1
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.gp_model.addConstr(
                        self.z_ij[i, j] - (self.parameters.Unfinished_Production_Time[i, m] + self.p_imj[i, m, j]) >= -1 * self.parameters.Very_Large_Positive_Number * (1 - self.r_imj[i, m, j])
                    )
        # constraint2
        for i in self.I[:-1]:
            M_i = self.M[i - 1]
            for m in M_i:
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
        # constraint4
        for i in self.I:
            for m in self.M[i - 1]:
                self.gp_model.addConstr(
                    self.z_imR[i, m] >= (
                        self.parameters.Unfinished_Production_Time[i, m] + 
                        self.parameters.Maintenance_Length[i, m] +
                        self.parameters.Very_Large_Positive_Number * (quicksum(self.y_imj_before[i, m, j] for j in self.J) - self.parameters.Number_of_Jobs)
                    )
                )
        # constraint5
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.gp_model.addConstr(
                        self.z_ij[i, j] + self.parameters.Maintenance_Length[i, m] - self.z_imR[i, m] <= self.parameters.Very_Large_Positive_Number * (1 - self.y_imj_after[i, m, j])
                    )
        # constraint6
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.gp_model.addConstr(
                        self.z_imR[i, m] + self.p_imj[i, m, j] - self.z_ij[i, j] <= self.parameters.Very_Large_Positive_Number * (1 - self.y_imj_before[i, m, j])
                    )
        # constraint7
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.gp_model.addConstr(
                        self.p_imj[i, m, j] >= self.parameters.Initial_Production_Time[i, m, j] * (1 - (1 - self.parameters.Production_Time_Discount[i, m]) * self.y_imj_before[i, m, j])
                    )
        # constraint8
        for i1 in self.I:
            M_i1 = self.M[i1 - 1]
            for i2 in self.I:
                M_i2 = self.M[i2 - 1]
                for m1 in M_i1:
                    for m2 in M_i2:
                        if not (i1 == i2 and m1 == m2):
                            self.gp_model.addConstr(
                                self.z_imR[i1, m1] + self.parameters.Maintenance_Length[i2, m2] - self.z_imR[i2, m2] <= self.parameters.Very_Large_Positive_Number * (1 - self.w[i1, m1, i2, m2])
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
                        if j1 != j2:
                            self.gp_model.addConstr(
                                self.x[i, m, j1, j2] + self.x[i, m, j2, j1] >= self.r_imj[i, m, j1] + self.r_imj[i, m, j2] - 1
                            )
        # constraint11
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.gp_model.addConstr(
                        2 * (self.y_imj_before[i, m, j] + self.y_imj_after[i, m, j]) <= self.r_imj[i, m, j] + self.v_im[i, m]
                    )
        # constraint12
        for i in self.I:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.gp_model.addConstr(
                        self.y_imj_before[i, m, j] + self.y_imj_after[i, m, j] >= self.r_imj[i, m, j] + self.v_im[i, m] - 1
                    )
        # constraint13
        for i1 in self.I:
            M_i1 = self.M[i1 - 1]
            for i2 in self.I:
                M_i2 = self.M[i2 - 1]
                for m1 in M_i1:
                    for m2 in M_i2:
                        if not (i1 == i2 and m1 == m2):
                            self.gp_model.addConstr(
                                self.w[i1, m1, i2, m2] + self.w[i2, m2, i1, m1] >= self.v_im[i1, m1] + self.v_im[i2, m2] - 1
                            )
        # constraint14
        for i in self.I[1:]:
            M_i = self.M[i - 1]
            for m in M_i:
                for j in self.J:
                    self.gp_model.addConstr(
                        self.z_ij[i, j] - self.p_imj[i, m, j] - self.z_ij[i - 1, j] - self.parameters.Queue_Time_Limit[i, j] <= self.parameters.Very_Large_Positive_Number * (1 - self.r_imj[i, m, j])
                    )

    def set_objective(self) -> None:
        # define objective function
        self.gp_model.setObjective((quicksum(
            max(self.z_ij[self.parameters.Number_of_Stages] - self.parameters.Due_Time[j], 0) * self.Data.WEIGHT[j] 
            for j in self.Data.N_JOB
        )), GRB.MINIMIZE)
