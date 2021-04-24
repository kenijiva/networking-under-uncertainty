import networkx as nx
from itertools import islice

"""File containing path selection algorithms"""

def KSP(G, k, source=None, target=None, weight=None):
    """K-shortest paths"""
    if source != None or target != None:
        return list(
                islice(nx.shortest_simple_paths(G, source, target, weight=weight), k)
                )
    else:
        paths = [KSP(G,k, source=i, target=j, weight=weight)
                    for i in G.nodes for j in G.nodes if i!=j]
        return [[(p[i], p[i+1]) for i in range(len(p)-1)]
                    for ps in paths for p in ps]

def PST(G, k, source=None, target=None, weight=None):
    """Paths shorther than K"""
    if source != None or target != None:
        paths = nx.shortest_simple_paths(G, source, target, weight=weight)
        selected_paths = []
        for p in paths:
            if len(p)-1 <= k:
                selected_paths.append(p)
            else:
                break
        return selected_paths

        return list(
                islice(nx.shortest_simple_paths(G, source, target, weight=weight), k)
                )
    else:
        paths = [PST(G,k, source=i, target=j, weight=weight)
                    for i in G.nodes for j in G.nodes if i!=j]
        return [[(p[i], p[i+1]) for i in range(len(p)-1)]
                    for ps in paths for p in ps]
