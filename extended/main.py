import sys
from Models import Parameters, CompleteMIPModel, OldMIPModel

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
    model.plot_result()



if __name__ == '__main__':
    main()