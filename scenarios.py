from math import prod
from itertools import combinations,product

def get_flows(topology):
    """Internal method to generate list of flows for a topology"""
    return [(i,j) for i in topology.nodes for j in topology.nodes if i != j]

def group_paths_by_flow(paths, flows):
    """Internal method grouping paths by flows"""
    n_paths=len(paths)
    return list(zip(flows, [[paths[p]
        for p in range(n_paths) if f[0]==paths[p][0][0] and
        f[1]==paths[p][-1][1]] for f in flows]))

def create_scenarios(parent, all_edges, scens, paths, topology, cutoff):
    """Internal method creating scenarios recursively"""
    if parent == []:
        idx = 0
    else:
        idx = all_edges.index(parent[-1])+1

    children = []
    for e in all_edges[idx:]:
        scen = parent + [e]

        prob = (prod([topology[src][tgt]['prob_failure'] for src,tgt in scen])
                * prod([1-topology[src][tgt]['prob_failure']
                    for src, tgt in set(all_edges)-set(scen)]))

        if prob < cutoff:
            continue

        infeasible = True

        for p in paths:
            infeasible = infeasible and bool(set(p) & set(parent + [e, (e[1],e[0])]))
            if not infeasible:
                break

        if not infeasible:
            create_scenarios(parent + [e], all_edges, scens, paths,
                    topology, cutoff)
            scens.append(parent+[e])

def get_scenarios(flow2path, topology, cutoff):
    """Internal method creating scenarios and returning them with probabilities"""
    all_scens = []
    for i,j in flow2path:
        all_edges = list(set().union(*j))

        all_edges = list(set([(min(e[0],e[1]), max(e[0],e[1])) for e in all_edges]))

        scens = [[]]
        create_scenarios([], all_edges, scens, j, topology, cutoff)

        probs = ([prod([topology[src][tgt]['prob_failure'] for src,tgt in scen])
            * prod([1-topology[src][tgt]['prob_failure']
                for src, tgt in set(all_edges)-set(scen)]) for scen in scens])

        all_scens.append((i, list(zip(scens,probs))))
    return all_scens
        

def get_flow_scenarios(topology, paths, cutoff):
    """Method returning feasible scenarios with their probabilities per flow
    :param topology: input topology to the MILP
    :param paths: selected paths
    :param cutoff: cutoff used for faster computation
    :return: feasible scenarios per flow"""

    # Construct the feasible scenarios
    flows = get_flows(topology)
    flows = [(i,j) for i in topology.nodes for j in topology.nodes if i < j]
    flow2path = group_paths_by_flow(paths, flows)

    feasible_scenarios = get_scenarios(flow2path, topology, cutoff)

    # Make (1,2) and (2,1) fail together
    for i, j in feasible_scenarios:
        for k in j:
            for el in k[0].copy():
                if (el[1], el[0]) not in k[0]:
                    k[0].append((el[1], el[0]))

    # scenarios for flow (1,2) and (2,1) are identical -> copy them
    for i,j in feasible_scenarios.copy():
        feasible_scenarios.append(((i[1],i[0]),j))

    probs = [sum([s[1] for s in j]) for i,j in feasible_scenarios]
    max_prob = min(probs) 

    return feasible_scenarios
