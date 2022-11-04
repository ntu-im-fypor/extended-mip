from Models import Parameters
from Models.Gurobi import CompleteMIPModel
import pandas as pd
from enum import Enum

class Trend(Enum):
    INCLINE = 1
    DECLINE = 2
def run_base_and_compare_trend():
    # There are 50 base cases, and for every base case, there are fourteen scenarios, where each scenario has 5 instances to test
    # store the results of different scenarios in different xlsx files
    scenarios = [
        ("discount_H", Trend.INCLINE), 
        ("discount_L", Trend.DECLINE),
        ("due_time_H", Trend.DECLINE),
        ("due_time_L", Trend.INCLINE),
        ("initial_production_time_H", Trend.INCLINE),
        ("initial_production_time_L", Trend.DECLINE),
        ("maintenance_length_H", Trend.INCLINE),
        ("maintenance_length_L", Trend.DECLINE),
        ("penalty_H", Trend.INCLINE),
        ("penalty_L", Trend.DECLINE),
        ("queue_time_limit_H", Trend.DECLINE),
        ("queue_time_limit_L", Trend.INCLINE),
        ("unfinished_H", Trend.INCLINE),
        ("unfinished_L", Trend.DECLINE)
    ]
    for scenario in scenarios:
        run_scenario(scenario)

def run_scenario(scenario: tuple):
    # run every base case and its 5 instances for a given scenario
    # create a dataframe to store the results
    scenario_df = pd.DataFrame(columns=["base_case", "instance_1", "instance_2", "instance_3", "instance_4", "instance_5", "is_unreasonable"])

    for i in range(1, 51):
        obj_list = []
        is_unreasonable = False
        print("Running Base case: ", i, "...")
        base_file_path = f"./scenario/base/base_{i}.txt"
        base_parameters = Parameters()
        base_parameters.read_parameters(base_file_path)
        model = CompleteMIPModel(base_parameters)
        model.run_and_solve()
        base_obj_val = model.get_objective_value()
        obj_list.append(base_obj_val)

        print("Running Scenario: ", scenario[0], "...")
        for j in range(1, 6):
            file_path = f"./scenario/{scenario[0]}/base_{i}_{scenario[0]}_{j}.txt"
            parameters = Parameters()
            parameters.read_parameters(file_path)
            model = CompleteMIPModel(parameters)
            model.run_and_solve()
            obj_val = model.get_objective_value()
            if scenario[1] == Trend.INCLINE:
                if obj_val < base_obj_val:
                    is_unreasonable = True
            else:
                if obj_val > base_obj_val:
                    is_unreasonable = True
            obj_list.append(obj_val)
            print(f"base case {i}, scenario {scenario[0]}, instance {j}, obj val: {obj_val}")
        # append is_reasonable to the end of the list
        obj_list.append( 1 if is_unreasonable else 0)
        scenario_df.loc[i] = obj_list
    scenario_df.to_excel(f"./scenario/results/{scenario[0]}.xlsx")

if __name__ == '__main__':
    run_base_and_compare_trend()