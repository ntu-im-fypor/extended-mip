import random
def ga_order_crossover(job_order_lists) -> list:

  # print(job_order_lists)

  job_count = len(job_order_lists[0])
  crosspoint = random.randint(1, job_count - 2)
  # print(crosspoint)
  job_unarranged_list = []
  for i in range(2):
    job_unarranged_list.append(list(range(1, job_count + 1)))

  new_job_orders = [[], []]
  for i in range(2):
    for j in range(crosspoint):
      new_job_orders[i].append(job_order_lists[i][j])
      job_unarranged_list[i].remove(new_job_orders[i][j])
    job_initial_order = []
    for j in range(len(job_unarranged_list[i])):
      job_initial_order.append(job_order_lists[(i + 1) % 2].index(job_unarranged_list[i][j]))
    for j in range(job_count - crosspoint):
      first_job_index = job_initial_order.index(min(job_initial_order))
      new_job_orders[i].append(job_unarranged_list[i][first_job_index])
      del job_unarranged_list[i][first_job_index]
      del job_initial_order[first_job_index]

  # print(new_job_order)
  return new_job_orders