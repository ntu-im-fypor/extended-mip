import random
def ga_order_crossover(job_order_lists) -> list:

  # print(job_order_lists)

  job_count = len(job_order_lists[0])
  crosspoint = random.randint(1, job_count - 2)
  # print(crosspoint)
  job_unarranged = list(range(1, job_count + 1))

  new_job_order = []
  for i in range(crosspoint):
    new_job_order.append(job_order_lists[0][i])
    job_unarranged.remove(new_job_order[i])
  job_initial_order = []
  for i in range(len(job_unarranged)):
    job_initial_order.append(job_order_lists[1].index(job_unarranged[i]))
  for i in range(job_count - crosspoint):
    first_job_index = job_initial_order.index(min(job_initial_order))
    new_job_order.append(job_unarranged[first_job_index])
    del job_unarranged[first_job_index]
    del job_initial_order[first_job_index]

  print(new_job_order)
  return new_job_order

# test
# job_order_list1 = [2, 1, 4, 7, 5, 8, 6, 3, 9, 10]
# job_order_list2 = [3, 7, 9, 2, 1, 5, 10, 8, 6, 4]

# ga_order_crossover([job_order_list1, job_order_list2])