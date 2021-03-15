from topology import *
from paths import *
from scenarios import *
from parser import *
from lp import *
from util import *

from itertools import combinations

import math

import pandas as pd
import random

from tqdm import tqdm

def update_capacity(beta, gamma, topology, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost, added_edges=[], cheapest=None):

    paths = k_shortest_paths(topology, n_paths)
    scenarios = get_flow_scenarios(topology, paths) # TODO reuse scenarios, not everly flow changes i think

    cost = find_capacity_update(beta, gamma, topology, paths, demand, scenarios, fiberhut_capacity, gbps_cost, fiberhut_cost, added_edges=added_edges, cheapest=cheapest)
    return cost


def add_edges(beta, gamma, topology, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges):
    # calculate the cost of not adding
    no_adding_cost = update_capacity(beta, gamma, topology, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost)
    cheapest = no_adding_cost
    cheapest_es = []

    # Find cheaper topology
    possible_add = possible_edges.keys()

    index_f = lambda possible_add, es: 0 if len(es) == 0 else (possible_add.index(es[-1])+1)

    topologies = [[]]

    # at most max_r iterations
    # per r at most combinations_r children
    import sys
    num_combs = [math.comb(len(possible_add), i) for i in range(0, len(possible_add)+1)]

    pbar = tqdm(desc='Outer Loop', file=sys.stdout, dynamic_ncols=True)
    qbar = tqdm(desc='Inner Loop', file=sys.stdout, dynamic_ncols=True)
    pbar.update(1)
    with open(f'{run}.txt', 'a') as f:
        f.write(f'{ds} {cheapest} 0 {[]}\n')
    for r in range(1,len(possible_add)):
        prev_cheapest = cheapest
        new_tops = set([frozenset(es+[add]) for es in topologies for add in possible_add if add not in es])
        new_tops = [sorted(list(es)) for es in new_tops if r*fiberhut_cost < cheapest]

        new_tops = [sorted(list(es)) for es in new_tops if r*fiberhut_cost < prev_cheapest] # TODO

        num_combs[r] = len(new_tops)
        qbar.reset()
        max_r = int(cheapest/fiberhut_cost)
        pbar.total = sum(num_combs[:max_r+1])
        qbar.total = num_combs[r]

        if cheapest != 0:
            pbar.set_postfix({'improvement:': round(no_adding_cost/cheapest,2), 'cheapest:': int(cheapest)})
            qbar.set_postfix({f'#edges per comb': r})
        pbar.refresh()
        qbar.refresh()

        #for es, cost in tqdm(new_tops, file=sys.stdout, desc = 'Inner Loop', dynamic_ncols=True):
        my_tops = []
        for es in new_tops:
            if r*fiberhut_cost < cheapest:
                G = topology.copy()
                for e in es:
                    G.add_edge(*e, prob_failure=possible_edges[e], capacity=0, num_fiberhuts=0)
                #total_cost = update_capacity(beta, gamma, G, cutoff, demand, edge_cost) + cost
                #total_cost = update_capacity(beta, gamma, G, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost, added_edges=es, cheapest=cheapest)
                total_cost = update_capacity(beta, gamma, G, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost, added_edges=es, cheapest=None)
                with open(f'{run}.txt', 'a') as f:
                    f.write(f'{ds} {total_cost} {r} {es}\n')

                my_tops.append((es, total_cost))

                if total_cost < cheapest:
                    cheapest = min(total_cost, cheapest)
                    cheapest_es = es

                    max_r = int(cheapest/fiberhut_cost)
                    pbar.total = sum(num_combs[:max_r+1])
                    pbar.set_postfix({'improvement:': round(no_adding_cost/cheapest,2), 'cheapest:': int(cheapest)})

                pbar.update(1)
                qbar.update(1)
            else:
                pbar.total = pbar.total - 1
                qbar.total = qbar.total - 1

            pbar.refresh()
            qbar.refresh()

        #filter tops out for next iteration
        new_tops = sorted(my_tops, key=lambda x: x[1])
        new_tops = [es for es,co  in new_tops if r*fiberhut_cost < cheapest and co < prev_cheapest] #TODO
        topologies = new_tops


runs = 1
for run in range(runs):
    weibull_scale = 0.001
    weibull_shape = 0.8
    
    topology_path = 'topology/my_B4'
    topology = pd_to_nx(read_topology(topology_path, weibull_scale, weibull_shape))
    beta = 0.999
    gamma = 1.0
    cutoff = 0.0000001
    demand = read_demand(topology_path, topology, 0)

    n_paths = 4
    
    wavelength_capacity = 400 #Gbps
    n_wavelengths_fiber = 64 # number wavelengths per fiber
    gbps_cost = 10 #$ per Gbps
    transceiver_amortization_years = 3 # How long can I keep transceiver
    fiber_cost = 3600 # $ per year
    n_fibers_per_fiberhut = 200 # How many fibers are build together

    fiberhut_capacity = n_fibers_per_fiberhut * n_wavelengths_fiber * wavelength_capacity
    gbps_cost = gbps_cost / transceiver_amortization_years # Cost per Gbps per year
    fiberhut_cost = n_fibers_per_fiberhut*fiber_cost # Cost per fiber hut
    
    possible_edges = [(i,j) for i in topology.nodes for j in topology.nodes if i!=j and (i,j) not in topology.edges] # TODO: Select some of these
    possible_edges = dict(zip(possible_edges, weibull(len(possible_edges), weibull_scale, weibull_shape)))

    demand_scales = [0.5,.55, 0.6,0.7,1,2.0]

    for ds in demand_scales:
        demand_scaled = {k: demand[k]*ds for k in demand}
        add_edges(beta, gamma, topology, n_paths, demand_scaled, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges)
