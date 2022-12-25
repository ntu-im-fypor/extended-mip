import pandas as pd
import math
import random

def greedy_initial(instance_iteration, job_float_order, machine_num_list) -> list:
  # instance_iteration: 目前總共是 80 個 instance(tests/base_1130 下的 50 個 和 test/benchmark_1203 下的 30 個)
  #                    , 要傳進來說現在是第幾個 instance
  #                    , 也就是 instance_iteration 應為 1-80 的數字
  # job_float_order: [0.4, 0.2, 0.6, 0.8]
  # machine_num_list: [2,2] -> 有兩個 stage, 每個 stage 都有 兩個 machine，不用管該 machine 是否有被使用
  # 回傳：該 instance 透過 greedy initial_job_listing 產生的 schedule, 
  #     ex: [[3.40, 3.20, 2.60, 1.80, 1.42, 2.61, 3.13], [1.40, 1.20, 3.60, 1.80, 1.55, 2.22, 3.18]]
  if instance_iteration <= 50:
    csv = pd.read_csv("extended/initial-job-listing-results/base_1130/base_" + str(instance_iteration) + ".csv")
  else:
    csv = pd.read_csv("extended/initial-job-listing-results/benchmark_1203/benchmark_" + str(instance_iteration) + ".csv")
  result = []
  for index, row in csv.iterrows():
    new = row['output'].replace('[', '').replace(']', '').replace('\'', '').split(',')
    temp = []
    for i in new:
      if i.strip() == 'M':
        temp.append(i.strip())
      else:
        temp.append(int(i.strip()))
    result.append(temp)
  print("order: ", result)

  temp_2 = []
  for i in range(max(machine_num_list)):
    temp_2.append(i+1)

  schedule_result = []
  for i in range(len(machine_num_list)):
    schedule_result.append(job_float_order+temp_2)

  # 切割 stage 為單位
  all = []
  for i in machine_num_list:
    stage = []
    for k in range(i):
      stage.append(result[0])
      result.pop(0)
    all.append(stage)

  for stage in all:
    stage_num = all.index(stage)+1
    for machine in stage:
      machine_num = stage.index(machine)+1
      for e in machine:
        if e != 'M':
          schedule_result[stage_num-1][e-1] += machine_num
        else:
          # first position -> maintain 0
          # no machine -> maintain 0 (no meaning)
          if machine.index(e)+1 == len(machine): # last position / first position when len = 1  (no meaning)
            schedule_result[stage_num-1][len(job_float_order)-1+machine_num] += 0.99
          elif machine.index(e)+1 != 1: # middle position
            smaller_job = machine[machine.index(e)-1]
            larger_job = machine[machine.index(e)+1]
            smaller_bd = schedule_result[stage_num-1][smaller_job-1] - math.floor(schedule_result[stage_num-1][smaller_job-1])
            larger_bd = schedule_result[stage_num-1][larger_job-1] - math.floor(schedule_result[stage_num-1][larger_job-1])
            schedule_result[stage_num-1][len(job_float_order)-1+machine_num] += random.uniform(smaller_bd, larger_bd)
  return schedule_result

print(greedy_initial(1, [0.4, 0.2, 0.6, 0.8], [3,2]))