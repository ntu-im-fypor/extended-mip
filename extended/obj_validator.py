import pandas as pd

import sys
sys.path.insert(0, '../code-before/')
import model_cls as model

# scenario_list = ['benchmark', 'init_prod_time_L', 'init_prod_time_H', 'prod_discount_L', 'prod_discount_H',
#                  'weight_L', 'weight_H', 'due_time_L', 'due_time_H', 'maint_len_L', 'maint_len_H']

scenario_list = ['benchmark']
stage_list = ['stage1_start', 'stage1_end', 'stage2_start', 'stage2_end', 'stage3_start', 'stage3_end',
              'stage4_start', 'stage4_end', 'stage5_start', 'stage5_end']
index_thirty = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
index_tewnty = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]

# Create empty dataframes to store objective results, maint_time
obj_df = pd.DataFrame(columns=scenario_list, index=index_thirty)
maint_df = pd.DataFrame(columns=stage_list, index=index_thirty)

all_sol = pd.read_csv('tests/sol-before/dueweight_greedy_noswapping_sol.csv')
all_maint_sol = pd.read_csv('tests/sol-before/dueweight_greedy_noswapping_maint_sol.csv')

# Set number of machines and number of jobs
num_machine = 5
num_job = 20

for scenario in scenario_list:
  for instance in range(30):

    # Create empty dataframe to store job schedule times
    job_df = pd.DataFrame(columns=stage_list, index=index_tewnty)

    # Instance data from `scenario` folder
    data = model.Data()
    data.read_data(in_path='../code-before/experiment/scenario/' + scenario + '/' + scenario + '_' + str(instance + 1) + '.txt')

    # Get sol and maint_sol for this instance
    sol = all_sol[scenario][instance][1:-1].replace('.', '').split()
    maint_sol = all_maint_sol[scenario][instance][1:-1].replace('.', '').split()
    for i in range(num_job):
      sol[i] = int(sol[i])
    for i in range(num_machine):
      maint_sol[i] = int(maint_sol[i])
    
    # Array to store the current end time of each job, will update after looping each machine
    current_end_time = [0] * num_job

    # Array to store the start time and end time of each maintenance
    maint_time = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

    # Initial time calculation (not considering maintenance conflict)
    for i in range(num_machine): # loop all machines in order
      current_machine_time = 0
      current_machine_time += data.REMAIN[i + 1]

      for j in range(num_job): # loop all jobs in order
        if (maint_sol[i] == j): # record start and end time of maintenance
          maint_time[i][0] = current_machine_time
          current_machine_time += data.MAINT_LEN[i + 1]
          maint_time[i][1] = current_machine_time
        
        production_time = data.INIT_PROD_TIME[(i + 1, sol[j])] # initial production time
        if (maint_sol[i] <= j): # update production time if the job is after maintenance
          production_time *= data.PROD_DISCOUNT[i + 1]
        
        production_start_time = max(current_machine_time, current_end_time[sol[j] - 1])
        current_end_time[sol[j] - 1] = production_start_time + production_time
        current_machine_time = production_start_time + production_time

    # Check maintenance conflict
    maint_check = [False, False, False, False, False]
    maint_end_time = 0
    for i in range(num_machine):
      first_false = False
      for j in range(num_machine):
        if (maint_check[j] == False and first_false == False):
          min_start = maint_time[j][0]
          min_finish = maint_time[j][1]
          min_index = j
          first_false = True
        if (maint_check[j] == False and maint_time[j][0] < min_start):
          min_start = maint_time[j][0]
          min_finish = maint_time[j][1]
          min_index = j
      maint_check[min_index] = True
      if (min_start < maint_end_time):
        maint_time[min_index][0] = maint_end_time
        maint_time[min_index][1] = maint_end_time + data.MAINT_LEN[min_index + 1]
      maint_end_time = maint_time[min_index][1]
    
    print("instance", instance+1)
    print("maint_time for each stage", maint_time)
    for i in range(5):
      maint_df[stage_list[2*i]][instance+1] = maint_time[i][0]
      maint_df[stage_list[2*i+1]][instance+1] = maint_time[i][1]

    # Reset [Array to store the current end time of each job, will update after looping each machine] for re-calculation
    current_end_time = [0] * num_job

    # Time re-calculation to eliminate maintenance conflict
    for i in range(num_machine): # loop all machines in order
      current_machine_time = 0
      current_machine_time += data.REMAIN[i + 1]

      print("stage", i+1)

      for j in range(num_job): # loop all jobs in order
        if (maint_sol[i] == j):
          current_machine_time = maint_time[i][1]
        
        production_time = data.INIT_PROD_TIME[(i + 1, sol[j])]
        if (maint_sol[i] <= j): # the job is after maintenance
          production_time *= data.PROD_DISCOUNT[i + 1]
        
        production_start_time = max(current_machine_time, current_end_time[sol[j] - 1])
        current_end_time[sol[j] - 1] = production_start_time + production_time
        current_machine_time = production_start_time + production_time

        print("job", sol[j], production_start_time, production_start_time+production_time)
        job_df[stage_list[2*i]][sol[j]] = production_start_time
        job_df[stage_list[2*i+1]][sol[j]] = production_start_time+production_time

    job_df.to_csv('tests/validator/job_time_benchmark_' + str(instance+1) + '.csv')

    obj = 0
    for i in range(num_job):
      if (current_end_time[i] > data.DUE_TIME[i + 1]): # finished after due time
        obj += (current_end_time[i] - data.DUE_TIME[i + 1]) * data.WEIGHT[i + 1]

    obj_df[scenario][instance+1] = obj

    print("obj", obj)

obj_df.to_csv('tests/validator/validator_obj.csv')
maint_df.to_csv('tests/validator/maint_time_benchmarks.csv')