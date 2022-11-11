
import random

class temp():
    def __init__(self):
        self.Number_of_Stages = 5
        self.Number_of_Jobs = 10
        self.Number_of_Machines = [3,5,6,3,5]



'''
population_num=n : 對於每個方法的排列組合，都生成 n 個不同數值的解

'''
def generate_population(instance, population_num):
    stage_num = instance.Number_of_Stages
    job_num = instance.Number_of_Jobs
    machine_num = instance.Number_of_Machines

    # get max. machine
    max_machine  = max(machine_num)
    print("max_machine = ", max_machine)

    population = []
    for i in range(population_num):
        population.append([])
        for j in range(stage_num):
            population[i].append([])

            # job schedule
            for k in range(job_num):
                population[i][j].append(round(random.uniform(1, machine_num[j]+1), 2))

            # machine schedule
            # for k in range(machine_num[j]):
            for k in range(max_machine):
                population[i][j].append(round(random.uniform(k+1, k+2), 2))


    return population


if __name__ == "__main__":
    instance = temp()

    ans = generate_population(instance, 10)

    for i in range(len(ans)):
        for j in range(len(ans[i])):
            print(ans[i][j])
            print('\n')
        print("=================")
