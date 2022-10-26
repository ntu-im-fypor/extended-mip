import sys
from Models import Parameters
from Models.Gurobi import CompleteMIPModel, OldMIPModel
from Models.heuristic import HeuristicModel

def main():
    # read parameters from file
    if len(sys.argv) == 0:
        print("No parameters file specified")
        return
    file_path = sys.argv[1]
    parameters = Parameters()
    parameters.read_parameters(file_path)
    # build and solve the model
    model = CompleteMIPModel(parameters)
    model.run_and_solve()
    model.record_result()
    model.plot_result()

    heuristic_model = HeuristicModel(parameters)
    heuristic_model.run_and_solve()
    heuristic_model.record_result()



if __name__ == '__main__':
    main()