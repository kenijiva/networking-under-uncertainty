import numpy as np
import os

def read_demand(topology_path, topology, demand_no):
    nodes = sorted(topology.nodes)
    flows = [(i,j) for i in nodes for j in nodes]
    files = sorted((os.listdir(f'{topology_path}/demand/{demand_no:03d}')))

    demands = []
    for f in files:
        demand = np.loadtxt((f'{topology_path}/demand/{demand_no:03d}/{f}'))
        demand = list(demand.flatten())
        demand = dict([(i,j) for i,j in zip(flows, demand) if i[0] != i[1]])
        demands.append(demand)
    return demands
