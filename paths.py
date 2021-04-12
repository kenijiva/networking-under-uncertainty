import networkx as nx
from itertools import islice

def k_shortest_paths(G, k, source=None, target=None, weight=None):
    if source != None or target != None:
        return list(
                islice(nx.shortest_simple_paths(G, source, target, weight=weight), k)
                )
    else:
        paths = [k_shortest_paths(G,k, source=i, target=j, weight=weight)
                    for i in G.nodes for j in G.nodes if i!=j]
        return [[(p[i], p[i+1]) for i in range(len(p)-1)]
                    for ps in paths for p in ps]

def shortest_paths(G, k, source=None, target=None, weight=None):
    #k = 6
    if source != None or target != None:
        paths = nx.shortest_simple_paths(G, source, target, weight=weight)
        selected_paths = []
        for p in paths:
            if len(p)-1 <= k:
                selected_paths.append(p)
            else:
                break
        #print(len(selected_paths))
        return selected_paths

        return list(
                islice(nx.shortest_simple_paths(G, source, target, weight=weight), k)
                )
    else:
        paths = [shortest_paths(G,k, source=i, target=j, weight=weight)
                    for i in G.nodes for j in G.nodes if i!=j]
        #print([len(ps) for ps in paths])
        return [[(p[i], p[i+1]) for i in range(len(p)-1)]
                    for ps in paths for p in ps]
