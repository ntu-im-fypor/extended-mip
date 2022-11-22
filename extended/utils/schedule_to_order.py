import math

def findFloats(listOfFloats, value):
  for i, number in enumerate(listOfFloats):
      if abs(number-value) < 0.00001:
        return i
  
def generate_shared_job_order(schedule, max_machine_num) -> list:
  output = []
  for stage in schedule:
    for num in range(max_machine_num):
      temp_job = []
      temp_machine = 0
      for i in stage:
        if math.floor(i) == (num+1):
          if i in stage[-(max_machine_num):]:
            temp_machine = i
          else:
            temp_job.append(i)
      temp_job.sort()

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

# test
max_machine_num = 3
schedule = [[3.40, 3.20, 2.60, 1.80, 1.42, 2.61, 3.13], [1.40, 1.20, 3.60, 1.80, 1.55, 2.22, 3.18]]
print(generate_shared_job_order(schedule, max_machine_num))
# expected: [['M', 4], [3, 'M'], ['M', 2, 1],[2, 1, 'M', 4], ['M', 3]]
    
