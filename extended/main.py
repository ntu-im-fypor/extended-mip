import sys
import time
import xlsxwriter
import pandas as pd
from tokenize import String
from unittest import result
from Models import Parameters
# from Models.Gurobi import CompleteMIPModel, CompleteMIPModel_original, RelaxedMIPModel, SharedRelaxedMIPModel
# from Models.heuristic import MetaPSOModel, MetaGAModel, GreedyModel
from Models.heuristic import GreedyModel

def test_relaxation_result():
    result = []
    for i in range(31, 46):
        file_path = "tests/multiple_machine/base/base_" + str(i) + ".txt"
        # result_path = "Gurobi_results/due_time_02_long_prod_0418/job_time_" + str(i) + ".csv"
        parameters = Parameters()
        parameters.read_parameters(file_path)
        # build and solve the model
        model = CompleteMIPModel(parameters)
        result.append(model.run_and_solve())

    workbook = xlsxwriter.Workbook('Gurobi_results/0516_exp/multiple_machine/base_result.xlsx')
    worksheet = workbook.add_worksheet()
    for i in range(1, 16):
        # write operation perform
        worksheet.write(i, 0, result[i-1][0])
        worksheet.write(i, 1, result[i-1][1])
        worksheet.write(i, 2, result[i-1][2])

    workbook.close()

    # heuristic_model = HeuristicModel(parameters)
    # heuristic_model.run_and_solve()
    # heuristic_model.record_result()

def test_heuristic_model(scenario):
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
    df = pd.DataFrame(index=range(1, 31), columns=[
        "initial objective value", "initial shared job order", "initial schedule",
        "merge objective value", "merge shared job order", "merge schedule",
        # "no merge objective value", "no merge shared job order", "no merge schedule",
        "greedy time",
        "final objective value", "final shared job order", "final schedule",
        "time"])
    for i in range(30):
        print(scenario + "_" + str(i+1))
        # TODO: change parameters in Models/heuristic/ours_greedy.py, line 27-29, for single machine/multiple machine differences
        file_path = "extended/tests/multiple_machine/" + scenario + "/" + scenario + "_" + str(i+1) + ".txt"
        parameters = Parameters()
        parameters.read_parameters(file_path)
        start_time = time.time()
        # 1st T/F: use gurobi job order as initial job order
        # 2nd T/F: use ga after greedy
        heuristic_model = GreedyModel(parameters, False, True, file_path="extended/greedy-results/test.json", instance_num=i+1, job_weight_choice="WEDD", merge_step3_to_step2=True)
        
        heuristic_model.run_and_solve()
        df = heuristic_model.record_result(df, i)
        run_time = time.time() - start_time
        df.iloc[i]["time"] = run_time
        print("Run time: ", run_time)
        print("=====")
    df.to_csv('extended/greedy-results/final_test_0530/multiple_machine/' + scenario + '.csv')

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
    test_heuristic_model(scenario = 'base')
    test_heuristic_model(scenario = 'bottleneck_H')
    test_heuristic_model(scenario = 'bottleneck_H_2')
    test_heuristic_model(scenario = 'bottleneck_L')
    test_heuristic_model(scenario = 'maint_len_H')
    test_heuristic_model(scenario = 'maint_len_L')
    test_heuristic_model(scenario = 'queue_time_H')
    test_heuristic_model(scenario = 'queue_time_L')
    # run_initial_job_listing_for_GA_team()