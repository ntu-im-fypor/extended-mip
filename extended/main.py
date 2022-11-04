import sys
import xlsxwriter
from tokenize import String
from unittest import result
from Models import Parameters
from Models.Gurobi import CompleteMIPModel
from Models.heuristic import HeuristicModel
import pandas as pd

def main():
    # read parameters from file
    # if len(sys.argv) == 0:
    #     print("No parameters file specified")
    #     return
    # file_path = sys.argv[1]
    result = []
    for i in range(1, 51):
        # file_path = "/Users/ckocp3/Downloads/base/base_" + str(i) + ".txt"
        file_path = "/Users/ckocp3/Downloads/base_1104/base_" + str(i) + ".txt"
        parameters = Parameters()
        parameters.read_parameters(file_path)
        # build and solve the model
        model = CompleteMIPModel(parameters)
        result.append(model.run_and_solve())

    workbook = xlsxwriter.Workbook('relaxation_result.xlsx')
    worksheet = workbook.add_worksheet()
    for i in range(1, 51):
        # write operation perform
        worksheet.write(i, 0, result[i-1][0])
        worksheet.write(i, 1, result[i-1][1])
     
    workbook.close()

    # heuristic_model = HeuristicModel(parameters)
    # heuristic_model.run_and_solve()
    # heuristic_model.record_result()

if __name__ == '__main__':
    main()