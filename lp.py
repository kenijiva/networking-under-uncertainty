import networkx as nx
from pulp import *
#def find_capacity_update(alpha, topology, paths, demand, scenarios, link_lease_cost, transceiver_cost, n_wavelengths_fiber, wavelength_capacity, added_edges=[], cheapest=None):

def find_capacity_update(alpha, topology, paths, demand, scenarios, fiberduct_capacity, gbps_cost, fiberduct_cost, added_edges=[], cheapest=None, max_capacity_update=None, max_fiberduct_update=None):

    prob = LpProblem(name="Capacity_increase", sense=LpMinimize)
    edges = sorted(topology.edges)
    nodes = sorted(topology.nodes)
    flows = [(i,j) for i in nodes for j in nodes if i != j]
    n_paths = len(paths)
    capacity = nx.get_edge_attributes(topology, 'capacity')
    num_fiberducts = nx.get_edge_attributes(topology, 'num_fiberducts')
    flat_scenarios = set([frozenset(k) for i,j in scenarios for k,l in j])
    flat_scenarios = [sorted(list(k)) for k in flat_scenarios]
    scenarios = sorted(scenarios)
    n_scenarios = len(flat_scenarios)
    #print(n_scenarios)

    #############################################
    ##              LP VARIABLES               ##
    #############################################

    # Scenarios that are successful
    managed = LpVariable.dicts("Managed scenario", range(n_scenarios), cat='Binary')
    allocations = LpVariable.dicts("Allocations", range(n_paths), lowBound=0, cat='Continous')
    capacity_update = LpVariable.dicts("capacity update", edges, lowBound=0, cat='Continous')
    fiberduct_update = LpVariable.dicts("fiberduct update", edges, lowBound=0, cat='Integer')
    
    if max_fiberduct_update != None:
        for k in max_fiberduct_update:
            if k in edges:
                fiberduct_update[k].upBound = max_fiberduct_update[k]
    if max_capacity_update != None:
        for k in max_capacity_update:
            if k in edges:
                capacity_update[k].upBound = max_capacity_update[k]

    for e in added_edges:
        fiberduct_update[e].lowBound = 1

    bidirectional_constraints = []
    for e in added_edges:
        constr = fiberduct_update[(e[1],e[0])] == fiberduct_update[e]
        prob += constr

    #############################################
    ##    AVAILABILITY CONSTRAINTS             ##
    ##    for each flow                        ##
    ##    sum(p_relevant_scenarios) >= alpha    ##
    #############################################
    availability_constraints = []
    for flow, flow_scenarios in scenarios:
        constr = lpSum([managed[flat_scenarios.index(sorted(s))]*p for s,p in flow_scenarios]) >= alpha
        availability_constraints.append(constr)

    #############################################
    ##    SATISFACTION CONSTRAINTS             ##
    ##    for each flow: each rel. scenario    ##
    ##    active_allocation >= demand    ##
    #############################################
    flow2path = dict(zip(flows, [[p for p in range(n_paths) if f[0]==paths[p][0][0] and f[1]==paths[p][-1][1]] for f in flows]))
    satisfaction_constraints = [lpSum([allocations[path] for path in flow2path[f] if set(paths[path]).isdisjoint(set(s))]) >= managed[flat_scenarios.index(sorted(s))]*demand[f] for f,scens in scenarios for s,_ in scens]

    #############################################
    ##    CAPACITY CONSTRAINTS                 ##
    ##    for each edge:                       ##
    ##    sum_allocations_edge <= c + c_up     ##
    #############################################
    # map edges to paths
    edge2path = dict(zip(edges,[[p for p in range(n_paths) if e in paths[p]] for e in edges]))
    capacity_constraints = [lpSum([allocations[ind] for ind in edge2path[e]]) <= capacity[e]+capacity_update[e] for e in edges]

    #############################################
    ##   MAXIMUM CAPACITY UPDATE CONSTRAINTS   ##
    ##   for each edge:                        ##
    ##   c + c_up <= c_max + c_max_update      ##
    #############################################
    max_capacity_constraints = [capacity[e] + capacity_update[e] <= num_fiberducts[e]*fiberduct_capacity +fiberduct_update[e] * fiberduct_capacity for e in edges]

    objective = lpSum([capacity_update[e] * gbps_cost + fiberduct_update[e] * (fiberduct_cost/2) for e in edges])

    for a in availability_constraints:
        prob += a
    for a in capacity_constraints:
        prob += a
    for a in satisfaction_constraints:
        prob += a
    for a in max_capacity_constraints:
        prob += a

    if cheapest != None:
        prob += lpSum([capacity_update[e] * gbps_cost + fiberduct_update[e] * fiberduct_cost for e in edges]) <= cheapest

    prob += objective

    solver = GUROBI(msg=0)
    prob.solve(solver)

    if prob.status == LpStatusOptimal:
        #print(objective.value())
        return objective.value(), {k: capacity_update[k].value() for k in capacity_update}, {k: fiberduct_update[k].value() for k in fiberduct_update}
    else:
        #print('heeeeeeeeeeeee')
        #print(float("inf"))
        return float("inf"), None, None
        raise Exception('Not Implemented')
