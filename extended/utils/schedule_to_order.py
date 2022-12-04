import math

def findFloats(listOfFloats, value):
  for i, number in enumerate(listOfFloats):
      if abs(number-value) < 0.00001:
        return i

# generate share job order (1-dim list)
def schedule_to_share_job_order_list(schedule, max_machine_num) -> list:
  job_schedule = list(schedule[0][:-(max_machine_num)])
  job_schedule = [job_schedule[i] % 1 for i in range(len(job_schedule))]
  output = [i+1 for i in range(len(job_schedule))]
  output = [x for _,x in sorted(zip(job_schedule,output))]
  return output

# generate whole schedule
def generate_shared_job_order(schedule, max_machine_num, machine_num) -> list:
  output = []

  # 針對每個 stage
  for index, stage in enumerate(schedule):
    # 針對每個機器生成 temp_job list
    for num in range(max_machine_num):
      temp_job = []
      temp_machine = 0
      # 該個 stage 的每個數值 (包含 job & maintenance)
      # TODO: 改成用 index 去看，才可以避免maintenance 數字撞擊
      for i in range(len(stage)):
        if math.floor(stage[i]) == (num+1):
          if i >= (len(stage) - max_machine_num):
            temp_machine = stage[i]
          else:
            temp_job.append(stage[i])
      temp_job.sort()
      if(num < machine_num[index] and len(temp_job) == 0):
        temp_job = ['NO_ASSIGN']

      if(len(temp_job) == 1 and temp_job[0] == 'NO_ASSIGN'):
        output.append(['M'])
      else:
        temp_result = []
        bk = True
        for job in temp_job:
          if (temp_machine < job) & bk:
            temp_result.append('M')
            temp_result.append(findFloats(stage, job)+1)
            bk = False
          else:
            temp_result.append(findFloats(stage, job)+1)

        if ('M' not in temp_result) & (len(temp_result) > 0):
          temp_result.append('M')

        if len(temp_result) > 0:
          output.append(temp_result)
  return output

# # test
# max_machine_num = 3
# # schedule = [[3.40, 3.20, 2.60, 1.80, 1.42, 2.61, 3.13], [1.40, 1.20, 3.60, 1.80, 1.55, 2.22, 3.18]]
# schedule =  [[2.09090909 ,3.54545455 ,1.63636364 ,3.81818182 ,1.36363636 ,1.45454545
#  , 1.90909091 ,1.18181818 ,1.72727273 ,2.27272727 ,1.22351419 ,2.35062122
#  , 3.66912985],
#  [2.09090909,1.54545455,2.63636364,2.81818182,2.36363636,2.45454545
# ,1.90909091,2.18181818,1.72727273,1.27272727,1.58253683,2.86471603
# ,3.99999991],
#  [2.09090909,2.54545455,2.63636364,1.81818182,1.36363636,1.45454545
#  ,2.90909091,2.18181818,1.72727273,2.27272727,1.92022143,2.14569305
# , 3.99999991],
#  [2.09090909,1.54545455,2.63636364,2.81818182,2.36363636,2.45454545
# , 2.90909091,2.18181818,2.72727273,2.27272727,1.54545455,2.18181818
# , 3.99999991]]
# # sjr = schedule_to_share_job_order_list(schedule, max_machine_num)
# sjr = [3,2,2,2]
# print("sjr = ", sjr)
# print(generate_shared_job_order(schedule, max_machine_num,sjr))
# # expected: [['M', 4], [3, 'M'], ['M', 2, 1],[2, 1, 'M', 4], ['M', 3]]




