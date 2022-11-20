import sys
from tokenize import String
from unittest import result
from Models import Parameters
from Models.Gurobi import CompleteMIPModel, CompleteMIPModel_original
from Models.heuristic import MetaPSOModel, MetaGAModel
import pandas as pd
import numpy as np

class ResultParameters:
    def __init__(self) -> None:
        self.objVal = 0 # objective value

    def read_result(self, instance_file_path, result_file_path) -> None:
        parameters = Parameters() # read parameters
        parameters.read_parameters(instance_file_path)

        self.MACHINES_NUM_FLATTEN = sum(parameters.Number_of_Machines)
        self.JOBS_NUM = parameters.Number_of_Jobs
        self.STAGES_NUM = parameters.Number_of_Stages
        self.MACHINES_NUM = parameters.Number_of_Machines
        self.MAX_MACHINE_NUM = parameters.Max_Number_of_Machines

        self.rmj = np.zeros((self.MACHINES_NUM_FLATTEN, self.JOBS_NUM)) # whether job j completed on machine m
        self.zij = np.zeros((self.STAGES_NUM, self.JOBS_NUM)) # whether job j's completion time in stage i
        self.vim = np.zeros((self.STAGES_NUM, max(self.MACHINES_NUM))) # whether maintenance is completed on machine m in stage i
        self.bim = np.zeros((self.STAGES_NUM, max(self.MACHINES_NUM))) # maintenance completion time of machine m in stage i
        self.schedule = np.zeros((self.STAGES_NUM, self.JOBS_NUM + max(self.MACHINES_NUM))) # solution schedule

        with open(result_file_path, 'r') as f:
            [self.objVal] = map(float, f.readline().split())
            for m in range(self.MACHINES_NUM_FLATTEN):
                row = list(map(int,map(float, f.readline().split())))
                for j in range(self.JOBS_NUM):
                    self.rmj[m][j] = row[j]
            for i in range(self.STAGES_NUM):
                row = list(map(float, f.readline().split()))
                for j in range(self.JOBS_NUM):
                    self.zij[i][j] = row[j]
            for i in range(self.STAGES_NUM):
                row = list(map(float, f.readline().split()))
                for m in range(self.MACHINES_NUM[i]):
                    self.vim[i][m] = row[m]
            for i in range(self.STAGES_NUM):
                row = list(map(float, f.readline().split()))
                for m in range(self.MACHINES_NUM[i]):
                    self.bim[i][m] = row[m]

    def generateOrder(self) -> None:
        machine = 0
        for i in range(self.STAGES_NUM):
            for m in range(self.MACHINES_NUM[i]):
                indexes = np.where(self.rmj[machine] == 1) # filter jobs completed on this machine in this stage
                completion_time = self.zij[i][indexes] # retrieve their completion times
                index_completion_time_list = list(zip(np.array(indexes).flatten(), completion_time))
                if(self.vim[i][m] == 1): # if maintenance is completed on stage i of machine m
                    index_completion_time_list.append((-1, self.bim[i][m])) # zip to (index, completion time) list and append maintenance time
                index_completion_time_list = sorted(index_completion_time_list, key=lambda x: x[1]) # sort according to completion time
                for k in range(len(index_completion_time_list)):
                    if index_completion_time_list[k][0] != -1: # is a job
                        self.schedule[i][index_completion_time_list[k][0]] = (m+1) + round(k / len(index_completion_time_list), 2)
                    else: # is maintenance
                        self.schedule[i][self.JOBS_NUM + m] = (m+1) + round(k / len(index_completion_time_list), 2)
                machine+=1

def test_objective_function():
    # read parameters from file
    if len(sys.argv) == 0:
        print("No parameters file specified")
        return
    file_id = sys.argv[1]
    parameters = Parameters()
    parameters.read_parameters('tests/base/base_'+ str(file_id) +'.txt')
    heuristic_model = MetaPSOModel(parameters)
    # heuristic_model.run_and_solve()

    # generate a schedule from the base results
    resultParameters = ResultParameters()
    resultParameters.read_result('tests/base/base_'+ str(file_id) +'.txt','tests/base_result_1107/base_result_'+ str(file_id) +'.txt')
    resultParameters.generateOrder()
    print("Generated Ordering:")
    print(resultParameters.schedule)
    heuristic_model.record_result(resultParameters.schedule)
    print("Gurobi objective value: ", resultParameters.objVal)
    ### for listing and comparing all objective values
    # return resultParameters.objVal, heuristic_model.record_result(resultParameters.schedule) # gurobi value, fn value



if __name__ == '__main__':
    test_objective_function()

    ### function to list and compare all objective values
    # data = [['Gurobi obj', 'Constrained obj']]
    # for i in range(1, 51):
    #     real_obj, unconstrained_obj = test_objective_function(i)
    #     print(real_obj, unconstrained_obj)
    #     data.append([real_obj, unconstrained_obj])
    # df = pd.DataFrame(data)
    # df.to_csv('./tests/1108_objective_values_constrained.csv')
