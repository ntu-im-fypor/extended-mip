import sys
from tokenize import String
from unittest import result
from Models import Parameters
from Models.Gurobi import CompleteMIPModel, CompleteMIPModel_original
from utils.common import cast_parameters_to_instance
from utils.generate_schedule import generate_schedule
from Models.heuristic import MetaPSOModel, MetaGAModel
import pandas as pd
import numpy as np

class ResultParameters:
    def __init__(self, file_id, instance) -> None:
        self.file_id = file_id
        self.instance = instance
        self.objVal = 0 # objective value
        self.shared_job_order = [] # shared job order
        self.job_maintenance_order = [] # job and maintenance order on each machine
    
    def read_result(self, job_order_file_path, maint_order_file_path) -> None:
        job_order_data = pd.read_csv(job_order_file_path)
        self.shared_job_order = list(map(int, job_order_data['benchmark'][int(self.file_id)-1].replace("[", "").replace("]", "").split()))
        maint_order_data = pd.read_csv(maint_order_file_path)
        maint_order = list(map(int, maint_order_data['benchmark'][int(self.file_id)-1].replace("[", "").replace("]", "").replace(".", "").split()))
        self.job_maintenance_order = []
        for i in range(sum(self.instance.MACHINES_NUM)):
            job_order_for_machine = []
            for _, job in enumerate(self.shared_job_order):
                if maint_order[i] == len(job_order_for_machine):
                    job_order_for_machine.append('M')
                    job_order_for_machine.append(job)
                else:
                    job_order_for_machine.append(job)
            self.job_maintenance_order.append(job_order_for_machine)


def test_objective_function():
    # read parameters from file
    if len(sys.argv) == 0:
        print("No parameters file specified")
        return
    file_id = sys.argv[1]
    parameters = Parameters()
    parameters.read_parameters('tests/benchmark_1203/benchmark_'+ str(file_id) +'.txt')
    instance = cast_parameters_to_instance(parameters)
    
    resultParameters = ResultParameters(file_id, instance)
    resultParameters.read_result('./tests/sol-before/dueweight_greedy_noswapping_sol.csv','./tests/sol-before/dueweight_greedy_noswapping_maint_sol.csv')

    print(resultParameters.job_maintenance_order)
    heuristic_obj = generate_schedule(resultParameters.shared_job_order, resultParameters.job_maintenance_order, instance)
    print(heuristic_obj)
    return heuristic_obj


if __name__ == '__main__':
    test_objective_function()

    ### function to list and compare all objective values
    # heuristic_obj_list = []
    # for i in range(1, 31):
    #     heuristic_obj = test_objective_function(i)
    #     heuristic_obj_list.append(heuristic_obj)
    # obj_before = pd.read_csv('./tests/sol-before/dueweight_greedy_noswapping_obj.csv')
    # df = pd.DataFrame(data = {'Obj fn before': obj_before['benchmark'], 'Our Obj fn': heuristic_obj_list})
    # df.to_csv('./tests/compare_obj_fn.csv')
