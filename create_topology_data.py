import os
import numpy as np
from distutils.dir_util import copy_tree
from scipy.stats import uniform
from parser import *

def weibull(n_sample,scale=0.001, shape=0.8):
    return scale * np.random.weibull(a=shape, size=n_sample)


def derive_topologies(top):
    n_tops = len([d for d in os.listdir(f'topology/') if top in d])
    for i in range(10):
        copy_tree(f"topology/base_topology/{top}", f"topology/{top}_{(i+n_tops):03d}")
        t = read_topology(f'topology/{top}_{(i+n_tops):03d}')
        topology  = pd_to_nx(t)
        for e in topology.edges:
            topology[e[0]][e[1]]['prob_failure'] = weibull(1)[0]
            topology[e[0]][e[1]]['capacity'] *= 0.5
            topology[e[0]][e[1]]['num_fiberducts'] = 1
    
        possible_edges = [(i,j) for i in topology.nodes for j in topology.nodes if i!=j and (i,j) not in topology.edges]
        possible_edges = dict(zip(possible_edges, weibull(len(possible_edges))))
        for k in possible_edges:
            topology.add_edge(*k, prob_failure=possible_edges[k], capacity=0, num_fiberducts=0)
        write_topology(nx_to_pd(topology), f'topology/{top}_{(i+n_tops):03d}')

        k = 0
        for demand in sorted(os.listdir(f'topology/{top}_{(i+n_tops):03d}/demand'))[0:10]:
            os.mkdir(f'topology/{top}_{(i+n_tops):03d}/demand/{k:03d}')
            for j in range(10):
                d = np.loadtxt(f'topology/{top}_{(i+n_tops):03d}/demand/demand_{demand[7:10]}.demand')
                ds = [d]
            for h in range(9):
                scaler = uniform(loc = 1.0, scale = 1.0).rvs(d.shape)
                d = scaler*d
                ds.append(d)
            for h, d in enumerate(ds):
                np.savetxt(f'topology/{top}_{(i+n_tops):03d}/demand/{k:03d}/{h:03d}.demand', d)
            k += 1
        for f in os.listdir(f'topology/{top}_{(i+n_tops):03d}/demand/'):
            if 'demand' in f:
                os.remove(f"topology/{top}_{(i+n_tops):03d}/demand/{f}")

tops = os.listdir('topology/base_topology/')
tops = [top for top in tops if 'B4' not in top]
for top in tops:
    derive_topologies(top)
