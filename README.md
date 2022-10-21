# extended-mip
A Joint Production and Preventive Maintenance Scheduling Problem in a Multi-stage Flexible Flow Shop Environment

## How to Run Gurobi
1. clone this repo
2. go to the repo directory and `cd` to extended folder
3. install required packages by typing `pip install -r requirements.txt`
4. Make sure you have a valid Gurobi license in your computer. If don't, please refer to the link to apply for an individual academic license: https://www.gurobi.com/academia/academic-program-and-licenses/.
5. run the Gurobi Model by typing `python main.py -tests/origianl_test.txt`


## About accessing Gurobi variable and Parameters for plotting result
You can define the plotting result function in the function `plot_result()` in `extended/Models/complete_mip_gurobi.py`. And to access the value of every variable and parameters, you can refer to the comment in the function:
```python
def plot_result(self) -> None:
        """
        1. you can access every variable by passing its index
        e.g. you can access completion time of job 1 in stage 1 using self.z_ij[1, 1].x (Note: z_ij[1, 1] is a gurobi variable, but its value needs to be accessed by .x)
        2. you can access every parameter by using the property self.parameters
        e.g. you can access the due time of job 1 using self.parameters.Due_Time[0]

        What should be noticed is that the index of every parameter starts from 0, while the index of every variable starts from 1
        """
        print("Plotting...")
        # use following method, you can get the value of completion time of job 1 in stage 1 and due time of job 1
        print(f"z_11: {self.z_ij[1, 1].x}")
        print(f"due time of job 1: {self.parameters.Due_Time[0]}")
```
