from math import prod
from itertools import combinations,product

def get_flows(topology):
    return [(i,j) for i in topology.nodes for j in topology.nodes if i != j]

def group_paths_by_flow(paths, flows):
    n_paths=len(paths)
    return list(zip(flows, [[paths[p] for p in range(n_paths) if f[0]==paths[p][0][0] and f[1]==paths[p][-1][1]] for f in flows]))

def create_scenarios(parent, all_edges, scens, paths, topology):
    if parent == []:
        idx = 0
    else:
        idx = all_edges.index(parent[-1])+1

    children = []
    for e in all_edges[idx:]:
        scen = parent + [e]

        prob = prod([topology[src][tgt]['prob_failure'] for src,tgt in scen]) * prod([1-topology[src][tgt]['prob_failure'] for src, tgt in set(scen)-set(all_edges)])

        if prob < 10**(-5):
            continue

        infeasible = True

        for p in paths:
            infeasible = infeasible and bool(set(p) & set(parent + [e, (e[1],e[0])]))
            if not infeasible:
                break

        if not infeasible:
            create_scenarios(parent + [e], all_edges, scens, paths, topology)
            scens.append(parent+[e])

def get_scenarios(flow2path, topology):
    all_scens = []
    for i,j in flow2path:
        all_edges = list(set().union(*j))

        all_edges = list(set([(min(e[0],e[1]), max(e[0],e[1])) for e in all_edges])) # use undirected for failures (1,2) indicates (1,2), (2,1)

        scens = [[]]
        create_scenarios([], all_edges, scens, j, topology)
        all_scens.append((i, scens))
    return all_scens
        

def get_flow_scenarios(topology, paths):
    flows = get_flows(topology)
    flows = [(i,j) for i in topology.nodes for j in topology.nodes if i < j]
    flow2path = group_paths_by_flow(paths, flows)

    feasible_scenarios = get_scenarios(flow2path, topology)
    for i in range(len(feasible_scenarios)):
        flow = feasible_scenarios[i][0]
        j = feasible_scenarios[i][1]
        j_edges = set().union(*flow2path[i][1])
        probs = [prod([topology[e[0]][e[1]]['prob_failure'] if e in s else 1-topology[e[0]][e[1]]['prob_failure'] for e in j_edges]) for s in j]
        feasible_scenarios[i] = (flow, list(zip([list(x) for x in j],probs)))

    # make failure scenarios from bidirectional link to two unidirection links
    # (1,2) -> (1,2), (2,1)
    for i, j in feasible_scenarios:
        for k in j:
            for el in k[0].copy():
                if (el[1], el[0]) not in k[0]:
                    k[0].append((el[1], el[0]))

    for i,j in feasible_scenarios.copy():
        feasible_scenarios.append(((i[1],i[0]),j))

    probs = [sum([s[1] for s in j]) for i,j in feasible_scenarios]
    max_prob = min(probs) 
    #print(max_prob)

    return feasible_scenarios
