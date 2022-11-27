import sys
import pandas as pd
from tokenize import String
from unittest import result
from Models import Parameters
from Models.Gurobi import CompleteMIPModel, CompleteMIPModel_original
from Models.heuristic import MetaPSOModel, MetaGAModel, GreedyModel

def test_relaxation_result():
    result = []
    for i in range(1, 51):
        file_path = "/Users/ckocp3/Downloads/base/base_" + str(i) + ".txt"
        # file_path = "/Users/ckocp3/Downloads/base_1105/base_" + str(i) + ".txt"
        result_path = "/Users/ckocp3/Downloads/base_result_1107/base_result_" + str(i) + ".txt"
        parameters = Parameters()
        parameters.read_parameters(file_path)
        # build and solve the model
        model = CompleteMIPModel(parameters)
        result.append(model.run_and_solve(result_path))

    # workbook = xlsxwriter.Workbook('relaxation_result.xlsx')
    # worksheet = workbook.add_worksheet()
    # for i in range(1, 3):
    #     # write operation perform
    #     worksheet.write(i, 0, result[i-1][0])
    #     worksheet.write(i, 1, result[i-1][1])
    #     worksheet.write(i, 2, result[i-1][2])

    # workbook.close()

    # heuristic_model = HeuristicModel(parameters)
    # heuristic_model.run_and_solve()
    # heuristic_model.record_result()

def test_heuristic_model():
    # # read parameters from file
    # if len(sys.argv) <= 1:
    #     print("No parameters file specified")
    #     return
    # # print(sys.argv)
    # file_path = sys.argv[1]
    file_path = "tests/base/base_3.txt"
    parameters = Parameters()
    parameters.read_parameters(file_path)
    # use input to choose which model to use
    model_type = input("Please choose which model to use: 1. MetaPSOModel, 2. MetaGAModel, 3. GreedyModel, 4. CompleteMIPModel")
    heuristic_model = None
    if model_type == "1":
        heuristic_model = MetaPSOModel(parameters)
    elif model_type == "2":
        heuristic_model = MetaGAModel(parameters)
    elif model_type == "3":
        heuristic_model = GreedyModel(parameters, file_path="greedy-results/test.json")
    elif model_type == "4":
        heuristic_model = CompleteMIPModel(parameters)
    else:
        print("Invalid model type")
        return

    heuristic_model.run_and_solve()
    heuristic_model.record_result()

if __name__ == '__main__':
    # test_relaxation_result()
    test_heuristic_model()
