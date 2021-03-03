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


def add_edges(beta, gamma, topology, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, weibull_scale, weibull_shape):
    # calculate the cost of not adding
    no_adding_cost = update_capacity(beta, gamma, topology, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost)
    cheapest = no_adding_cost
    cheapest_es = []

    # Find cheaper topology
    possible_add = [e for e in possible_edges if not e in topology.edges]
    possible_edge_probabilities = {e: weibull(1, weibull_scale, weibull_shape) for e in possible_edges}

    index_f = lambda possible_add, es: 0 if len(es) == 0 else (possible_add.index(es[-1])+1)

    topologies = [([], 0)]
    for r in range(1,len(possible_add)):

        # new_tops list of (added_edges, their_min cost), becomes then topologies
        new_tops = [(es + [add], r*fiberhut_cost) for es,cost in topologies for add in possible_add[index_f(possible_add, es):]]

        new_tops = [(sorted(i),j) for i,j in new_tops if j < cheapest]


        max_r = int(cheapest/(r*fiberhut_cost))
        print(cheapest, r*fiberhut_cost)

        #sum([link_lease_cost[e]+2*transceiver_cost for e in possible_add])

        #Consider only the ones that are cheaper
        #Update cheapest
        print(f'ITERATION {r}/{max_r}')
        for es, cost in tqdm(new_tops):
            #print(r, len(new_tops) ,new_tops.index((es,cost)))
            if cost < cheapest:
                G = topology.copy()
                for e in es:
                    G.add_edge(*e, prob_failure=possible_edge_probabilities[e], capacity=0)
                #total_cost = update_capacity(beta, gamma, G, cutoff, demand, edge_cost) + cost
                total_cost = update_capacity(beta, gamma, G, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost, added_edges=es, cheapest=cheapest)

                if total_cost < cheapest:
                    cheapest = min(total_cost, cheapest)
                    cheapest_es = es
                    max_r = int(cheapest/(r*fiberhut_cost))
                    print(cheapest,max_r)

        #filter tops out for next iteration
        new_tops = [(i,j) for i,j in new_tops if j < cheapest]
        #print(r, len(new_tops))
        topologies = new_tops

for run in range(1):
    weibull_scale = 0.001
    weibull_shape = 0.8
    
    topology_path = 'topology/B4'
    topology = pd_to_nx(read_topology(topology_path, weibull_scale, weibull_shape))
    beta = 0.999
    gamma = 1.0
    cutoff = 0.0000001
    demand = read_demand(topology_path, topology, 0)
    #demand = {k: demand[k]*0.7 for k in demand}
    n_paths = 4
    
    
    wavelength_capacity = 400 #Gbps
    n_wavelengths_fiber = 64 # number wavelengths per fiber
    gbps_cost = 10 #$ per Gbps
    transceiver_amortization_years = 3 # How long can I keep transceiver
    fiber_cost = 3600 # $ per year
    n_fibers_per_fiberhut = 200 # How many fibers are build together

    #fiber_capacity = n_wavelengths_fiber*wavelength_capacity # Capacity of fiber
    fiberhut_capacity = n_fibers_per_fiberhut * n_wavelengths_fiber * wavelength_capacity
    gbps_cost = gbps_cost / transceiver_amortization_years # Cost per Gbps per year
    fiberhut_cost = n_fibers_per_fiberhut*fiber_cost # Cost per fiber hut
    
    possible_edges = [(i,j) for i in topology.nodes for j in topology.nodes if i!=j] # TODO: Select some of these

    #################
    
    add_edges(beta, gamma, topology, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, weibull_scale, weibull_shape)
