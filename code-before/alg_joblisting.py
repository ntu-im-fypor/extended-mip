import numpy as np

class InitSchedule:
    def __init__(self, Data) -> None:
        self.Data = Data
        self.method = 'none'
        self.compared_value = {}  # 比較、拿來排序的值
        self.scheduled_job = []  # 存取 job 順序

    def init_prod_time_sort(self) -> None:
        self.method = 'init_prod_time_sort'
        for job_id in range(1, self.Data.n_j+1):
            self.compared_value[job_id] = self.Data.INIT_PROD_TIME[1, job_id]
        self.scheduled_job = sort_value(self.compared_value, ascending=True)

    def due_sort(self) -> None:
        self.method = 'due_sort'
        self.compared_value = self.Data.DUE_TIME
        self.scheduled_job = sort_value(self.compared_value, ascending=True)
        # self.scheduled_all = np.tile(self.scheduled_job, (self.Data.n_i, 1))

    def due_weight_sort(self) -> None:
        self.method = 'dueue_weight_sort'
        for key in self.Data.DUE_TIME.keys():
            self.compared_value[key] = self.Data.DUE_TIME[key] / self.Data.WEIGHT[key]
        self.scheduled_job = sort_value(self.compared_value, ascending=True)

    def due_initprodtime_sort(self) -> None:
        self.method = 'dueue_initprodtime_sort'
        sum_initprodtime = {}
        for (i, j), value in self.Data.INIT_PROD_TIME.items():
            try:
                sum_initprodtime[j] += value
            except:
                sum_initprodtime[j] = value

        for key in self.Data.DUE_TIME.keys():
            self.compared_value[key] = self.Data.DUE_TIME[key] / sum_initprodtime[key]
        self.scheduled_job = sort_value(self.compared_value, ascending=True)

    def __getmethod__(self) -> str:
        return self.method

    def _getcomparedvalue__(self) -> dict:
        return self.compared_value


def sort_value(compared_value: dict, ascending=True):
    if ascending:
        # job_list = np.append(
        job_list = np.array([x[0] for x in sorted(compared_value.items(), key=lambda item: item[1])])
            # , 0)  # 0 or 'M' 代表保養，目前 append 0
    else:
        # job_list = np.append(
        job_list = np.array([x[0] for x in sorted(compared_value.items(), key=lambda item: -item[1])])
            # , 0)  # 0 or 'M' 代表保養，目前 append 0
    return job_list
