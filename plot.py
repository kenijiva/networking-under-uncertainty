import pandas as pd
import os
import ast
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt

def plot_edge_vs_link(paths):
    for path in paths:
        file_path = os.path.join(path, 'topology_evaluations.txt')
        with open(file_path, 'r') as f:
            data = []
            for l in f.readlines():
                row = l.split()[:5]
                row[-1] = float(row[-1])
                row[-2] = int(row[-2])
                edges = ast.literal_eval(''.join(l.split()[5:]))
                row.append(len(edges))
                data.append(row)
            
            data = pd.DataFrame.from_records(data, columns=['time_h', 'upgrade_f', 'path', 't', 'cost', 'n_edges'])
            #print(data[['time_h', 'upgrade_f']].unique())
            unique = data.groupby(['time_h','upgrade_f', 'path', 't']).size().reset_index().rename(columns={0:'count'})[['time_h', 'upgrade_f', 'path', 't']]
            for index, row in unique.iterrows():
                sub_data = data[(data.time_h == row.time_h) & (data.upgrade_f == row.upgrade_f) & (data.path == row.path) & (data.t == row.t)]
                #print(sub_data)
                plot_data = sub_data.groupby('n_edges').min().reset_index()
                plt.plot(plot_data.n_edges, plot_data.cost)
            plt.show()

def plot_cost_over_time(paths):
    for path in paths:
        data = pd.read_csv(os.path.join(path,'cost_history.txt'), delimiter=' ', names=['time_h', 'upgrade_f', 'path', 't', 'cost'], dtype={'time_h':str, 'upgrade_f':str, 'path':str, 't':int, 'cost':float})
        #print(data)
        unique = data.groupby(['time_h','upgrade_f', 'path']).size().reset_index().rename(columns={0:'count'})[['time_h', 'upgrade_f', 'path']]
        for index, row in unique.iterrows():
            sub_data = data[(data.time_h == row.time_h) & (data.upgrade_f == row.upgrade_f) & (data.path == row.path)]
            sub_data = sub_data.sort_values(by='t').reset_index(drop = True)
            time = list(sub_data.t)
            cost = list(sub_data.cost)
            for i in range(len(cost)):
                cost[i] = sum(cost[:i+1])
            plt.plot(time, cost, label = ' '.join([sub_data.time_h.iloc[0], sub_data.upgrade_f.iloc[0], sub_data.path.iloc[0]]))
        plt.legend()
        plt.show()
            #print(, sum(cost))
        #data = pd.read_csv(os.path.join(path,'cost_history.txt'), delimiter=' ')
        #print(data)
        #data.columns = ['time_h', 'upgrade_f', 'path', 't', 'cost']
        #print(data)
        #forward upgrade_capacity KSP 0 146877727.65420002


paths = ['experiments/000-link-adding-effect',
'experiments/001-link-adding-effect',
'experiments/002-link-adding-effect',
'experiments/003-link-adding-effect',
#'experiments/004-link-adding-effect',
'experiments/005-link-adding-effect',
'experiments/006-link-adding-effect',
'experiments/007-link-adding-effect',
'experiments/008-link-adding-effect',
'experiments/009-link-adding-effect',
'experiments/010-link-adding-effect',
'experiments/011-link-adding-effect',
'experiments/012-link-adding-effect',]
paths = ['experiments/014-cost_over_time']
#plot_edge_vs_link(paths)
plot_cost_over_time(paths)




