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

def upgrade_capacity(alpha, topology, n_paths, demand, fiberduct_capacity,
        gbps_cost, fiberduct_cost, path_selection, cutoff, added_edges=[],
        max_capacity_update=None, max_fiberduct_update=None):
    """Given the parameters this method creates scenarios and calls the MILP
    to find the optimal capacity upgrade on the network.
    :param alpha: minimum availability specified in SLA
    :param topology: Topology of the network that is going to be upgraded
    :param n_paths: For KSP this is k, for PST this is path shorter than n_paths
    :param demand: Forecasted traffic matrix
    :param fiberduct_capacity: How much capacity a fiberduct supports.
    :param gbps_cost: Cost of transceiver in $/Gbps/year
    :param fiberduct_cost: Fiberduct cost in $/year
    :param path_selection: Path selection algorithm
    :param cutoff: Param to pass to MILP to enforce construction of these fiber ducts
    :param max_capacity_update: Param for backward heuristic to reduce set of possibilities
    :param max_fiberduct_update: Similar to max_capacity_update
    :return: return cost, capacity upgrade and fiber duct upgrades"""

    # Create paths
    if path_selection == 'KSP':
        paths = KSP(topology, n_paths)
    elif path_selection == 'PST':
        paths = PST(topology, n_paths)
    # Get scenarios
    scenarios = get_flow_scenarios(topology, paths, cutoff)
    # Call MILP, get return values
    cost, capacity_update, fiberduct_update = find_capacity_update(
            alpha, topology, paths, demand, scenarios, fiberduct_capacity, gbps_cost,
            fiberduct_cost, added_edges=added_edges, max_capacity_update=max_capacity_update,
            max_fiberduct_update=max_fiberduct_update)

    return cost, capacity_update, fiberduct_update

def add_edges(alpha, topology, n_paths, demand, fiberduct_capacity, gbps_cost,
        fiberduct_cost, possible_edges, timestep, path_selection, experiment_path,
        doc_str, cutoff):
    """Given the parameters this method evaluates multiple topologies and
    return the cheapest such that network upgrades can be derived.
    :param alpha: minimum availability specified in SLA
    :param topology: Topology of the network that is going to be upgraded
    :param n_paths: For KSP this is k, for PST this is path shorter than n_paths
    :param demand: Forecasted traffic matrix
    :param fiberduct_capacity: How much capacity a fiberduct supports.
    :param gbps_cost: Cost of transceiver in $/Gbps/year
    :param fiberduct_cost: Fiberduct cost in $/year
    :param possible_edges: Set of constructible links
    :param timestep: Param indicating which t in {1,...,T}
    :param path_selection: Path selection algorithm
    :param experiment_path: Path to experiment folder to store data
    :param doc_str: doc_str just used for documentation
    :param cutoff: Param to pass to MILP to enforce construction of these fiber ducts
    :return: cheapest solution"""

    # helper method for tracking how much has been evaluated
    def update_bars(reset = False):
        if reset: qbar.reset()
        num_combs[r] = len(new_tops)
        if cheapest == float("inf"):
            max_r = len(possible_edges)
        else:
            max_r = int(cheapest / fiberduct_cost)
        qbar.total = num_combs[r]
        pbar.total = sum(num_combs[:max_r+1])
        pbar.set_postfix({'improvement:': round(no_adding_cost/cheapest,2),
            'cheapest:': int(cheapest) if cheapest != float('inf') else float('inf'),
            'timestep': timestep})
        qbar.set_postfix({f'#edges per comb': r})
        pbar.refresh()
        qbar.refresh()

    # Base solution: upgrade capacity without additional links
    cheapest, capacity_update, fiberduct_update = upgrade_capacity(alpha, topology,
            n_paths, demand, fiberduct_capacity, gbps_cost, fiberduct_cost,
            path_selection, cutoff)
    cheapest_capacity_update = capacity_update
    cheapest_fiberduct_update = fiberduct_update
    no_adding_cost = cheapest
    cheapest_edges = []

    # Write result
    f_name = 'topology_evaluations.txt'
    with open(os.path.join(experiment_path, f_name), 'a') as f:
        f.write(f'{doc_str} {cheapest} {cheapest_edges}\n')

    # Find cheaper topology
    possible_add = possible_edges.keys()

    # Show progress
    pbar = tqdm(desc='Outer Loop', file=sys.stdout, dynamic_ncols=True)
    qbar = tqdm(desc='Inner Loop', file=sys.stdout, dynamic_ncols=True)
    num_combs = [math.comb(len(possible_add), i)
            for i in range(0, len(possible_add)+1)]
    pbar.update(1)

    topologies = [[]]
    for r in range(1,len(possible_add)):
        # Can topology with more fiber huts even be cheaper
        if r * fiberduct_cost >= cheapest:
            break

        prev_cheapest = cheapest

        # Create topologies to check out from topologies and possible_add
        new_tops = set([frozenset(es+[add]) for es in topologies
            for add in possible_add if add not in es])
        # To list of lists again
        new_tops = [sorted(list(es)) for es in new_tops]

        update_bars(reset = True)

        # Tops that looked at
        succ_tops = []
        for es in new_tops:
            # Create topology
            G = topology.copy()
            for e in es:
                G.add_edge(*e, prob_failure=possible_edges[e],
                        capacity=0, num_fiberducts=0)
                G.add_edge(*(e[1],e[0]), prob_failure=possible_edges[e],
                        capacity=0, num_fiberducts=0)

            # Upgrade capacity of new topology and append to succesful
            total_cost, capacity_update, fiberduct_update = upgrade_capacity(
                    alpha, G, n_paths, demand, fiberduct_capacity, gbps_cost,
                    fiberduct_cost, path_selection, cutoff, added_edges=es)
            succ_tops.append((es, total_cost))
            # Write result

            with open(os.path.join(experiment_path, f_name), 'a') as f:
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

        # Search heuristic: sort by cost to explore promising one first
        new_tops = sorted(succ_tops, key=lambda x: x[1])
        # Space reduction heuristic: Use topologies cheaper than prev iteration
        new_tops = [es for es,co  in new_tops if r*fiberduct_cost < cheapest
                and co < prev_cheapest]

        topologies = new_tops

    return cheapest, cheapest_edges, cheapest_capacity_update, cheapest_fiberduct_update

def backwards_iterative_upgrade(alpha, topology, n_paths, demands,
        fiberduct_capacity, gbps_cost, fiberduct_cost, possible_edges,
        timesteps, upgrade_f, path_selection, experiment_path, cutoff):
    """Backward heuristic for creating a series of strategies over time.
    :param alpha: minimum availability specified in SLA
    :param topology: Topology of the network that is going to be upgraded
    :param n_paths: For KSP this is k, for PST this is path shorter than n_paths
    :param demands: Forecasted traffic matrices
    :param fiberduct_capacity: How much capacity a fiberduct supports.
    :param gbps_cost: Cost of transceiver in $/Gbps/year
    :param fiberduct_cost: Fiberduct cost in $/year
    :param possible_edges: Set of constructible links
    :param timesteps: How many years in the future
    :param upgrade_f: Use upgrade_capacity or add_edges
    :param path_selection: Path selection algorithm
    :param experiment_path: Path to experiment folder to store data
    :param cutoff: Param to pass to MILP to enforce construction of these fiber ducts"""

    # create string for documentation
    doc_str = f'backward {upgrade_f} {path_selection}-{n_paths}'

    # copy values if using for other experiments
    G = topology.copy()
    possible_edges = {k: possible_edges[k] for k in possible_edges}

    # e.g. if at t=4 capacity upgade of 1000 on link e created
    # then it does not make sense to create upgrade of
    # 1200 at t=3
    capacity_update = None
    fiberduct_update = None

    # loop over demands in reversed time
    for t in reversed(range(timesteps)):

        if upgrade_f == 'add_edges':
            cost, edges, capacity_update, fiberduct_update = add_edges(alpha,
                    G, n_paths, demands[t], fiberduct_capacity, gbps_cost,
                    fiberduct_cost, possible_edges, t, path_selection,
                    experiment_path, f'{doc_str} {t}', cutoff)
        elif upgrade_f == 'upgrade_capacity':
            cost, capacity_update, fiberduct_update = upgrade_capacity(alpha,
                    G, n_paths, demands[t], fiberduct_capacity, gbps_cost,
                    fiberduct_cost, path_selection, cutoff,
                    max_capacity_update = capacity_update,
                    max_fiberduct_update = fiberduct_update)
            edges = []

        # Documentation: cost is yearly cost
        with open(os.path.join(experiment_path, 'cost_history.txt'), 'a') as f:
            f.write(f'{doc_str} {t} {cost}\n')

        # reduce the space of constructible links
        possible_edges = {e: possible_edges[e] for e in edges}


def iterative_upgrade(alpha, topology, n_paths, demands, fiberduct_capacity,
        gbps_cost, fiberduct_cost, possible_edges, timesteps, upgrade_f,
        path_selection, experiment_path, cutoff):
    """Greedy heuristic for creating a series of strategies over time.
    :param alpha: minimum availability specified in SLA
    :param topology: Topology of the network that is going to be upgraded
    :param n_paths: For KSP this is k, for PST this is path shorter than n_paths
    :param demands: Forecasted traffic matrices
    :param fiberduct_capacity: How much capacity a fiberduct supports.
    :param gbps_cost: Cost of transceiver in $/Gbps/year
    :param fiberduct_cost: Fiberduct cost in $/year
    :param possible_edges: Set of constructible links
    :param timesteps: How many years in the future
    :param upgrade_f: Use upgrade_capacity or add_edges
    :param path_selection: Path selection algorithm
    :param experiment_path: Path to experiment folder to store data
    :param cutoff: Param to pass to MILP to enforce construction of these fiber ducts"""

    doc_str = f'forward {upgrade_f} {path_selection}-{n_paths}'
    # copy values if using for other experiments
    G = topology.copy()
    possible_edges = {k: possible_edges[k] for k in possible_edges}

    costs = []

    for t in range(timesteps):
        if upgrade_f == 'add_edges':
            cost, edges, capacity_update, fiberduct_update = add_edges(alpha,
                    G, n_paths, demands[t], fiberduct_capacity, gbps_cost,
                    fiberduct_cost, possible_edges, t, path_selection,
                    experiment_path, f'{doc_str} {t}', cutoff)
        elif upgrade_f == 'upgrade_capacity':
            cost, capacity_update, fiberduct_update = upgrade_capacity(alpha,
                    G, n_paths, demands[t], fiberduct_capacity, gbps_cost,
                    fiberduct_cost, path_selection, cutoff)
            edges = []

        costs.append(cost)

        year_cost = sum(costs)

        # Document yearly cost
        file_n = 'cost_history.txt'
        with open(os.path.join(experiment_path, file_n), 'a') as f:
            f.write(f'{doc_str} {t} {year_cost} {cutoff}\n')

        # modify topology for next iteration
        for e in edges:
            G.add_edge(*e, prob_failure=possible_edges[e],
                    capacity=0, num_fiberducts=0)
            G.add_edge(*(e[1],e[0]), prob_failure=possible_edges[e],
                    capacity=0, num_fiberducts=0)
        for e in topology.edges:
            G[e[0]][e[1]]['capacity'] += capacity_update[e]
            G[e[0]][e[1]]['num_fiberducts'] += fiberduct_update[e]
        possible_edges = {k: possible_edges[k] for k in possible_edges
                if k not in edges}

# get experiment parameters
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

# Run experiment
time_heuristic(args.alpha, topology, n_paths, demands, fiberduct_capacity, gbps_cost, fiberduct_cost, possible_edges, args.timesteps, upgrade_f, path_selection, args.path, args.cutoff)

