import pandas as pd
import os
import ast
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager


def plot_edge_vs_link(paths, show, name):
    plt.rcParams['axes.facecolor'] = 'E6E6E6'
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams.update({
                "font.size":18,
                "text.usetex": True,
                "font.family": "sans-serif",
                "font.sans-serif": ["Helvetica"]})
    plt.clf()
    colours = ["#03c03c","#f39a27","#976ed7","#c47a53","#579abe", "#eada52"]
    markers = ["o", "^", "D"]
    col_idx = 0
    for path in paths:
        col_idx = 0
        plt.grid(axis='y', color='white')
        plt.xlabel('Number of links constructed', fontsize = 18)
        plt.ylabel('Cost [USD]', fontsize = 18)
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
            unique = data.groupby(['time_h','upgrade_f', 'path', 't']).size().reset_index().rename(columns={0:'count'})[['time_h', 'upgrade_f', 'path', 't']]
            n_edges = -1
            for index, row in unique.iterrows():
                sub_data = data[(data.time_h == row.time_h) & (data.upgrade_f == row.upgrade_f) & (data.path == row.path) & (data.t == row.t)]
                plot_data = sub_data.groupby('n_edges').min().reset_index()
                x = 0
                while  10**(x+1) < max(sub_data.cost):
                    x+=1
                ticks = [0] + [y*10**x for y in range(x)]


                n_edges = max(max(plot_data.n_edges), n_edges)
                plt.plot(plot_data.n_edges, plot_data.cost, colours[col_idx%len(colours)], marker=markers[col_idx%len(markers)])
                plt.yticks(ticks)
                col_idx = (col_idx + 1) 
                plot_data = plot_data[['n_edges','cost']]
                #plot_data.to_csv('cost_over_edges.dat', header = False, index=False, sep = ' ')

        if show:
            plt.show()
        else:
            plt.savefig(os.path.join('plots', name), bbox_inches = 'tight', pad_inches = 0.05)

def plot_cost_over_time(paths, which, show, name):
    plt.rcParams['axes.facecolor'] = 'E6E6E6'#'#F5F5F5'#'#cfd5d3'# '#A9A9A9'
    plt.rcParams.update({
                "font.size": 18,
                "text.usetex": True,
                "font.family": "sans-serif",
                "font.sans-serif": ["Helvetica"]})
    markers = ["o", "^", "D"]
    colours = ["#03c03c","#f39a27","#976ed7","#c47a53","#579abe", "#eada52"]
    col_idx = 0
    plt.clf()
    plt.grid(axis='y', color='white')
    plt.xlabel('Time [years]', fontsize = 18)
    plt.ylabel('Cost [USD]', fontsize = 18)
    for path in paths:
        data = pd.read_csv(os.path.join(path,'cost_history.txt'), delimiter=' ', names=['time_h', 'upgrade_f', 'path', 't', 'cost', 'cutoff'], dtype={'time_h':str, 'upgrade_f':str, 'path':str, 't':int, 'cost':float})
        unique = data.groupby(['time_h','upgrade_f', 'path', 'cutoff']).size().reset_index().rename(columns={0:'count'})[['time_h', 'upgrade_f', 'path', 'cutoff']]
        for index, row in unique.iterrows():
            if which == None or f'{row.time_h} {row.upgrade_f} {row.path} {row.cutoff}' in which:
                sub_data = data[(data.time_h == row.time_h) & (data.upgrade_f == row.upgrade_f) & (data.path == row.path) & (data.cutoff == row.cutoff)]
                sub_data = sub_data.sort_values(by='t').reset_index(drop = True)


                time = [0] + [k+1 for k in list(sub_data.t)]
                cost = list(sub_data.cost)
                for i in range(len(cost)):
                    cost[i] = sum(cost[:i+1])
                cost = [0] + cost

                label = row.time_h + ' iteration with' + ('out ' if row.upgrade_f == 'upgrade_capacity' else ' ') + 'adding links ' + row.path  + ' ' + str(row.cutoff)

                sub_data = sub_data[['t','cost']]
                #sub_data.to_csv('cost_over_time.dat', header = False, index=False, sep = ' ')
                plt.plot(time, cost, label = label, color = colours[col_idx%len(colours)], marker = markers[col_idx%len(markers)])
                col_idx += 1
        font = font_manager.FontProperties(family='sans-serif', style='normal', size=12)
        plt.legend(fontsize=12,facecolor = 'white')

        if show:
            plt.show()
        else:
            plt.savefig(os.path.join('plots', name), bbox_inches = 'tight', pad_inches = 0.05)
