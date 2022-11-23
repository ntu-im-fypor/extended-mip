import sys
from tokenize import String
from unittest import result
from Models import Parameters
from Models.Gurobi import CompleteMIPModel, CompleteMIPModel_original
from utils.schedule_objective_value_calculation import calculate_objective_value, transform_parameters_to_instance, print_instance
from Models.heuristic import MetaPSOModel, MetaGAModel
import pandas as pd
import numpy as np
from check_cycle import ResultParameters, Graph

def test_objective_function():
    # read parameters from file
    if len(sys.argv) == 0:
        print("No parameters file specified")
        return
    file_id = sys.argv[1]
    parameters = Parameters()
    parameters.read_parameters('tests/base/base_'+ str(file_id) +'.txt')
    instance = transform_parameters_to_instance(parameters)

    resultParameters = ResultParameters()
    resultParameters.read_result('tests/base/base_'+ str(file_id) +'.txt','tests/base_result_1107/base_result_'+ str(file_id) +'.txt')
    resultParameters.generateJobMaintenanceOrder()
    resultParameters.generateSharedJobOrder()

    print(resultParameters.job_maintenance_order)
    print(resultParameters.shared_job_order)



    
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
    test_objective_function()

    ### function to list and compare all objective values
    # data = [['Gurobi obj', 'Constrained obj']]
    # for i in range(1, 51):
    #     real_obj, unconstrained_obj = test_objective_function(i)
    #     print(real_obj, unconstrained_obj)
    #     data.append([real_obj, unconstrained_obj])
    # df = pd.DataFrame(data)
    # df.to_csv('./tests/1108_objective_values_constrained.csv')
