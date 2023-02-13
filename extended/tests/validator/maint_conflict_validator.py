import pandas as pd

# declare global variables
NUM_OF_INSTANCES = 30
NUM_OF_STAGES = 5
JOBS_PER_INSTANCE = 20

# define a StageInfo class that has two attributes: start_time and end_time
class StageInfo:
    def __init__(self, start_time: float, end_time: float):
        self.start_time = start_time
        self.end_time = end_time

# define a job class that has two attributes: job_id and a list of StageInfo indicating start time and end time of each stage
class Job:
    def __init__(self, job_id: int):
        self.job_id = job_id
        self.stage_info = []
    def print_job_info(self, stage_id: int):
        if self.job_id == 0: # it means maintenance
            print(f"Maintenance on stage {stage_id + 1} from {self.stage_info[stage_id].start_time} to {self.stage_info[stage_id].end_time}")
        else:
            print(f"Job {self.job_id} on stage {stage_id + 1} from {self.stage_info[stage_id].start_time} to {self.stage_info[stage_id].end_time}")

# every instance is a csv file having 20 jobs and 10 stage info (stage1_start_time, stage1_end_time, stage2_start_time, stage2_end_time, etc.)
maint_instance = pd.read_csv(f"maint_time_benchmarks.csv")

for i in range(NUM_OF_INSTANCES):
    jobs = []
    # read instance csv file
    job_instance = pd.read_csv(f"job_time_benchmark_{i + 1}.csv")
    # read maintenance info
    for j in range(1, JOBS_PER_INSTANCE + 1):
        job = Job(j)
        # job_instance.iloc[j - 1, 0] is the start time of stage 1 of job j
        # job_instance.iloc[j - 1, 1] is the end time of stage 1 of job j
        for k in range(NUM_OF_STAGES):
            job.stage_info.append(StageInfo(job_instance.iloc[j - 1, k * 2 + 1], job_instance.iloc[j - 1, (k+1) * 2]))
        jobs.append(job)
    # read maintenance info
    maint_job = Job(0)
    for k in range(NUM_OF_STAGES):
        maint_job.stage_info.append(StageInfo(maint_instance.iloc[i, k * 2 + 1], maint_instance.iloc[i, (k+1) * 2]))
    # we want to check if there is any maintenance happening during the execution of a job
    for j in range(JOBS_PER_INSTANCE):
        for k in range(NUM_OF_STAGES):
            # only consider the stages that have maintenance, which means the start time and end time of the stage are not zero
            if maint_job.stage_info[k].start_time == 0 and maint_job.stage_info[k].end_time == 0:
                continue
            # determine whether the job is being exectued first or the maintenance is being executed first
            if jobs[j].stage_info[k].start_time < maint_job.stage_info[k].start_time:
                # then the conflict happens when the end time of the job is greater than the start time of the maintenance
                if jobs[j].stage_info[k].end_time > maint_job.stage_info[k].start_time:
                    print(f"Conflict happens in instance {i + 1}!")
                    maint_job.print_job_info(k)
                    jobs[j].print_job_info(k)
                    print("--------------------")
            else:
                # then the conflict happens when the end time of the maintenance is greater than the start time of the job
                if maint_job.stage_info[k].end_time > jobs[j].stage_info[k].start_time:
                    print(f"Conflict happens in instance {i + 1}!")
                    maint_job.print_job_info(k)
                    jobs[j].print_job_info(k)
                    print("--------------------")

# Path: tests\validator\maint_conflict_validator.py

