import random
from schedule_objective_value_calculation import calculate_objective_value

# schedule_instance_dict: {schedule: instance}


def ga_selection(schedule_instance_dict, chosen_method) -> dict:
    for schedule in schedule_instance_dict:
        print("schedule:", schedule, ", instance:",
              schedule_instance_dict[schedule])
    schedule_list = list(schedule_instance_dict.keys())

    chosen_dict = {}
    if chosen_method == 'binary':
        while len(chosen_dict) < 2:
            chosen = random.choice(schedule_list)
            chosen_dict[chosen] = schedule_instance_dict[chosen]
    elif chosen_method == 'ranking':
        # temp_dict: {schedule, obj value}
        temp_dict = {}
        for i in schedule_list:
            obj = calculate_objective_value(i, schedule_instance_dict(i))
            temp_dict[i] = obj

        # sorted_dict: [(schedule, obj value)] (large -> small)
        sorted_dict = list(
            reversed(sorted(temp_dict.items(), key=lambda x: x[1])))

        # ranking_dict: {schedule, chosen possibility}
        ranking_dict = {}
        index = 0
        for j in sorted_dict:
            index = index + 1
            ranking_dict[j[0]] = 2*index / \
                (len(sorted_dict) * (len(sorted_dict)+1))

        # chosen_schedule_list
        ranking_schedule = list(ranking_dict.keys())
        ranking_possibility = tuple(ranking_dict.values())
        chosen_schedule_list = random.choices(
            ranking_schedule, weights=ranking_possibility, k=2)
        for k in chosen_schedule_list:
            chosen_dict[k] = schedule_instance_dict[k]
    return chosen_dict
