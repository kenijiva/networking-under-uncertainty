import networkx as nx
from pulp import *
#def find_capacity_update(beta, gamma, topology, paths, demand, scenarios, link_lease_cost, transceiver_cost, n_wavelengths_fiber, wavelength_capacity, added_edges=[], cheapest=None):

def find_capacity_update(beta, gamma, topology, paths, demand, scenarios, fiberhut_capacity, gbps_cost, fiberhut_cost, added_edges=[], cheapest=None):

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

    # Scenarios that are successful
    managed = LpVariable.dicts("Managed scenario", range(n_scenarios), cat='Binary')
    allocations = LpVariable.dicts("Allocations", range(n_paths), lowBound=0, cat='Continous')
    #c_update = LpVariable.dicts("capacity update", edges, lowBound=0, cat='Continous')
    capacity_update = LpVariable.dicts("capacity update", edges, lowBound=0, cat='Continous')
    fiberhut_update = LpVariable.dicts("fiberhut update", edges, lowBound=0, cat='Integer')
    
    for e in added_edges:
        fiberhut_update[e].lowBound = 1

    #############################################
    ##    AVAILABILITY CONSTRAINTS             ##
    ##    for each flow                        ##
    ##    sum(p_relevant_scenarios) >= beta    ##
    #############################################
    availability_constraints = []
    for flow, flow_scenarios in scenarios:
        constr = lpSum([managed[flat_scenarios.index(sorted(s))]*p for s,p in flow_scenarios]) >= beta
        availability_constraints.append(constr)

    #############################################
    ##    SATISFACTION CONSTRAINTS             ##
    ##    for each flow: each rel. scenario    ##
    ##    active_allocation >= gamma*demand    ##
    #############################################
    flow2path = dict(zip(flows, [[p for p in range(n_paths) if f[0]==paths[p][0][0] and f[1]==paths[p][-1][1]] for f in flows]))
    satisfaction_constraints = [lpSum([allocations[path] for path in flow2path[f] if set(paths[path]).isdisjoint(set(s))]) >= managed[flat_scenarios.index(sorted(s))]*gamma*demand[f] for f,scens in scenarios for s,_ in scens]

    #############################################
    ##    CAPACITY CONSTRAINTS                 ##
    ##    for each edge:                       ##
    ##    sum_allocations_edge <= c + c_up     ##
    #############################################
    # map edges to paths
    edge2path = dict(zip(edges,[[p for p in range(n_paths) if e in paths[p]] for e in edges]))
    capacity_constraints = [lpSum([allocations[ind] for ind in edge2path[e]]) <= capacity[e]+capacity_update[e] for e in edges]

    #############################################
    ##   MAXIMUM CAPACITY UPDATE CONSTRAINTS   ## TODO
    ##   for each edge:                        ## capacity[e] on both sides
    ##   c + c_up <= c_max + c_max_update      ##
    #############################################
    max_capacity_constraints = [capacity[e] + capacity_update[e] <= capacity[e] +fiberhut_update[e] * fiberhut_capacity for e in edges]

    objective = lpSum([capacity_update[e] * gbps_cost + fiberhut_update[e] * fiberhut_cost for e in edges])

    for a in availability_constraints:
        prob += a
    for a in capacity_constraints:
        prob += a
    for a in satisfaction_constraints:
        prob += a
    for a in max_capacity_constraints:
        prob += a

    if cheapest != None:
        prob += lpSum([capacity_update[e] * gbps_cost + fiberhut_update[e] * fiberhut_cost for e in edges]) <= cheapest

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
        #print({k: capacity_update[k].value() for k in capacity_update})
        #print({k: fiberhut_update[k].value() for k in fiberhut_update})
        #print(objective.value())
        return objective.value()
    else:
        #print(LpStatus[prob.status])
        return 999999999999999999999999999999
        raise Exception('Not Implemented')
