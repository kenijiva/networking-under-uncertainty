def find_capacity_update2(beta, gamma, topology, paths, demand, scenarios, edge_cost):
    prob = LpProblem(name="Capacity_increase", sense=LpMinimize)
    edges = sorted(topology.edges)
    nodes = sorted(topology.nodes)
    flows = [(i,j) for i in nodes for j in nodes if i != j]
    n_paths = len(paths)
    capacity = nx.get_edge_attributes(topology, 'capacity')
    flat_scenarios = set([frozenset(k) for i,j in scenarios for k,l in j])
    flat_scenarios = [sorted(list(k)) for k in flat_scenarios]
    scenarios = sorted(scenarios)
    n_scenarios = len(flat_scenarios)

    #############################################
    ##              LP VARIABLES               ##
    #############################################
    managed = LpVariable.dicts("Managed scenario", range(n_scenarios), cat='Binary')
    allocations = LpVariable.dicts("Allocations", range(n_paths), lowBound=0, cat='Continous')
    c_update = LpVariable.dicts("capacity update", edges, lowBound=0, cat='Continous')

    #############################################
    ##         AVAILABILITY CONSTRAINTS        ##
    #############################################
    availability_constraints = []
    for flow, flow_scenarios in scenarios:
        constr = lpSum([managed[flat_scenarios.index(sorted(s))]*p for s,p in flow_scenarios]) >= beta
        availability_constraints.append(constr)

    #############################################
    ##          CAPACITY CONSTRAINTS           ##
    #############################################
    # map edges to paths
    edge2path = dict(zip(edges,[[p for p in range(n_paths) if e in paths[p]] for e in edges]))
    # for each edge
    capacity_constraints = [lpSum([allocations[ind] for ind in edge2path[e]]) <= capacity[e]+c_update[e] for e in edges]

    #############################################
    ##       SATISFACTION CONSTRAINTS          ##
    #############################################
    flow2path = dict(zip(flows, [[p for p in range(n_paths) if f[0]==paths[p][0][0] and f[1]==paths[p][-1][1]] for f in flows]))
    satisfaction_constraints = [lpSum([allocations[path] for path in flow2path[f] if set(paths[path]).isdisjoint(set(s))]) >= managed[flat_scenarios.index(sorted(s))]*gamma*demand[f] for f,scens in scenarios for s,_ in scens]


    objective = lpSum([edge_cost[e]*c_update[e] for e in edges])

    for a in availability_constraints:
        prob += a
    for a in capacity_constraints:
        prob += a
    for a in satisfaction_constraints:
        prob += a
    prob += objective

    solver = GUROBI(msg=0)
    prob.solve(solver)
    

    if prob.status == LpStatusOptimal:
        #print(LpStatus[prob.status])
        #print([e for e in edges])
        #print([value(c_update[e]) for e in edges])
        #print(c_update.value())
        #print([(managed[s].value()) for s in range(n_scenarios)])
        #print(len([value(managed[s]) for s in range(n_scenarios)]))
        #print(objective.value())
        return objective.value()
    else:
        return 999999999999999999999999999999
        raise Exception('Not Implemented')


def find_capacity_update(beta, gamma, topology, paths, demand, scenarios, edge_cost):
    prob = LpProblem(name="Capacity_increase", sense=LpMinimize)

    edges = sorted(topology.edges)
    nodes = sorted(topology.nodes)
    flows = [(i,j) for i in nodes for j in nodes if i != j]

    capacity = nx.get_edge_attributes(topology, 'capacity')

    n_paths = len(paths)
    n_scenarios = len(scenarios)

    allocations = LpVariable.dicts("Allocations", range(n_paths), lowBound=0, cat='Continous')
    managed = LpVariable.dicts("Managed scenario", range(n_scenarios), cat='Binary')
    c_update = LpVariable.dicts("capacity update", edges, lowBound=0, cat='Continous')

    # minimum availability constraint
    min_beta_constraint = lpSum([managed[s]*scenarios[s][1] for s in range(n_scenarios)]) >= beta

    # not any edge is over utilized
    edge2path = dict(zip(edges,[[p for p in range(n_paths) if e in paths[p]] for e in edges]))
    # for each edge
    capacity_constraints = [lpSum([allocations[ind] for ind in edge2path[e]]) <= capacity[e]+c_update[e] for e in edges]

    flow2path = dict(zip(flows, [[p for p in range(n_paths) if f[0]==paths[p][0][0] and f[1]==paths[p][-1][1]] for f in flows]))
    actives = [[int(not any([e in scenarios[s][0] or (e[1],e[0]) in scenarios[s][0] for e in p])) for p in paths] for s in range(n_scenarios)]
    min_bandwidth_constraints = [lpSum([actives[s][ind]*allocations[ind] for ind in flow2path[f]]) >= managed[s]*gamma*demand[f] for s in range(n_scenarios) for f in flows]

    objective = lpSum([edge_cost[e]*c_update[e] for e in edges])

    for c in capacity_constraints + [min_beta_constraint] + min_bandwidth_constraints + [objective]:
        prob += c

    solver = GUROBI(msg=0)
    print('activate solver')
    prob.solve(solver)
    print('finished solver')
    

    if prob.status == LpStatusOptimal:
        #print(LpStatus[prob.status])
        #print([e for e in edges])
        #print([value(c_update[e]) for e in edges])
        #print(c_update.value())
        #print([(managed[s].value()) for s in range(n_scenarios)])
        #print(len([value(managed[s]) for s in range(n_scenarios)]))
        #print(objective.value())
        return objective.value()
    else:
        return 999999999999999999999999999999
        raise Exception('Not Implemented')


def add_edges2(beta, gamma, base_topology, cutoff, demand, edge_cost):
    no_adding_cost = update_capacity(beta, gamma, base_topology, cutoff, demand, edge_cost)
    cheapest = no_adding_cost

    edges = base_topology.edges
    possible_add = [(i,j) for i in base_topology.nodes for j in base_topology.nodes if i!=j and (i,j) not in edges]

    topologies = [([], 0)]

    index_f = lambda possible_add, es: 0 if len(es) == 0 else (possible_add.index(es[-1])+1)

    def highest_comb(cheapest, costs):
        c = sorted(costs)
        cost = 0
        for i in range(len(c)):
            if cost + c[i] < cheapest:
                cost += c[i]
            else:
                break
        return i

    my_costs = [1000000*edge_cost[e] for e in edges]
    print(highest_comb(cheapest, my_costs))


    from tqdm import tqdm

    # number of iterations is the amount of edges added at most
    # sub is at most new_tops size
    for r in tqdm((range(1,len(possible_add))), position=0):
        #print('=========')
        new_tops = [(es + [add], cost+1000000*edge_cost[add]) for es,cost in topologies for add in possible_add[index_f(possible_add, es):]]

        new_tops = [(sorted(i),j) for i,j in new_tops if j < cheapest]

        #Consider only the ones that are cheaper
        #Update cheapest
        acc = 0
        for es, cost in tqdm(new_tops, position=1):
            #print(r, len(new_tops) ,new_tops.index((es,cost)))
            if cost < cheapest:
                #print('comb of at most', highest_comb(cheapest, my_costs))
                #print(cost, cheapest, es)
                ##print(acc)
                acc+=1
                G = base_topology.copy()
                for e in es:
                    G.add_edge(*e, prob_failure=0.04, capacity=0)
                total_cost = update_capacity(beta, gamma, G, cutoff, demand, edge_cost) + cost
                cheapest = min(total_cost, cheapest)
            #else:
            #    print('skip')
        #print('totally', acc)
        
        #print('cheapest is', cheapest)
                

        #filter tops out for next iteration
        new_tops = [(i,j) for i,j in new_tops if j < cheapest]
        #print(r, len(new_tops))
        topologies = new_tops




def update_capacity(beta, gamma, topology, cutoff, demand, edge_cost):
    k = 4
    paths = k_shortest_paths(topology, k)

    scenarios = get_flow_scenarios(topology, paths)
    cost = find_capacity_update2(beta, gamma, topology, paths, demand, scenarios, edge_cost)
    #cus(topology, paths)
    #test(topology, paths)
    #scenarios = get_scenarios(topology, cutoff)
    #print(len(scenarios))
    #scenarios = [(i,sorted(i)) for i,j in scenarios]
    #scenarios2 = get_scenarios2(topology, cutoff)
    #scenarios2 = [(i,sorted(i)) for i,j in scenarios2]
    #scenarios3 = get_scenarios3(topology, beta)
    #scenarios3 = [(i,sorted(i)) for i,j in scenarios3]
    #print(len(scenarios3))
    #print(len(scenarios2))
    #print(sorted(scenarios)==sorted(scenarios2))
    #print(sorted(scenarios)==sorted(scenarios3))
    #cost = find_capacity_update(beta, gamma, topology, paths, demand, scenarios, edge_cost)
    return cost

topology_path = 'topology/B4'
topology = pd_to_nx(read_topology(topology_path))
beta = 0.99
gamma = 1.0
cutoff = 0.0000001
demand = read_demand(topology_path, topology, 0)
n_paths = 4



edge_cost = dict([ ((i,j), random.random()) for i in topology.nodes for j in topology.nodes if i!=j])


#cost = update_capacity(beta, gamma, topology, cutoff, demand, edge_cost)
add_edges2(beta, gamma, topology, cutoff, demand, edge_cost)


