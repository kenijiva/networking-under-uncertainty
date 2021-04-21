from topology import *
from paths import *
from scenarios import *
from parser import *
from lp import *
from util import *

from itertools import combinations

import math
import sys
import os

import pandas as pd
import random

from tqdm import tqdm
from scipy.stats import uniform

from argparser import *

def upgrade_capacity(alpha, topology, n_paths, demand, fiberduct_capacity, gbps_cost, fiberduct_cost, path_selection, cutoff, added_edges=[], cheapest=None, max_capacity_update=None, max_fiberduct_update=None):
    if path_selection == 'KSP':
        paths = KSP(topology, n_paths)
    elif path_selection == 'PST':
        paths = PST(topology, n_paths)
        #alpha = 0.999

    #print('get scenarios')
    scenarios = get_flow_scenarios(topology, paths, cutoff) # TODO reuse scenarios, not everly flow changes i think # TODO no need to actually do for all paths: (1,2) == (2,1)
    #print(min([sum(sorted([p for _,p in scenarios[l][1]])) for l in range(len(scenarios))]))
    #print('calc sol')
    #print(alpha)
    cost, capacity_update, fiberduct_update = find_capacity_update(alpha, topology, paths, demand, scenarios, fiberduct_capacity, gbps_cost, fiberduct_cost, added_edges=added_edges, cheapest=cheapest, max_capacity_update=max_capacity_update, max_fiberduct_update=max_fiberduct_update)

    return cost, capacity_update, fiberduct_update

def add_edges(alpha, topology, n_paths, demand, fiberduct_capacity, gbps_cost, fiberduct_cost, possible_edges, timestep, path_selection, experiment_path, doc_str, cutoff):
    def update_bars(reset = False):
        if reset: qbar.reset()
        num_combs[r] = len(new_tops)
        if cheapest == float("inf"):
            max_r = len(possible_edges)
        else:
            max_r = int(cheapest / fiberduct_cost)
        qbar.total = num_combs[r]
        pbar.total = sum(num_combs[:max_r+1])
        pbar.set_postfix({'improvement:': round(no_adding_cost/cheapest,2), 'cheapest:': int(cheapest) if cheapest != float('inf') else float('inf'), 'timestep': timestep})
        qbar.set_postfix({f'#edges per comb': r})
        pbar.refresh()
        qbar.refresh()

    # Calculate the cost of not adding
    cheapest, capacity_update, fiberduct_update = upgrade_capacity(alpha, topology, n_paths, demand, fiberduct_capacity, gbps_cost, fiberduct_cost, path_selection, cutoff)
    cheapest_capacity_update = capacity_update
    cheapest_fiberduct_update = fiberduct_update
    #print(fiberduct_update)
    no_adding_cost = cheapest
    cheapest_edges = []

    # Write result
    with open(os.path.join(experiment_path, 'topology_evaluations.txt'), 'a') as f:
        f.write(f'{doc_str} {cheapest} {cheapest_edges}\n')

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
        if r * fiberduct_cost >= cheapest:
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
                G.add_edge(*e, prob_failure=possible_edges[e], capacity=0, num_fiberducts=0)
                G.add_edge(*(e[1],e[0]), prob_failure=possible_edges[e], capacity=0, num_fiberducts=0)

            # Upgrade capacity of new topology and append to succesful
            total_cost, capacity_update, fiberduct_update = upgrade_capacity(alpha, G, n_paths, demand, fiberduct_capacity, gbps_cost, fiberduct_cost, path_selection, cutoff, added_edges=es, cheapest=None)
            succ_tops.append((es, total_cost))
            # Write result
            with open(os.path.join(experiment_path, 'topology_evaluations.txt'), 'a') as f:
                f.write(f'{doc_str} {total_cost} {es}\n')

            # Update cheapest
            if total_cost < cheapest:
                cheapest = total_cost
                cheapest_edges = es
                cheapest_capacity_update = capacity_update
                cheapest_fiberduct_update = fiberduct_update

            # update bars
            update_bars()
            qbar.update(1)
            pbar.update(1)

        # Search heuristic: sort by cost to explore promising one first # TODO more elaborate sorting once children are created
        new_tops = sorted(succ_tops, key=lambda x: x[1])
        # Space reduction heuristic: Look only at the ones that are cheaper then the cheapest from previous round TODO do cheaper than parent from previous round
        new_tops = [es for es,co  in new_tops if r*fiberduct_cost < cheapest and co < prev_cheapest] #TODO

        topologies = new_tops

    return cheapest, cheapest_edges, cheapest_capacity_update, cheapest_fiberduct_update

def backwards_iterative_upgrade(alpha, topology, n_paths, demands, fiberduct_capacity, gbps_cost, fiberduct_cost, possible_edges, timesteps, upgrade_f, path_selection, experiment_path, cutoff):
    doc_str = f'backward {upgrade_f} {path_selection}-{n_paths}'
    # copy values if using for other experiments
    G = topology.copy()
    possible_edges = {k: possible_edges[k] for k in possible_edges}

    costs = []
    total_cost = 0

    capacity_update = None
    fiberduct_update = None
    for t in reversed(range(timesteps)):

        if upgrade_f == 'add_edges':
            cost, edges, capacity_update, fiberduct_update = add_edges(alpha, G, n_paths, demands[t], fiberduct_capacity, gbps_cost, fiberduct_cost, possible_edges, t, path_selection, experiment_path, f'{doc_str} {t}', cutoff)
        elif upgrade_f == 'upgrade_capacity':
            cost, capacity_update, fiberduct_update = upgrade_capacity(alpha,  G, n_paths, demands[t], fiberduct_capacity, gbps_cost, fiberduct_cost, path_selection, cutoff, max_capacity_update = capacity_update, max_fiberduct_update = fiberduct_update)
            edges = []

        costs.append(cost)

        total_cost += cost

        with open(os.path.join(experiment_path, 'cost_history.txt'), 'a') as f:
            f.write(f'{doc_str} {t} {cost}\n')

        possible_edges = {e: possible_edges[e] for e in edges} # constraint to minimize TODO CHECK HERE

def iterative_upgrade(alpha, topology, n_paths, demands, fiberduct_capacity, gbps_cost, fiberduct_cost, possible_edges, timesteps, upgrade_f, path_selection, experiment_path, cutoff):
    doc_str = f'forward {upgrade_f} {path_selection}-{n_paths}'
    # copy values if using for other experiments
    G = topology.copy()
    possible_edges = {k: possible_edges[k] for k in possible_edges}

    costs = []
    total_cost = 0

    for t in range(timesteps):
        if upgrade_f == 'add_edges':
            cost, edges, capacity_update, fiberduct_update = add_edges(alpha, G, n_paths, demands[t], fiberduct_capacity, gbps_cost, fiberduct_cost, possible_edges, t, path_selection, experiment_path, f'{doc_str} {t}', cutoff)
        elif upgrade_f == 'upgrade_capacity':
            cost, capacity_update, fiberduct_update = upgrade_capacity(alpha, G, n_paths, demands[t], fiberduct_capacity, gbps_cost, fiberduct_cost, path_selection, cutoff)
            edges = []

        costs.append(cost)
        #print(cost)

        total_cost += sum(costs)
        year_cost = sum(costs)

        with open(os.path.join(experiment_path, 'cost_history.txt'), 'a') as f:
            #f.write(f'forward {upgrade_f} {path_selection} {t} {year_cost}\n')
            f.write(f'{doc_str} {t} {year_cost} {cutoff}\n')
        #print('\n\nTOTAL COST AND COST\nFIND HERE\n\n',total_cost,costs)

        # modify topology for next iteration
        for e in edges:
            G.add_edge(*e, prob_failure=possible_edges[e], capacity=0, num_fiberducts=0)
            G.add_edge(*(e[1],e[0]), prob_failure=possible_edges[e], capacity=0, num_fiberducts=0)
        for e in topology.edges:
            G[e[0]][e[1]]['capacity'] += capacity_update[e]
            G[e[0]][e[1]]['num_fiberducts'] += fiberduct_update[e]
            #G[e[1]][e[0]]['capacity'] += capacity_update[(e[1],e[0])]
            #G[e[1]][e[0]]['num_fiberducts'] += fiberduct_update[(e[1],e[0])]
        possible_edges = {k: possible_edges[k] for k in possible_edges if k not in edges}
    #print(total_cost)
    #print('\n\nTOTAL COST AND COST\nFIND HERE\n\n',total_cost,costs)

runs = 1
for run in range(runs):

    # get parameters
    args = get_arguments()
    try:
        os.mkdir(args.path)
    except:
        pass
    write_config_file(args, path= os.path.join(args.path, 'config.cfg'))

    topology_path = 'topology/' + args.topology
    topology_df = read_topology(topology_path,None,None)
    topology = pd_to_nx(topology_df[topology_df.num_fiberducts > 0])

    possible_edges = topology_df[topology_df.num_fiberducts == 0]
    possible_edges = dict(zip(list(zip(possible_edges.from_node, possible_edges.to_node)), possible_edges.prob_failure))
    possible_edges = {k: possible_edges[k] for k in possible_edges if k[0]<k[1]}
    
    G = topology.copy()

    demands = read_demand(topology_path, topology, args.demand_no)
    demands = [{k: args.demand_scale*d[k] for k in d} for d in demands]

    fiberduct_capacity = args.n_fibers_per_fiberduct * args.n_wavelengths_fiber * args.wavelength_capacity
    gbps_cost = args.gbps_cost / args.transceiver_amortization_years
    fiberduct_cost = args.n_fibers_per_fiberduct * args.fiber_cost

    path_sel = args.path_selection.split('-')
    path_selection = path_sel[0]
    n_paths = int(path_sel[1])
    
    upgrade_f = 'add_edges' if args.add_ducts else 'upgrade_capacity'

    time_heuristic = iterative_upgrade if args.time_heuristic_fwd else backwards_iterative_upgrade

    time_heuristic(args.alpha, topology, n_paths, demands, fiberduct_capacity, gbps_cost, fiberduct_cost, possible_edges, args.timesteps, upgrade_f, path_selection, args.path, args.cutoff)

