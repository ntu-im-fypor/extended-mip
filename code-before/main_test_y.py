import model_cls as model
import model_relax_x as model_relax_x
import model_relax_y as model_relax_y
import model_relax_w as model_relax_w
# from model_cls import Data, MaintModel
import pandas as pd

factors_key = ['init_prod_time', 'prod_discount', 'weight', 'due_time', 'maint_len']

scenario_list = ['benchmark']
for key in factors_key:
    for level in ['L', 'H']:
        scenario_list.append(key + '_' + level)

def run_scen(title, model, mode='model', instance_num=10,
             run_time=1800, scenario_list=scenario_list, start_instance_num=1) -> None:

    data_path = 'code/scenario/'
    save_path='code/record/' + mode + '/'
    obj_df = pd.DataFrame(index=range(1, instance_num+1))
    runtime_df = pd.DataFrame(index=range(1, instance_num+1))
    mingap_df = pd.DataFrame(index=range(1, instance_num+1))
    bestbd_df = pd.DataFrame(index=range(1, instance_num+1))
    # sol_df = pd.DataFrame(index=range(1, instance_num+1))
    # maint_sol_df = pd.DataFrame(index=range(1, instance_num+1))

    for scenario in scenario_list:
        obj_list = []
        runtime_list = []
        # sol_list = []
        # maint_sol_list = []
        mingap_list = []
        bestbd_list = []
        for num in range(start_instance_num, start_instance_num+instance_num):
            print('='*100)
            print('='*100)
            print(scenario + '_' + str(num))
            full_path = data_path + scenario + '/' + scenario + '_' + str(num) + '.txt'
            data = model.Data()
            data.read_data(in_path=full_path)
            maint_model = model.MaintModel(data, run_time=run_time)
            maint_model.run()
            obj, runtime, mingap, bestbd = maint_model.record()
            obj_list.append(obj)
            runtime_list.append(runtime)
            mingap_list.append(mingap)
            bestbd_list.append(bestbd)
            # sol_list.append(tabu.best_sol)
            # maint_sol_list.append(tabu.best_maint_sol)
        obj_df[scenario] = obj_list
        runtime_df[scenario] = runtime_list
        mingap_df[scenario] = mingap_list
        bestbd_df[scenario] = bestbd_list
        # sol_df[scenario] = sol_list
        # maint_sol_df[scenario] = maint_sol_list

    obj_df.to_csv(save_path + title + '_obj.csv', index=False)
    runtime_df.to_csv(save_path + title + '_runtime.csv', index=False)
    mingap_df.to_csv(save_path + title + '_mingap.csv', index=False)
    bestbd_df.to_csv(save_path + title + '_bestbd.csv', index=False)
    # sol_df.to_csv(save_path + title + '_sol.csv', index=False)
    # maint_sol_df.to_csv(save_path + title + '_maint_sol.csv', index=False)


# file_title = '0221_5min'
# model = model_relax_x  # 'model'
# mode = 'model_relax_x'  # 'model'
# run_scen(file_title, model, mode=mode, instance_num=10, run_time=300, scenario_list=scenario_list)

# run_scen('0627_5min', model, mode='model', instance_num=10, run_time=300,
#           scenario_list=scenario_list, start_instance_num=6)
run_scen('0627_30min', model_relax_y, mode='model_relax_y', instance_num=30, run_time=1800,
          scenario_list=scenario_list, start_instance_num=1)
# run_scen('0627_5min_1', model_relax_y, mode='model_relax_y', instance_num=5, run_time=300,
#           scenario_list=scenario_list, start_instance_num=1)
# run_scen('0627_5min_6', model_relax_y, mode='model_relax_y', instance_num=5, run_time=300,
#           scenario_list=scenario_list, start_instance_num=6)
# run_scen('0627_5min_11', model_relax_y, mode='model_relax_y', instance_num=5, run_time=300,
#           scenario_list=scenario_list, start_instance_num=11)
# run_scen('0627_5min_16', model_relax_y, mode='model_relax_y', instance_num=5, run_time=300,
#           scenario_list=scenario_list, start_instance_num=16)
# run_scen('0516_5min', model_relax_x, mode='model_relax_x', instance_num=30, run_time=300, scenario_list=scenario_list)
# run_scen('0516_5min', model_relax_y, mode='model_relax_y', instance_num=30, run_time=300, scenario_list=scenario_list)
# run_scen('0516_5min', model_relax_w, mode='model_relax_w', instance_num=30, run_time=300, scenario_list=scenario_list)
