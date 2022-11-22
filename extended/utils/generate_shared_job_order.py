def generate_shared_job_order(instance) -> list:
  due_time = instance.DUE_TIME
  weight = instance.WEIGHT

  WEDD = []
  sorted_WEDD = []
  for i in range(len(due_time)):
    WEDD.append(due_time[i]/weight[i])
    sorted_WEDD.append(due_time[i]/weight[i])
  sorted_WEDD.sort()

  job_order = []
  for i in sorted_WEDD:
    job_order.append(WEDD.index(i)+1)

  result = [job_order]
  for i in range(len(job_order) - 1):
    job_order[i], job_order[i+1] = job_order[i+1], job_order[i]
    new = job_order.copy()
    result.append(new)
    job_order[i], job_order[i+1] = job_order[i+1], job_order[i]
  return result

# test
# class Instance:
#     JOBS_NUM = 3
#     STAGES_NUMBER = 2
#     MACHINES_NUM = [2, 1]
#     DISCOUNT = [0.8, 0.7, 0.9]
#     MAINT_LEN = [5, 4, 6]
#     REMAIN = [3, 6, 0]
#     INIT_PROD_TIME = [[10, 15, 13], [12, 17, 15], [8, 15, 12]]
#     DUE_TIME = [30, 40, 30]
#     WEIGHT = [100, 200, 200]
#     QUEUE_LIMIT = [10, 10, 0]
#     MAX_MACHINES_NUM = max(MACHINES_NUM)
# instance = Instance()
# generate_shared_job_order(instance)
