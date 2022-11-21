import random
import math

# ex: job_possiblility-> 0.0007
# ex: iteration -> 1
# ex: job_float_order -> [0.2, 0.4, 0.6, 0.8]
def ga_mutation(schedule, job_possibility, machine_possibility, job_num, max_machine_num, iteration, job_float_order) -> list:
  # print("==============================")
  # print("schedule = ")
  # print(schedule)
  # print("job_possibility = ", job_possibility)
  # print("machine_possibility = ", machine_possibility)
  # print("job_num = ", job_num)
  # print("max_machine_num", max_machine_num)
  # # iteration, job_float_order
  # print("iteration = ", iteration)
  # print("job_float_order = ", job_float_order)
  # print("==============================")





  # job
  if random.random() < job_possibility:
    chosen_station_num = random.randint(0,len(schedule)-1)
    # print("chosen_station_num = ", chosen_station_num) # expected an integer
    job_schedule = schedule[chosen_station_num][:job_num]
    job_schedule.reverse()
    # print("job_schedule = ", job_schedule)
    machine_schedule = schedule[chosen_station_num][-(max_machine_num):]
    schedule[chosen_station_num] = job_schedule + machine_schedule
    for i in range(len(schedule[chosen_station_num])):
      if i < job_num:
        # print("schedule[chosen_station_num][i] = ", schedule[chosen_station_num][i])
        schedule[chosen_station_num][i] = math.floor(schedule[chosen_station_num][i]) + job_float_order[i]

  # machine
  if random.random() < machine_possibility:
    chosen_station_num = random.randint(0,len(schedule)-1)

    # key: machine index, value: [jobs index]
    job_on_machine_dict = {}
    for machine_ind in range(max_machine_num):
      job_on_machine_dict[machine_ind] = []
    for job_ind in range(job_num):
      # print("schedule[chosen_station_num][job_ind] = ", schedule[chosen_station_num][job_ind])
      int_part = math.floor(schedule[chosen_station_num][job_ind])
      job_on_machine_dict[int_part-1].append(job_ind)
    for machine_ind in range(max_machine_num):
      if len(job_on_machine_dict[machine_ind]) != 0:
        chosen_job_index = random.choice(job_on_machine_dict[machine_ind])
        offset = (0.1 ** (iteration+2))/(job_num+1)
        if schedule[chosen_station_num][job_num+machine_ind] > schedule[chosen_station_num][chosen_job_index]:
          schedule[chosen_station_num][job_num+machine_ind] = schedule[chosen_station_num][chosen_job_index] - offset
        else:
          schedule[chosen_station_num][job_num+machine_ind] = schedule[chosen_station_num][chosen_job_index] + offset
  return schedule
