import sys
import time
import pandas as pd
from tokenize import String
from unittest import result
from Models import Parameters
from Models.Gurobi import CompleteMIPModel, CompleteMIPModel_original
# from Models.heuristic import MetaPSOModel, MetaGAModel, GreedyModel
from Models.heuristic import MetaGAModel
import time



def test_relaxation_result():
    result = []
    # for i in range(1, 51):
    #     file_path = "/Users/ckocp3/Downloads/base/base_" + str(i) + ".txt"
    #     # file_path = "/Users/ckocp3/Downloads/base_1105/base_" + str(i) + ".txt"
    #     result_path = "/Users/ckocp3/Downloads/base_result_1107/base_result_" + str(i) + ".txt"
    #     parameters = Parameters()
    #     parameters.read_parameters(file_path)
    #     # build and solve the model
    #     model = CompleteMIPModel(parameters)
    #     result.append(model.run_and_solve(result_path))

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
    heuristic_model = None

    # iterate all instance
    population_number = [30, 50]
    machine_mutation_rate =  [0.05, 0.1]
    job_mutation_rate = [0.05, 0.1]

    for p_num in population_number:
        for m_rate in machine_mutation_rate:
            for j_rate in job_mutation_rate:
                result = {
                "final objective value": [],
                "first objective value": [],
                "final shared job order": [],
                "final schedule": [],
                "time": []
                }

                for i in range(50):
                    file_path = "tests/base_1130/base_" + str(i+1) + ".txt"
                    parameters = Parameters()
                    parameters.read_parameters(file_path)

                    # create model
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



                    # Parameter Tuning
                    ''''
                    1. population number: [30, 40, 50]
                    2. machine mutation rate: [0.02, 0.04, 0.06, 0.08, 0.1]
                    3. job mutation rate: [0.02, 0.04, 0.06, 0.08, 0.1]
                    '''

                    init_time = time.time()
                    heuristic_model.run_and_solve(
                        job_mutation_rate = j_rate,
                        machine_mutation_rate = m_rate,
                        population_num = p_num)
                    obj, share_job_order, schedule, init_obj = heuristic_model.record_result()
                    finish_time = time.time()
                    result['final objective value'].append(obj)
                    result['final shared job order'].append(share_job_order)
                    result['final schedule'].append(schedule)
                    result['time'].append(finish_time-init_time)
                    result['first objective value'].append(init_obj)
                    print("duration = ", finish_time-init_time)

                output = pd.DataFrame(result)
                output_filename = 'GA-results/GA_base_1202_' + 'p_num_' + str(p_num) + '_m_rate_' + str(m_rate) + '_j_rate_' + str(j_rate) + '.csv'
                output.to_csv(output_filename, index=True)
                print('====== finish ', output_filename, ' =========')

if __name__ == '__main__':
    # test_relaxation_result()
    test_heuristic_model()
