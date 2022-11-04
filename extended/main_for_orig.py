import sys
from Models import Parameters, CompleteMIPModel_original

def main():
    runtime = []
    objVal = []
    MIPGap = []
    objBd = []
    for i in range(1, 31):
        # read parameters from file
        # if len(sys.argv) == 0:
        #     print("No parameters file specified")
        #     return
        # file_path = sys.argv[1]
        file_path = "/Users/ckocp3/Downloads/benchmark_small_transformed/benchmark_small_transformed_" + str(i) + ".txt"
        # file_path = "/Users/ckocp3/Downloads/benchmark/benchmark_" + str(i) + ".txt"
        parameters = Parameters()
        parameters.read_parameters(file_path)
        # build and solve the model
        model = CompleteMIPModel_original(parameters)
        result = model.run_and_solve()
        # model.plot_result()
        print("Final result is", result)
        runtime.append(result[0])
        objVal.append(result[1])
        MIPGap.append(result[2])
        objBd.append(result[3])

if __name__ == '__main__':
    main()