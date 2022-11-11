import random

# ex: job_possiblility-> 0.0007
def ga_mutation(schedule, job_possibility, machine_possibility, job_num, machine_num) -> list:
  # job
  if random.random() < job_possibility:
    chosen_station_num = random.randint(0,len(schedule)-1)
    schedule[chosen_station_num].reverse()

  # machine
  if random.random() < machine_possibility:
    chosen_station_num = random.randint(0,len(schedule)-1)

    # key: machine index, value: [jobs index]
    job_on_machine_dict = {}
    for machine_ind in range(machine_num):
      job_on_machine_dict[machine_ind] = []
    for job_ind in range(job_num):
      int_part = int(schedule[chosen_station_num][job_ind])
      job_on_machine_dict[int_part-1].append(job_ind)
    for machine_ind in range(machine_num):
      if len(job_on_machine_dict[machine_ind]) != 0:
        temp_value = schedule[chosen_station_num][job_num+machine_ind]
        chosen_job_index = random.choice(job_on_machine_dict[machine_ind])
        schedule[chosen_station_num][job_num+machine_ind] = schedule[chosen_station_num][chosen_job_index]
        schedule[chosen_station_num][chosen_job_index] = temp_value
  return schedule