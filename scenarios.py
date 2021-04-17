from math import prod
from itertools import combinations,product

def get_flows(topology):
    return [(i,j) for i in topology.nodes for j in topology.nodes if i != j]

def group_paths_by_flow(paths, flows):
    n_paths=len(paths)
    return list(zip(flows, [[paths[p] for p in range(n_paths) if f[0]==paths[p][0][0] and f[1]==paths[p][-1][1]] for f in flows]))

def get_scenarios(flow2path, topology):
    res = []
    lb_scens = set()
    for i,j in flow2path:
        all_scens = set()
        all_edges = set().union(*j)

        all_smaller_cutoff = False
        for path_len in range(len(j)):
            if all_smaller_cutoff:
                break

            fail_paths_gen = combinations(j,path_len)
            all_smaller_cutoff = True
            for fail_paths in fail_paths_gen:
                scens = set([(frozenset(p)) for p in list(product(*fail_paths))])
                scens = scens-all_scens
                scens = set([scen for scen in scens if not any([lb.issubset(scen) for lb in lb_scens])])
                lb_scens = lb_scens.union(set([scen for scen in scens if all([scen & set(path) for path in j])]))

                scens = scens-all_scens
                all_scens = all_scens.union(scens)
                if scens == set():
                    probs = [0.]
                else:
                    probs = [prod([topology[src][tgt]['prob_failure'] for src,tgt in scen])*prod([1-topology[src][tgt]['prob_failure'] for src,tgt in all_edges-scen]) for scen in scens]
                    
                all_smaller_cutoff = all_smaller_cutoff and max(probs) <=  10**(-5)
            all_probs = [prod([topology[src][tgt]['prob_failure'] for src,tgt in scen])*prod([1-topology[src][tgt]['prob_failure'] for src,tgt in all_edges-scen]) for scen in all_scens]
            all_smaller_cutoff = (sum(all_probs)) >= 0.999

        res.append((i,all_scens))

    res = [(i, set([scen for scen in all_scens if not any(lb.issubset(scen) for lb in lb_scens)])) for i, all_scens in res]

    return res

def get_flow_scenarios(topology, paths):
    # TODO flow 1 2 and 2 1 share 100% scenarios:
    # TODO use only flows i < j. flow2path change edges direction s.t  s < t
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
