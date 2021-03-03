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

def update_capacity(beta, gamma, topology, n_paths, demand, link_lease_cost, transceiver_cost, n_wavelengths_fiber, wavelength_capacity, added_edges=[], cheapest=None):

    paths = k_shortest_paths(topology, n_paths)
    scenarios = get_flow_scenarios(topology, paths) # TODO reuse scenarios, not everly flow changes i think

    cost = find_capacity_update(beta, gamma, topology, paths, demand, scenarios, link_lease_cost, transceiver_cost, n_wavelengths_fiber, wavelength_capacity, added_edges=added_edges, cheapest=None)

    return cost



def add_edges(run, beta, gamma, topology, n_paths, demand, link_lease_cost, transceiver_cost, n_wavelengths_fiber, wavelength_capacity, possible_edges, weibull_scale, weibull_shape):
    # calculate the cost of not adding
    no_adding_cost = update_capacity(beta, gamma, topology, n_paths, demand, link_lease_cost, transceiver_cost, n_wavelengths_fiber, wavelength_capacity)
    cheapest = no_adding_cost
    cheapest_es = []

    with open(f'{run}.txt', 'a+') as my_run:
        my_run.write(f'0 {cheapest} {cheapest_es}\n')


    # Find cheaper topology
    possible_add = [e for e in possible_edges if not e in topology.edges]
    possible_edge_probabilities = {e: weibull(1, weibull_scale, weibull_shape) for e in possible_edges}

    index_f = lambda possible_add, es: 0 if len(es) == 0 else (possible_add.index(es[-1])+1)

    topologies = [([], 0)]
    for r in range(1,len(possible_add)):

        # new_tops list of (added_edges, their_min cost), becomes then topologies
        new_tops = [(es + [add], cost+link_lease_cost[add]+2*transceiver_cost) for es,cost in topologies for add in possible_add[index_f(possible_add, es):]]

        new_tops = [(sorted(i),j) for i,j in new_tops if j < cheapest]


        max_r = int(cheapest/(3600+2*transceiver_cost))
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
                total_cost = update_capacity(beta, gamma, G, n_paths, demand, link_lease_cost, transceiver_cost, n_wavelengths_fiber, wavelength_capacity, added_edges=es, cheapest = None)

                if total_cost < cheapest:
                    cheapest = min(total_cost, cheapest)
                    cheapest_es = es
                    print(cheapest)

        with open(f'{run}.txt', 'a+') as my_run:
            my_run.write(f'{r} {cheapest} {cheapest_es}\n')

        #filter tops out for next iteration
        new_tops = [(i,j) for i,j in new_tops if j < cheapest]
        #print(r, len(new_tops))
        topologies = new_tops

for run in range(1):
    weibull_scale = 0.001
    weibull_shape = 0.8
    
    topology_path = 'topology/B4'
    topology = pd_to_nx(read_topology(topology_path, weibull_scale, weibull_shape))
    beta = 0.9999
    gamma = 1.0
    cutoff = 0.0000001
    demand = read_demand(topology_path, topology, 0)
    n_paths = 4
    
    
    wavelength_capacity = 400 #Gbps
    
    transceiver_gbps_cost = 10 #$ per Gbps
    transceiver_amortization_years = 3 # How long can I keep transceiver
    transceiver_cost = wavelength_capacity*transceiver_gbps_cost/transceiver_amortization_years #ammortized $ per transceiver per year
    
    fiber_lease_cost = 3600 # $ per year
    n_wavelengths_fiber = 40 # number wavelengths per fiber
    
    possible_edges = [(i,j) for i in topology.nodes for j in topology.nodes if i!=j] # TODO read out from fiber map
    n_fibers_link = [1 for e in possible_edges] # TODO For each potential edge: number of fibers between nodes (one link may consist of 3 fibers)
    
    
    link_lease_cost = [fiber_lease_cost*i for i in n_fibers_link]
    link_lease_cost = dict(zip(possible_edges, link_lease_cost))
    
    ################
    
    add_edges(run, beta, gamma, topology, n_paths, demand, link_lease_cost, transceiver_cost, n_wavelengths_fiber, wavelength_capacity, possible_edges, weibull_scale, weibull_shape)
