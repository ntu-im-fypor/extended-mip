from Models import Parameters, CompleteMIPModel

def main():
    # read parameters from file
    parameters = Parameters()
    parameters.read_parameters('small_case.txt')
    # build and solve the model
    model = CompleteMIPModel(parameters)
    model.run_and_solve()


if __name__ == '__main__':
    main()