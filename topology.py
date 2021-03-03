import os
import pandas as pd
import networkx as nx
import numpy as np
from itertools import islice

from util import *

def read_topology(top, weibull_scale=0.001, weibull_shape=0.8):
    dataset = pd.read_csv(os.path.join(top, 'topology.txt'), sep=' ')
    if weibull_scale != None and weibull_shape != None:
        dataset['prob_failure'] = weibull(dataset.shape[0], weibull_scale, weibull_shape)
    return dataset

def pd_to_nx(dataset):
    G = nx.from_pandas_edgelist(dataset, source="from_node", target="to_node", edge_attr=True, create_using=nx.DiGraph())
    #G = nx.from_pandas_edgelist(dataset, target="from_node", source="to_node", edge_attr=True, create_using=nx.DiGraph())
    return G

def nx_to_pd(G, cols=None):
    df = nx.to_pandas_edgelist(G, source='from_node', target='to_node')
    if cols != None:
        df = df[cols]
    return df

def write_topology(dataset, top_dir, cols = None):
    if cols == None:
        top = dataset['to_node', 'from_node', 'capacity', 'prob_failure']
    else:
        top = dataset[cols]
    top.to_csv(os.path.join(top_dir, 'topology.txt'), index = False)
