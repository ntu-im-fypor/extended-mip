from Models import Parameters, SolutionModel
from utils.common import cast_parameters_to_instance
from utils.generate_population import generate_population
import numpy as np

class MetaPSOModel(SolutionModel):
    def __init__(self, parameters: Parameters):
        super().__init__(parameters)

    def run_and_solve(self, population_num: int = 10, iteration_num: int = 60, w: float = 0.8, c1: float = 1.5, c2: float = 1.5):
        """
        Run and solve the problem using PSO, and then store the output schedule into self.schedule.
        Then calculate the objective value of the schedule using record_result()
        """
        instance = cast_parameters_to_instance(self.parameters)
        print("Running and solving using PSOModel")
        # TODO: implement PSO algorithm here

        # generate population
        particles = generate_population(self.parameters, population_num)
        # initialize velocity as a 3-dimension array, 
        # the first dimension is the population, 
        # the second dimension is the stage, 
        # the third dimension is the job and machine
        velocity = np.zeros((population_num, self.parameters.Number_of_Stages, self.parameters.Number_of_Jobs + max(self.parameters.Number_of_Machines)))
        # initialize pbest
        pbest = particles
        # initialize gbest
        gbest = particles[0]
        gbest_obj = np.inf
        # for each iteration, update the velocity and position of each particle. 
        # And in each iteration we also check whether updated position is reasonable.
        # If not, we don't update the position and velocity of that particle.
        for _ in range(iteration_num):
            for j in range(population_num):
                # update velocity
                # TODO: current particles is not numpy array, so it can't be used in numpy array operation, 
                # TODO: we will wait for generate_population() update the return type from list to numpy array
                velocity[j] = w * velocity[j] + c1 * np.random.random() * (pbest[j] - particles[j]) + c2 * np.random.random() * (gbest - particles[j])
                # update position
                updated_position = particles[j] + velocity[j]
                schedule_obj = calculate_objective_value(updated_position, instance)
                # check whether the updated position is reasonable
                # if not, we don't update the position and velocity of that particle
                if schedule_obj != -1:
                    particles[j] = updated_position
                    # update pbest
                    if schedule_obj < gbest_obj:
                        gbest = updated_position
                        gbest_obj = schedule_obj
        self.schedule = gbest
        self.gbest_obj = gbest_obj
        print(f"PSOModel Finished, global best objective value: {gbest_obj}. And the schedule has been stored in self.schedule.")

    def record_result(self):
        """
        print out the objective value of self.schedule
        """
        print(f"The best objective value of PSOModel is {self.gbest_obj}")