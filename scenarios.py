from math import prod

def get_scenarios(topology, cutoff):
    def create_scenario(scenario, index, prob):
        scenarios.append(scenario)
        scenario_probs.append(prob)

        for i in range(index+1, n_e):
            new_scenario = scenario.copy()
            new_scenario.append(edges[i])

            p_fail = topology[edges[i][0]][edges[i][1]]['prob_failure']
            new_prob = prob / (1-p_fail) * p_fail
            
            if new_prob >= cutoff:
                create_scenario(new_scenario, i, new_prob)

    edges = sorted(topology.edges)
    n_e = len(edges)

    scenario_probs = []
    scenarios = []

    create_scenario([], -1, prod([1. - topology[i][j]['prob_failure'] for i,j in edges]))



    return list(zip(scenarios, scenario_probs))

def get_scenarios2(topology, cutoff):
    edges = sorted(topology.edges)
    n_e = len(edges)
    scenarios_r = [([], prod([1. - topology[i][j]['prob_failure'] for i,j in edges]))]
    all_scenarios = [([], prod([1. - topology[i][j]['prob_failure'] for i,j in edges]))]
    index_f = lambda edges, es: 0 if len(es)==0 else (edges.index(es[-1])+1)
    for r in range(1,len(edges)):
        #new_scenarios = [(es+[e], prob/(1-topology[e[0]][e[1]]['prob_failure'])*topology[e[0]][e[1]]['prob_failure']) for es, prob in scenarios_r for e in edges[index_f(edges, es):]]
        #new_scenarios = [(i,j) for i,j in new_scenarios if j >= cutoff]

        new_scenarios = []
        for es,prob in scenarios_r:
            index = 0 if len(es)==0 else (edges.index(es[-1])+1)
            for e in edges[index:]:
                p_fail = topology[e[0]][e[1]]['prob_failure']
                new_prob = prob / (1-p_fail) * p_fail
                if new_prob >= cutoff:
                    new_scenarios.append((es+[e],new_prob))
        all_scenarios.extend(new_scenarios)
        scenarios_r = new_scenarios
    return all_scenarios

def get_scenarios3(topology, beta):
    # for each path we have a set of scnearios that we must consider
    edges = sorted(topology.edges)

    acc = 0.
    smallest = 1.
    scenarios = []
    probabilities = []
    smallests = []
    for i in range(len(edges)):
        combs = combinations(edges, i)
        combs = [sorted(list(j)) for j in combs]
        probs = [0.004**len(j)*(1-0.004)**(len(edges)-len(j)) for j in combs]
        prob = sum(probs)
        smallest = min(smallest, *probs)
        
        acc += prob
        scenarios.extend(combs)
        probabilities.extend(probs)
        tree_prob = 1-acc
        smallests.append(smallest)
        
        if acc >= beta:
            break
    return list(zip(scenarios, probabilities))

from itertools import chain, combinations,product
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def get_flows(topology):
    return [(i,j) for i in topology.nodes for j in topology.nodes if i != j]

def group_paths_by_flow(paths, flows):
    n_paths=len(paths)
    return list(zip(flows, [[paths[p] for p in range(n_paths) if f[0]==paths[p][0][0] and f[1]==paths[p][-1][1]] for f in flows]))

def get_all_possible_bad_scenarios(flow2path):
    #create failure scenarios
    # TODO only for scenarios that actually changed
    bad_scenarios = [(i, list(set([frozenset(k) for k in list(product(*j))]))) for i,j in flow2path]
    #make lists from frozenset
    bad_scenarios = [(i, sorted([list(k) for k in j], key=len)) for i,j in bad_scenarios]
    return bad_scenarios

def get_bad_scenarios(possible_bad_scenarios, low_up):
    bad_subset = []
    for b in range(len(possible_bad_scenarios)):
        new_bads = []
        bad = sorted(possible_bad_scenarios[b][1], key=len)
        while len(bad) > 0:
            if low_up == 'low':
                new_bads.append(bad[-1])
                bad = [i for i in bad if not set(i).issubset(bad[-1])]
            elif low_up == 'up':
                new_bads.append(bad[0])
                bad = [i for i in bad if not set(bad[0]).issubset(set(i))]
            else:
                raise Exception('This low_up is not defined')
        bad_subset.append((possible_bad_scenarios[b][0], new_bads))
    return bad_subset


def get_flow_scenarios(topology, paths):
    flows = get_flows(topology)
    flow2path = group_paths_by_flow(paths, flows)

    bad_scenarios = get_all_possible_bad_scenarios(flow2path)
    bad_scenarios_low = get_bad_scenarios(bad_scenarios, 'low')
    bad_scenarios_up = get_bad_scenarios(bad_scenarios, 'up')

    #all scenarios possibily satisfying + bad_scenarios_up
    #some scenarios are included that are subset of a bad...
    feasible_scenarios = [(i, [list(powerset(z)) for z in j]) for i,j in bad_scenarios_low]
    feasible_scenarios = [(i,set([frozenset(l) for k in j for l in k])) for i,j in feasible_scenarios]
    feasible_scenarios = [(i,[list(k) for k in j]) for i,j in feasible_scenarios]
    #remove bad scenarios
    feasible_scenarios = [(feasible_scenarios[i][0], [k for k in feasible_scenarios[i][1] if not any([set(b).issubset(set(k)) for b in bad_scenarios_up[i][1]])]) for i in range(len(feasible_scenarios))]

    #calculate probabilities
    for i in range(len(feasible_scenarios)):
        flow = feasible_scenarios[i][0]
        j = feasible_scenarios[i][1]
        j_edges = set().union(*j)
        probs = [prod([topology[e[0]][e[1]]['prob_failure'] if e in s else 1-topology[e[0]][e[1]]['prob_failure'] for e in j_edges]) for s in j]
        feasible_scenarios[i] = (flow, list(zip(j,probs)))

    probs = [sum([s[1] for s in j]) for i,j in feasible_scenarios]
    max_prob = min(probs) 

    return feasible_scenarios


def test(topology, paths):
    n_paths=len(paths)
    flows= [(i,j) for i in topology.nodes for j in topology.nodes]
    flow2path = list(zip(flows, [[paths[p] for p in range(n_paths) if f[0]==paths[p][0][0] and f[1]==paths[p][-1][1]] for f in flows]))
    print(flow2path[2])
    print(len(list(powerset(set().union(*(flow2path[2][1]))))))
    
    flow2path = [(i, list(set([frozenset(k) for k in list(product(*j))]))) for i,j in flow2path]
    flow2path = [(i, [list(k) for k in j]) for i,j in flow2path]
    bads = flow2path
    edges = sorted(topology.edges)
    bads = [(i,sorted([set(k) for k in j], key=len)) for i,j in bads]
    max_s = 0.
    for m,bad in bads:
        new_bads = []
        while len(bad) > 0:
            new_bads.append(bad[0])
            bad = [i for i in bad if not bad[0].issubset(i)]
        new_bads = [sorted(list(i)) for i in new_bads]
        #print(len(new_bads))
        s = 0.
        for k in new_bads:
            if len(k) == 0: continue
            last = edges.index(k[-1])
            fixed_vars = edges[:last+1]
            g=0.996**(len(fixed_vars)-len(k))*0.004**(len(k))
            s+=g
            #print(g)
            #print(k, fixed_vars)
            #fails = []
            #free_vars = edges[last+1:] not really important
        max_s = max(max_s, s)
        print(m,1-s)
        print('end')
    print('max_availability', 1-max_s)
    print('end')
