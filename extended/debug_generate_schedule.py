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
    def __init__(self, sol, maint_sol) -> None:
        self.objVal = 0 # objective value
        self.shared_job_order = None # shared job order
        self.job_maintenance_order = [] # job and maintenance order on each machine



def test_objective_function():
    # read parameters from file
    if len(sys.argv) == 0:
        print("No parameters file specified")
        return
    file_id = sys.argv[1]
    parameters = Parameters()
    parameters.read_parameters('tests/benchmark/benchmark_'+ str(file_id) +'.txt')
    instance = cast_parameters_to_instance(parameters)

    print(instance.REMAIN)

    # resultParameters = ResultParameters()
    # resultParameters.read_result('tests/base/base_'+ str(file_id) +'.txt','tests/base_result_1107/base_result_'+ str(file_id) +'.txt')
    # resultParameters.generateJobMaintenanceOrder()
    # resultParameters.generateSharedJobOrder()

    # print(resultParameters.job_maintenance_order)
    # print(resultParameters.shared_job_order)
    # gurobi_obj = resultParameters.objVal
    # print(gurobi_obj)

    # heuristic_obj = None
    # if resultParameters.shared_job_order != None:
    #     heuristic_obj = generate_schedule(resultParameters.shared_job_order, resultParameters.job_maintenance_order, instance)
    # print(heuristic_obj)
    # return gurobi_obj, heuristic_obj

    
    # # generate a schedule from the base results
    # resultParameters = ResultParameters()
    # resultParameters.read_result('tests/base/base_'+ str(file_id) +'.txt','tests/base_result_1107/base_result_'+ str(file_id) +'.txt')
    # resultParameters.generateOrder()
    # print("Generated Ordering:")
    # print(resultParameters.schedule)
    # heuristic_model.record_result(resultParameters.schedule)
    # print("Gurobi objective value: ", resultParameters.objVal)
    # ### for listing and comparing all objective values
    # # return resultParameters.objVal, heuristic_model.record_result(resultParameters.schedule) # gurobi value, fn value



if __name__ == '__main__':
    sol_data = pd.read_csv('./tests/sol-before/dueweight_greedy_noswapping_sol.csv')
    maint_data = pd.read_csv('./tests/sol-before/dueweight_greedy_noswapping_maint_sol.csv')
    print(sol_data['benchmark'])
    print(maint_data['benchmark'])

    test_objective_function()

    ### function to list and compare all objective values
    # data = [['Gurobi obj', 'Generate Schedule obj']]
    # for i in range(1, 51):
    #     gurobi_obj, heuristic_obj = test_objective_function(i)
    #     # print(real_obj, unconstrained_obj)
    #     data.append([gurobi_obj, heuristic_obj])
    # df = pd.DataFrame(data)
    # df.to_csv('./tests/1124_test_generate_schedule.csv')
