from utils.ours_utils import transform_our_param_to_before
from Models import Parameters

if __name__ == '__main__':
    parameters = Parameters()
    for i in range(1, 31):
        parameters.read_parameters(f"extended/tests/single_machine/queue_time_H/queue_time_H_{i}.txt")
        transform_our_param_to_before(
            params=parameters,
            folder_to_save="transformed_params/single_machine/queue_time_H",
            scenario_name="queue_time_H",
            instance_id=i
        )