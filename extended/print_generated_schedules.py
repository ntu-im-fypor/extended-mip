import sys
from tokenize import String
from unittest import result
from Models import Parameters
from Models.Gurobi import CompleteMIPModel, CompleteMIPModel_original
from Models.heuristic import MetaPSOModel
import pandas as pd
import numpy as np
import os

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

        self.rmj = np.zeros((self.MACHINES_NUM_FLATTEN, self.JOBS_NUM)) # whether job j completed on machine m
        self.zij = np.zeros((self.STAGES_NUM, self.JOBS_NUM)) # whether job j's completion time in stage i
        self.vim = np.zeros((self.STAGES_NUM, max(self.MACHINES_NUM))) # whether maintenance is completed on machine m in stage i
        self.bim = np.zeros((self.STAGES_NUM, max(self.MACHINES_NUM))) # maintenance completion time of machine m in stage i
    
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
  
    def generateOrder(self, file) -> None:
        machine = 0
        for i in range(self.STAGES_NUM):
            for m in range(self.MACHINES_NUM[i]):
                maint_job_list = []
                indexes = np.where(self.rmj[machine] == 1) # filter jobs completed on this machine in this stage
                completion_time = self.zij[i][indexes] # retrieve their completion times
                index_completion_time_list = list(zip(np.array(indexes).flatten(), completion_time))
                if(self.vim[i][m] == 1): # if maintenance is completed on stage i of machine m
                    index_completion_time_list.append((-1, self.bim[i][m])) # zip to (index, completion time) list and append maintenance time
                sorted_index_completion_time_list = sorted(index_completion_time_list, key=lambda x: x[1]) # sort according to completion time
                for k in range(len(sorted_index_completion_time_list)):
                    if sorted_index_completion_time_list[k][0] != -1: # is a job
                        maint_job_list.append(sorted_index_completion_time_list[k][0] + 1)
                    else : # is maintenance
                        if k != len(sorted_index_completion_time_list)-1: # if maintenance is not completed last
                            maint_job_list.append('M')
                maint_job_str = ' '.join([str(i) for i in maint_job_list])
                file.write(f'{maint_job_str}\n')
                machine+=1
            file.write('-------------------------------------\n')
        


def print_generated_schedule(file_id, file):
    parameters = Parameters()
    parameters.read_parameters('tests/base/base_'+ str(file_id) +'.txt')

    # generate a schedule from the base results
    resultParameters = ResultParameters()
    resultParameters.read_result('tests/base/base_'+ str(file_id) +'.txt','tests/base_result_1107/base_result_'+ str(file_id) +'.txt')
    resultParameters.generateOrder(file)


if __name__ == '__main__':
    # function to create the generated schedule txt files
    folder_name = 'tests/'
    path = folder_name + 'base_job_order_1109'
    if not os.path.isdir(path):
        os.makedirs(path)
    
    for i in range(1, 51):
        file = open(path + '/base_job_order_' + str(i) + '.txt', 'w+')
        print_generated_schedule(i, file)
