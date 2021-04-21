from topology import *
from distutils.dir_util import copy_tree

for i in range(10):
    copy_tree("topology/my_B4", f"topology/my_B4_{i:03d}")
    t = (read_topology(f'topology/my_B4_{i:03d}'))
    topology  = pd_to_nx(t)
    
    possible_edges = [(i,j) for i in topology.nodes for j in topology.nodes if i!=j and (i,j) not in topology.edges] # TODO: Select some of these
    possible_edges = dict(zip(possible_edges, weibull(len(possible_edges))))
    for k in possible_edges:
        topology.add_edge(*k, prob_failure=possible_edges[k], capacity=0, num_fiberducts=0)
    write_topology(nx_to_pd(topology), f'topology/my_B4_{i:03d}')
    
