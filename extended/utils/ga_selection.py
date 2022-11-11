import random
from schedule_objective_value_calculation import calculate_objective_value

# schedule_list: array of schedule
def ga_selection(schedule_list, instance, chosen_method) -> list:
  for schedule in schedule_list:
    print("schedule:", schedule)

  chosen_list = []
  if chosen_method == 'binary':
    chosen = random.choice(schedule_list)
    chosen_list.append(chosen)
    new_list = [i for i in schedule_list if i != chosen]
    chosen_list.append(random.choice(new_list))
  elif chosen_method == 'ranking':
    # temp_dict: {schedule, obj value}
    temp_dict = {}
    for i in schedule_list:
      obj = calculate_objective_value(i, instance)
      temp_dict[i] = obj

    # sorted_dict: [(schedule, obj value)] (large -> small)
    sorted_dict = list(reversed(sorted(temp_dict.items(), key=lambda x:x[1])))

    # ranking_dict: {schedule, chosen possibility}
    ranking_dict = {}
    index = 0
    for j in sorted_dict:
      index = index + 1
      ranking_dict[j[0]] = 2*index/(len(sorted_dict)* (len(sorted_dict)+1))

    # chosen_schedule_list
    ranking_schedule = list(ranking_dict.keys())
    ranking_possibility = tuple(ranking_dict.values())
    chosen_list = random.choices(ranking_schedule, weights=ranking_possibility, k=2)
  return chosen_list