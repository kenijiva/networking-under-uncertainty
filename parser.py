import numpy as np
import os
import os
import pandas as pd
import networkx as nx
import numpy as np
from itertools import islice

def read_demand(topology_path, topology, demand_no):
    nodes = sorted(topology.nodes)
    flows = [(i,j) for i in nodes for j in nodes]
    files = sorted((os.listdir(f'{topology_path}/demand/{demand_no:03d}')))

    demands = []
    for f in files:
        demand = np.loadtxt((f'{topology_path}/demand/{demand_no:03d}/{f}'))
        demand = list(demand.flatten())
        demand = dict([(i,j) for i,j in zip(flows, demand) if i[0] != i[1]])
        demands.append(demand)
    return demands

def read_topology(top):
    dataset = pd.read_csv(os.path.join(top, 'topology.txt'), sep=' ')
    d = dataset[dataset.from_node < dataset.to_node]
    for index, row in dataset.iterrows():
        if row.to_node < row.from_node:
            prob = dataset[(dataset.from_node == row.to_node) & (dataset.to_node == row.from_node)]['prob_failure'].iloc[0]
            dataset.at[index, 'prob_failure'] = prob
    return dataset

def pd_to_nx(dataset):
    G = nx.from_pandas_edgelist(dataset, source="from_node", target="to_node", edge_attr=True, create_using=nx.DiGraph())
    return G

def nx_to_pd(G, cols=None):
    df = nx.to_pandas_edgelist(G, source='from_node', target='to_node')
    if cols != None:
        df = df[cols]
    return df

def write_topology(dataset, top_dir, cols = None):
    top = dataset
    if cols != None:
        top = dataset[cols]
    top.to_csv(os.path.join(top_dir, 'topology.txt'), index = False, sep=' ')
