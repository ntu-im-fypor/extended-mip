def ga_crossover(schedule_list, job_num, machine_num, job_point, machine_point) -> list:
  for schedule in schedule_list:
    print("schedule:", schedule)

  stage_num = len(schedule_list[0])

  # divide job list and machine list
  schedule_1_job = []
  schedule_1_machine = []
  schedule_2_job = []
  schedule_2_machine = []
  for stage in schedule_list[0]:
    schedule_1_job.append(stage[:job_num])
    schedule_1_machine.append(stage[-(machine_num):])
  for stage in schedule_list[1]:
    schedule_2_job.append(stage[:job_num])
    schedule_2_machine.append(stage[-(machine_num):])

  # job
  job_1_point_before = []
  job_1_point_after = []
  job_2_point_before = []
  job_2_point_after = []
  for stage in schedule_1_job:
    job_1_point_before.append(stage[:job_point])
    job_1_point_after.append(stage[-(job_num - job_point):])
  for stage in schedule_2_job:
    job_2_point_before.append(stage[:job_point])
    job_2_point_after.append(stage[-(job_num - job_point):])

  for i in range(stage_num):
    job_1_point_before[i] += job_2_point_after[i]
    job_2_point_before[i] += job_1_point_after[i]

  # test
  """
  for i in schedule_1_machine:
    print(i)
  print('-------')
  for i in schedule_2_machine:
    print(i)
  print('------------------')
  for i in machine_1_point_before:
    print(i)
  print('-------')
  for i in machine_2_point_before:
    print(i)
  print('------------------')
  """
  
  # machine
  machine_1_point_before = []
  machine_1_point_after = []
  machine_2_point_before = []
  machine_2_point_after = []
  for stage in schedule_1_machine:
    machine_1_point_before.append(stage[:machine_point])
    machine_1_point_after.append(stage[-(machine_num - machine_point):])
  for stage in schedule_2_machine:
    machine_2_point_before.append(stage[:machine_point])
    machine_2_point_after.append(stage[-(machine_num - machine_point):])

  for i in range(stage_num):
    machine_1_point_before[i] += machine_2_point_after[i]
    machine_2_point_before[i] += machine_1_point_after[i]

  # test
  """
  for i in schedule_1_machine:
    print(i)
  print('-------')
  for i in schedule_2_machine:
    print(i)
  print('------------------')
  for i in machine_1_point_before:
    print(i)
  print('-------')
  for i in machine_2_point_before:
    print(i)
  print('------------------')
  """

  # whole
  for i in range(stage_num):
    job_1_point_before[i] += machine_1_point_before[i]
    job_2_point_before[i] += machine_2_point_before[i]

  # test
  """
  for i in schedule_list[0]:
    print(i)
  print('-------')
  for i in schedule_list[1]:
    print(i)
  print('------------------')
  for i in job_1_point_before:
    print(i)
  print('-------')
  for i in job_2_point_before:
    print(i)
  print('------------------')
  """
    
  result = []
  result.append(job_1_point_before)
  result.append(job_2_point_before)
  return result

# test
"""
schedule_list = [[[1.2, 1.4, 2.6, 0.2, 3.3, 0.2, 1.3, 0.5], [1.3, 1.6, 0.3, 1.2, 0.3, 0.1, 0.3, 0.6]], [[1.8, 1.3, 2.5, 0, 2.3, 0.5, 2.3, 1.5], [2.2, 1.5, 1.3, 1.1, 0, 0.2, 1.3, 4.3]]]
a = ga_crossover(schedule_list, job_num=4, machine_num=4, job_point=2, machine_point=2)
print(a)
"""