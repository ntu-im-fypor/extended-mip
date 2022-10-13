import pandas as pd

date = '0211_30min'
path = 'code/' # record/'
filename_obj = path + date + '_obj.csv'
filename_time = path + date + '_runtime.csv'


factors_key = ['init_prod_time', 'prod_discount', 'weight', 'due_time', 'maint_len']

scenario_list = ['benchmark']
for key in factors_key:
    for level in ['L', 'H']:
        scenario_list.append(key + '_' + level)


f_obj = open(filename_obj, 'w+')
f_time = open(filename_time, 'w+')

i = 1
for scenario in scenario_list:
    f_obj.write(f'{scenario}')
    f_time.write(f'{scenario}')
    for num in range(10):
        f_obj.write(f', {i+num}')
        f_time.write(f', {i+num+10}')
        f_obj.close()
        f_time.close()
        f_obj = open(filename_obj, 'a+')
        f_time = open(filename_time, 'a+')
    f_obj.write('\n')
    f_time.write('\n')
    i += 1
f_obj.close()
f_time.close()

df = pd.read_csv(filename_obj, index_col='benchmark').T
df.to_csv(filename_obj)
print(df)


