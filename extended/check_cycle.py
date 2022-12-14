import sys
from tokenize import String
from unittest import result
from Models import Parameters
from Models.Gurobi import CompleteMIPModel, CompleteMIPModel_original
from Models.heuristic import MetaPSOModel
import pandas as pd
import numpy as np
import os
from collections import defaultdict
 
### copied from https://www.geeksforgeeks.org/detect-cycle-in-a-graph/
### topological sort from https://www.geeksforgeeks.org/topological-sorting/
class Graph():
    def __init__(self,vertices):
        self.graph = defaultdict(list)
        self.V = vertices
 
    def addEdge(self,u,v):
        self.graph[u].append(v)
 
    def isCyclicUtil(self, v, visited, recStack):
 
        # Mark current node as visited and
        # adds to recursion stack
        visited[v] = True
        recStack[v] = True
 
        # Recur for all neighbours
        # if any neighbour is visited and in
        # recStack then graph is cyclic
        for neighbour in self.graph[v]:
            if visited[neighbour] == False:
                if self.isCyclicUtil(neighbour, visited, recStack) == True:
                    return True
            elif recStack[neighbour] == True:
                return True
 
        # The node needs to be popped from
        # recursion stack before function ends
        recStack[v] = False
        return False
 
    # Returns true if graph is cyclic else false
    def isCyclic(self):
        visited = [False] * (self.V + 1)
        recStack = [False] * (self.V + 1)
        for node in range(self.V):
            if visited[node] == False:
                if self.isCyclicUtil(node,visited,recStack) == True:
                    return True
        return False

    # A recursive function used by topologicalSort
    def topologicalSortUtil(self, v, visited, stack):
 
        # Mark the current node as visited.
        visited[v] = True
 
        # Recur for all the vertices adjacent to this vertex
        for i in self.graph[v]:
            if visited[i] == False:
                self.topologicalSortUtil(i, visited, stack)
 
        # Push current vertex to stack which stores result
        stack.append(v)
 
    # The function to do Topological Sort. It uses recursive
    # topologicalSortUtil()
    def topologicalSort(self):
        # Mark all the vertices as not visited
        visited = [False]*self.V
        stack = []
 
        # Call the recursive helper function to store Topological
        # Sort starting from all vertices one by one
        for i in range(self.V):
            if visited[i] == False:
                self.topologicalSortUtil(i, visited, stack)
 
        # Print contents of the stack
        # print(stack[::-1])  # return list in reverse order
        return stack[::-1]
    
class ResultParameters:
    def __init__(self) -> None:
        self.objVal = 0 # objective value
        self.shared_job_order = None # shared job order
        self.job_maintenance_order = [] # job and maintenance order on each machine

    def read_result(self, instance_file_path, result_file_path) -> None:
        parameters = Parameters() # read parameters
        parameters.read_parameters(instance_file_path)

        self.MACHINES_NUM_FLATTEN = sum(parameters.Number_of_Machines)
        self.JOBS_NUM = parameters.Number_of_Jobs
        self.STAGES_NUM = parameters.Number_of_Stages
        self.MACHINES_NUM = parameters.Number_of_Machines

        self.rmj = np.zeros((self.MACHINES_NUM_FLATTEN, self.JOBS_NUM)) # whether job j completed on machine m
        self.zij = np.zeros((self.STAGES_NUM, self.JOBS_NUM)) # whether job j's completion time in stage i
        self.vim = np.zeros((self.STAGES_NUM, max(self.MACHINES_NUM))) # whether maintenance is completed on machine m in stage i
        self.bim = np.zeros((self.STAGES_NUM, max(self.MACHINES_NUM))) # maintenance completion time of machine m in stage i
        self.order = [] # job order on each machine
        self.adj_matrix = np.zeros((self.JOBS_NUM, self.JOBS_NUM)) # adjacency matrix for job precedence
    
        with open(result_file_path, 'r') as f:
            [self.objVal] = map(float, f.readline().split())
            for m in range(self.MACHINES_NUM_FLATTEN):
                row = list(map(int,map(float, f.readline().split())))
                for j in range(self.JOBS_NUM):
                    self.rmj[m][j] = row[j]
            for i in range(self.STAGES_NUM):
                row = list(map(float, f.readline().split()))
                for j in range(self.JOBS_NUM):
                    self.zij[i][j] = row[j]
            for i in range(self.STAGES_NUM):
                row = list(map(float, f.readline().split()))
                for m in range(self.MACHINES_NUM[i]):
                    self.vim[i][m] = row[m]
            for i in range(self.STAGES_NUM):
                row = list(map(float, f.readline().split()))
                for m in range(self.MACHINES_NUM[i]):
                    self.bim[i][m] = row[m]
  
    # generate order on machines of jobs only
    def generateOrder(self) -> None:
        machine = 0
        for i in range(self.STAGES_NUM):
            for m in range(self.MACHINES_NUM[i]):
                maint_job_list = []
                indexes = np.where(self.rmj[machine] == 1) # filter jobs completed on this machine in this stage
                completion_time = self.zij[i][indexes] # retrieve their completion times
                index_completion_time_list = list(zip(np.array(indexes).flatten(), completion_time))
                if(self.vim[i][m] == 1): # if maintenance is completed on stage i of machine m
                    index_completion_time_list.append((-1, self.bim[i][m])) # zip to (index, completion time) list and append maintenance time
                sorted_index_completion_time_list = sorted(index_completion_time_list, key=lambda x: x[1]) # sort according to completion time
                for k in range(len(sorted_index_completion_time_list)):
                    if sorted_index_completion_time_list[k][0] != -1: # is a job
                        maint_job_list.append(sorted_index_completion_time_list[k][0] + 1)
                self.order.append(maint_job_list)
                machine+=1
    
    # generate order on machines of jobs and maintenance
    def generateJobMaintenanceOrder(self) -> None:
        machine = 0
        for i in range(self.STAGES_NUM):
            for m in range(self.MACHINES_NUM[i]):
                maint_job_list = []
                indexes = np.where(self.rmj[machine] == 1) # filter jobs completed on this machine in this stage
                completion_time = self.zij[i][indexes] # retrieve their completion times
                index_completion_time_list = list(zip(np.array(indexes).flatten(), completion_time))
                if(self.vim[i][m] == 1): # if maintenance is completed on stage i of machine m
                    index_completion_time_list.append((-1, self.bim[i][m])) # zip to (index, completion time) list and append maintenance time
                sorted_index_completion_time_list = sorted(index_completion_time_list, key=lambda x: x[1]) # sort according to completion time
                for k in range(len(sorted_index_completion_time_list)):
                    if sorted_index_completion_time_list[k][0] != -1: # is a job
                        maint_job_list.append(sorted_index_completion_time_list[k][0] + 1)
                    else: # is maintenance
                         maint_job_list.append('M')
                self.job_maintenance_order.append(maint_job_list)
                machine+=1
    
    def create_adj_matrix(self) -> None:
        for i in range(len(self.order)):
            for j in range(len(self.order[i])-1):
                self.adj_matrix[self.order[i][j]-1][self.order[i][j+1]-1] = 1
        
    # generate shared job order, return 
    def generateSharedJobOrder(self) -> bool:
        self.generateOrder()
        self.create_adj_matrix()
        g = Graph(self.JOBS_NUM)
        for i in range(len(self.adj_matrix)):
            for j in range(len(self.adj_matrix[i])):
                if self.adj_matrix[i][j] == 1:
                    g.addEdge(i, j)
        if g.isCyclic() == 1:
            # print("Graph contains cycle")
            return False, None
        else:
            # print("Graph doesn't contain cycle")
            job_order = g.topologicalSort()
            job_order = [i+1 for i in job_order] # the job index start from 1
            self.shared_job_order = job_order
            return True, job_order
        


def look_for_topological_order(file_id):
    # if len(sys.argv) == 0:
    #     print("No parameters file specified")
    #     return
    # file_id = sys.argv[1]
    parameters = Parameters()
    parameters.read_parameters('tests/base/base_'+ str(file_id) +'.txt')

    # generate a schedule from the base results
    resultParameters = ResultParameters()
    resultParameters.read_result('tests/base/base_'+ str(file_id) +'.txt','tests/base_result_1107/base_result_'+ str(file_id) +'.txt')
    has_shared_job_order, job_order = resultParameters.generateSharedJobOrder()
    return has_shared_job_order, job_order

    



if __name__ == '__main__':
    # look_for_topological_order()
    
    data = [['Job Order Exists', 'Shared Job order']]
    for i in range(1, 51):
        total_order_exists, order = look_for_topological_order(i)
        data.append([total_order_exists, order])
    df = pd.DataFrame(data)
    df.to_csv('./tests/1123_exists_total_order.csv')
