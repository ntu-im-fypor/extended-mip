import sys
import time
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
    # # read parameters from fileˇ
    # if len(sys.argv) <= 1:
    #     print("No parameters file specified")
    #     return
    # # print(sys.argv)
    # file_path = sys.argv[1]
    # file_path = "tests/base_1125/base_2.txt"
    # parameters = Parameters()
    # parameters.read_parameters(file_path)
    # use input to choose which model to use
    model_type = input("Please choose which model to use: 1. MetaPSOModel, 2. MetaGAModel, 3. GreedyModel, 4. CompleteMIPModel")
    df = pd.DataFrame(index=range(1, 51), columns=[ # base_1125/base_1130: 51, 學姊's benchmark: 31
        "initial objective value", "initial shared job order", "initial schedule",
        "process objective value", "process shared job order", "process schedule",
        "final objective value", "final shared job order", "final schedule",
        "time"])
    for i in range(50): # base_1125/base_1130: 50, 學姊's benchmark: 30
        print("base_" + str(i+1))
        # test with base_1125
        # file_path = "tests/base_1125/base_" + str(i+1) + ".txt"
        # test with base_1130
        file_path = "tests/base_1130/base_" + str(i+1) + ".txt"
        # test with 學姊's benchmark
        # file_path = "tests/benchmark/benchmark_" + str(i+1) + ".txt"
        parameters = Parameters()
        parameters.read_parameters(file_path)
        start_time = time.time()
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
        df = heuristic_model.record_result(df, i)
        run_time = time.time() - start_time
        df.iloc[i]["time"] = run_time
        print("Run time: ", run_time)
        print("=====")
    # test with base_1125
    # df.to_csv('greedy-results/base_1125.csv')
    # test with base_1130
    df.to_csv('greedy-results/base_1130_1229update.csv')
    # test with 學姊's benchmark
    # df.to_csv('greedy-results/benchmark.csv')

def run_initial_job_listing_for_GA_team():
    for i in range(1, 51):
        file_path = f"tests/base_1130/base_{i}.txt"
        parameters = Parameters()
        parameters.read_parameters(file_path)
        heuristic_model = GreedyModel(parameters, file_path=f"tests/base_1130/base_{i}.json")
        heuristic_model.run_initial_and_save_result(f"initial-job-listing-results/base_1130/base_{i}.csv")
    for i in range(1, 31):
        file_path = f"tests/benchmark_1203/benchmark_{i}.txt"
        parameters = Parameters()
        parameters.read_parameters(file_path)
        heuristic_model = GreedyModel(parameters, file_path=f"tests/benchmark_1203/benchmark_{i}.json")
        heuristic_model.run_initial_and_save_result(f"initial-job-listing-results/benchmark_1203/benchmark_{i}.csv")


if __name__ == '__main__':
    # test_relaxation_result()
    test_heuristic_model()
    # run_initial_job_listing_for_GA_team()
