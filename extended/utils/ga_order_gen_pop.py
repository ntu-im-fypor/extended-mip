# from Models import Parameters
import numpy as np

def ga_order_gen_pop(job_count, population_num = 30):

    # population number has to be greater than or euqal to 3
    if(population_num < 3):
        return 0
    # =================== append greedy and WEDD solution into population: TODO (or do this outside of this function)===================

    # =================== generate random population ===================
    return_value = []
    while len(return_value) < population_num:
        random_order = np.random.permutation(list(range(1, job_count + 1)))
        order_existed = False
        for i in range(len(return_value)):
            if (random_order == return_value[i]).all():
                order_existed = True
                break
        if not order_existed:
            return_value.append(random_order.tolist())

    return return_value

# test
print(ga_order_gen_pop(10, 30)[0])