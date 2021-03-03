import numpy as np
import os

def read_demand(topology_path, topology, demand_no):
    nodes = sorted(topology.nodes)
    flows = [(i,j) for i in nodes for j in nodes]
    demand = np.loadtxt(os.path.join(topology_path, 'demand/demand_{:03d}.demand'.format(demand_no)))
    demands = list(demand.flatten())
    demands = [(i,j) for i,j in zip(flows, demands) if i[0] != i[1]]
    return dict(demands)
