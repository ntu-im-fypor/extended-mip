import sys
import time
import xlsxwriter
import pandas as pd
from tokenize import String
from unittest import result
from Models import Parameters
from Models.Gurobi import CompleteMIPModel, CompleteMIPModel_original, RelaxedMIPModel, SharedRelaxedMIPModel
from Models.heuristic import MetaPSOModel, MetaGAModel, GreedyModel
from Models.heuristic import MetaPSOModel, MetaGAModel, GreedyModel

def test_relaxation_result():
    result = []
    for i in range(1, 31):
        file_path = "extended/tests/no_maint_inf_queue_0317/base_" + str(i) + ".txt"
        result_path = "Gurobi_results/shared_no_maint_inf_queue_schedule/job_time_" + str(i) + ".csv"
        parameters = Parameters()
        parameters.read_parameters(file_path)
        # build and solve the model
        model = SharedRelaxedMIPModel(parameters)
        result.append(model.run_and_solve(result_path))

    workbook = xlsxwriter.Workbook('relaxation_result.xlsx')
    worksheet = workbook.add_worksheet()
    for i in range(1, 31):
        # write operation perform
        worksheet.write(i, 0, result[i-1][0])
        worksheet.write(i, 1, result[i-1][1])
        worksheet.write(i, 2, result[i-1][2])

    workbook.close()

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
    df = pd.DataFrame(index=range(1, 51), columns=[ # base_1125/base_1130: 51, 學姊's benchmark: 31
        "initial objective value", "initial shared job order", "initial schedule",
        "process objective value", "process shared job order", "process schedule",
        "final objective value", "final shared job order", "final schedule",
        "time"])
    for i in range(30): # base_1125/base_1130: 50, 學姊's benchmark: 30
        print("base_" + str(i+1))
        # test with base_1125
        # file_path = "tests/base_1125/base_" + str(i+1) + ".txt"
        # test with base_1130
        file_path = "extended/tests/no_maint_inf_queue_0317/base_" + str(i+1) + ".txt"
        file_path = "extended/tests/no_maint_inf_queue_0317/base_" + str(i+1) + ".txt"
        # test with 學姊's benchmark
        # file_path = "tests/benchmark/benchmark_" + str(i+1) + ".txt"
        parameters = Parameters()
        parameters.read_parameters(file_path)
        start_time = time.time()
        # 1st T/F: use gurobi job order as initial job order
        # 2nd T/F: use ga after greedy
        heuristic_model = GreedyModel(parameters, False, True, file_path="extended/greedy-results/test.json", instance_num=i+1)
        
        heuristic_model.run_and_solve()
        df = heuristic_model.record_result(df, i)
        run_time = time.time() - start_time
        df.iloc[i]["time"] = run_time
        print("Run time: ", run_time)
        print("=====")
    # test with base_1125
    # df.to_csv('greedy-results/base_1125.csv')
    # test with base_1130
    df.to_csv('extended/greedy-results/no-maint-inf-queue-results/no_maint_inf_queue_0411_5.csv')
    # test with 學姊's benchmark
    # df.to_csv('greedy-results/benchmark.csv')

# def run_initial_job_listing_for_GA_team():
#     for i in range(1, 51):
#         file_path = f"tests/base_1130/base_{i}.txt"
#         parameters = Parameters()
#         parameters.read_parameters(file_path)
#         heuristic_model = GreedyModel(parameters, file_path=f"tests/base_1130/base_{i}.json")
#         heuristic_model.run_initial_and_save_result(f"initial-job-listing-results/base_1130/base_{i}.csv")
#     for i in range(1, 31):
#         file_path = f"tests/benchmark_1203/benchmark_{i}.txt"
#         parameters = Parameters()
#         parameters.read_parameters(file_path)
#         heuristic_model = GreedyModel(parameters, file_path=f"tests/benchmark_1203/benchmark_{i}.json")
#         heuristic_model.run_initial_and_save_result(f"initial-job-listing-results/benchmark_1203/benchmark_{i}.csv")

if __name__ == '__main__':
    # test_relaxation_result()
    test_heuristic_model()
    # run_initial_job_listing_for_GA_team()
