from topology import *
from paths import *
from scenarios import *
from parser import *
from lp import *
from util import *

from itertools import combinations

import math
import sys

import pandas as pd
import random

from tqdm import tqdm
from scipy.stats import uniform

from argparser import *

def upgrade_capacity(beta, gamma, topology, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost, added_edges=[], cheapest=None, max_capacity_update=None, max_fiberhut_update=None):
    paths = k_shortest_paths(topology, n_paths)
    scenarios = get_flow_scenarios(topology, paths) # TODO reuse scenarios, not everly flow changes i think
    cost, capacity_update, fiberhut_update = find_capacity_update(beta, gamma, topology, paths, demand, scenarios, fiberhut_capacity, gbps_cost, fiberhut_cost, added_edges=added_edges, cheapest=cheapest, max_capacity_update=max_capacity_update, max_fiberhut_update=max_fiberhut_update)
    return cost, capacity_update, fiberhut_update

def add_edges(beta, gamma, topology, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, timestep):
    def update_bars(reset = False):
        if reset: qbar.reset()
        num_combs[r] = len(new_tops)
        max_r = int(cheapest / fiberhut_cost)
        qbar.total = num_combs[r]
        pbar.total = sum(num_combs[:max_r+1])
        pbar.set_postfix({'improvement:': round(no_adding_cost/cheapest,2), 'cheapest:': int(cheapest), 'timestep': timestep})
        qbar.set_postfix({f'#edges per comb': r})
        pbar.refresh()
        qbar.refresh()

    # Calculate the cost of not adding
    cheapest, capacity_update, fiberhut_update = upgrade_capacity(beta, gamma, topology, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost)
    cheapest_capacity_update = capacity_update
    cheapest_fiberhut_update = fiberhut_update
    #print(fiberhut_update)
    no_adding_cost = cheapest
    cheapest_edges = []

    # Write result
    with open(f'{run}.txt', 'a') as f:
        f.write(f'{timestep} {cheapest} {cheapest_edges}\n')

    # Find cheaper topology
    possible_add = possible_edges.keys()

    # Show progress
    pbar = tqdm(desc='Outer Loop', file=sys.stdout, dynamic_ncols=True)
    qbar = tqdm(desc='Inner Loop', file=sys.stdout, dynamic_ncols=True)
    num_combs = [math.comb(len(possible_add), i) for i in range(0, len(possible_add)+1)]
    pbar.update(1)

    topologies = [[]]
    for r in range(1,len(possible_add)):
        # Can topology with more fiber huts even be cheaper
        if r * fiberhut_cost >= cheapest:
            break

        prev_cheapest = cheapest

        # Create topologies to check out from topologies and possible_add
        new_tops = set([frozenset(es+[add]) for es in topologies for add in possible_add if add not in es])
        # To list of lists again
        new_tops = [sorted(list(es)) for es in new_tops]

        update_bars(reset = True)

        # Tops that looked at
        succ_tops = []
        for es in new_tops:
            # Create topology
            G = topology.copy()
            for e in es:
                G.add_edge(*e, prob_failure=possible_edges[e], capacity=0, num_fiberhuts=0)

            # Upgrade capacity of new topology and append to succesful
            total_cost, capacity_update, fiberhut_update = upgrade_capacity(beta, gamma, G, n_paths, demand, fiberhut_capacity, gbps_cost, fiberhut_cost, added_edges=es, cheapest=None)
            succ_tops.append((es, total_cost))
            # Write result
            with open(f'{run}.txt', 'a') as f:
                f.write(f'{timestep} {total_cost} {es}\n')

            # Update cheapest
            if total_cost < cheapest:
                cheapest = total_cost
                cheapest_edges = es
                cheapest_capacity_update = capacity_update
                cheapest_fiberhut_update = fiberhut_update

            # update bars
            update_bars()
            qbar.update(1)
            pbar.update(1)

        # Search heuristic: sort by cost to explore promising one first # TODO more elaborate sorting once children are created
        new_tops = sorted(succ_tops, key=lambda x: x[1])
        # Space reduction heuristic: Look only at the ones that are cheaper then the cheapest from previous round TODO do cheaper than parent from previous round
        new_tops = [es for es,co  in new_tops if r*fiberhut_cost < cheapest and co < prev_cheapest] #TODO

        topologies = new_tops

    return cheapest, cheapest_edges, cheapest_capacity_update, cheapest_fiberhut_update

def backwards_iterative_upgrade(beta, gamma, topology, n_paths, demands, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, timesteps, upgrade_f):
    # solve for last
    # solve for second last with added constraints of possible edges
    # SOLVE for LAST
    # NEW MAX for previous stage for capacities and fiberhuts
    # Solve Previous stage with these max

    # copy values if using for other experiments
    G = topology.copy()
    possible_edges = {k: possible_edges[k] for k in possible_edges}

    costs = []
    total_cost = 0

    capacity_update = None
    fiberhut_update = None
    for t in reversed(range(timesteps)):

        if upgrade_f == 'add_edges':
            cost, edges, capacity_update, fiberhut_update = add_edges(beta, gamma, G, n_paths, demands[t], fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, t)
        elif upgrade_f == 'upgrade_capacity':
            cost, capacity_update, fiberhut_update = upgrade_capacity(beta, gamma, G, n_paths, demands[t], fiberhut_capacity, gbps_cost, fiberhut_cost, max_capacity_update = capacity_update, max_fiberhut_update = fiberhut_update)
            edges = []

        costs.append(cost)

        total_cost += cost

        with open('my_results.txt', 'a') as f:
            f.write(f'{upgrade_f} {total_cost} {costs}\n')
        #print('\n\nTOTAL COST AND COST\nFIND HERE\n\n',total_cost,costs)

        # TODO SET MAXIMUM FOR FIBERHUTS UPDATE
        # TODO SET MAXIMUM FOR CAPACITY UPDATE
        # modify topology for next iteration
        #for e in edges:
        #    G.add_edge(*e, prob_failure=possible_edges[e], capacity=0, num_fiberhuts=0) #FIBERHUTS FFS TODO
        #for e in topology.edges:
        #    G[e[0]][e[1]]['capacity'] += capacity_update[e]
        #    G[e[0]][e[1]]['num_fiberhuts'] += fiberhut_update[e]

        possible_edges = {e: possible_edges[e] for e in edges} #TODO THIS IS DONE BECAUSE ONLY USE THESE EDGES TO ADD
    #print('\n\nTOTAL COST AND COST\nFIND HERE\n\n',total_cost,costs)
    print(total_cost)

def iterative_upgrade(beta, gamma, topology, n_paths, demands, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, timesteps, upgrade_f):
    # copy values if using for other experiments
    G = topology.copy()
    possible_edges = {k: possible_edges[k] for k in possible_edges}

    costs = []
    total_cost = 0

    for t in range(timesteps):

        if upgrade_f == 'add_edges':
            cost, edges, capacity_update, fiberhut_update = add_edges(beta, gamma, G, n_paths, demands[t], fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, t)
        elif upgrade_f == 'upgrade_capacity':
            cost, capacity_update, fiberhut_update = upgrade_capacity(beta, gamma, G, n_paths, demands[t], fiberhut_capacity, gbps_cost, fiberhut_cost)
            edges = []

        costs.append(cost)

        total_cost += sum(costs)

        with open('my_results.txt', 'a') as f:
            f.write(f'{upgrade_f} {total_cost} {costs}\n')
        #print('\n\nTOTAL COST AND COST\nFIND HERE\n\n',total_cost,costs)

        # modify topology for next iteration
        for e in edges:
            G.add_edge(*e, prob_failure=possible_edges[e], capacity=0, num_fiberhuts=0) #FIBERHUTS FFS TODO
        for e in topology.edges:
            G[e[0]][e[1]]['capacity'] += capacity_update[e]
            G[e[0]][e[1]]['num_fiberhuts'] += fiberhut_update[e]
        possible_edges = {k: possible_edges[k] for k in possible_edges if k not in edges}
    print(total_cost)
    #print('\n\nTOTAL COST AND COST\nFIND HERE\n\n',total_cost,costs)

runs = 1
for run in range(runs):
    args = get_arguments()
    write_config_file(args)

    topology_path = 'topology/' + args.topology
    topology = pd_to_nx(read_topology(topology_path, args.weibull_scale, args.weibull_shape))
    G = topology.copy()
    gamma = 1.0

    demand = read_demand(topology_path, topology, args.demand_no)
    demands = [{k: args.demand_scale*demand[k] for k in demand}]
    for i in range(args.timesteps-1):
        demands.append({k: uniform(loc = args.demand_min_growth, scale = args.demand_max_growth-args.demand_min_growth).rvs()*demands[-1][k] for k in demands[-1]})

    fiberhut_capacity = args.n_fibers_per_fiberhut * args.n_wavelengths_fiber * args.wavelength_capacity
    gbps_cost = args.gbps_cost / args.transceiver_amortization_years
    fiberhut_cost = args.n_fibers_per_fiberhut * args.fiber_cost

    # YEARLY COST VS TOTAL COST vs WHATEVER COST
    # iterative update
    #    t = 0: topology, possible_edges, cost
    #    t = 1: top[0], possible_edges[0], cost[0]+cost[1]
    # joint update: t0 t1 t2 t3 ...
    #    ...

    

    possible_edges = [(i,j) for i in topology.nodes for j in topology.nodes if i!=j and (i,j) not in topology.edges] # TODO: Select some of these
    possible_edges = dict(zip(possible_edges, weibull(len(possible_edges), args.weibull_scale, args.weibull_shape)))

    iterative_upgrade(args.beta, gamma, topology, args.n_paths, demands, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, args.timesteps, upgrade_f = 'upgrade_capacity')
    backwards_iterative_upgrade(args.beta, gamma, topology, args.n_paths, demands, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, args.timesteps, upgrade_f = 'upgrade_capacity')
    iterative_upgrade(args.beta, gamma, topology, args.n_paths, demands, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, args.timesteps, upgrade_f = 'add_edges')
    backwards_iterative_upgrade(args.beta, gamma, topology, args.n_paths, demands, fiberhut_capacity, gbps_cost, fiberhut_cost, possible_edges, args.timesteps, upgrade_f = 'add_edges')
