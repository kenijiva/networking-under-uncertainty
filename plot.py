import pandas as pd
import matplotlib
matplotlib.use('tkagg')
from matplotlib import pyplot as plt
from plot_topology import *
from topology import*
with open('0.txt', 'r') as f:
    lines = f.readlines()
    lines = [l.split() for l in lines]
    lines = [l[0:3]+[''.join(l[3:])] for l in lines]
    df = pd.DataFrame.from_records(lines, columns=['scale', 'cost','r','added'])
    df['scale'] = df.scale.astype('float64')
    df['cost'] = df.cost.astype('float64')
    df['r'] = df.r.astype('int64')
    df['scale'] = df.scale / 0.5
    #data = df.groupby(by=['scale', 'r']).min().reset_index()
    data = df

    scales = data.scale.unique()
    scale_data = []
    for s in scales:
        scale_data.append(data[data.scale == s].sort_values(by='cost').reset_index(drop=True).loc[0])
    scale_data = pd.DataFrame.from_records(scale_data)

    plt.plot(scale_data.scale, scale_data.cost, label='Best', color = 'black')

    for r in data.r.unique():
        tmp = data[data.r==r]
        scales = tmp.scale.unique()
        tmp = pd.DataFrame.from_records([tmp.loc[tmp[tmp.scale==s].cost.idxmin()] for s in scales])
        plt.plot(tmp.scale, tmp.cost, label=f'{r} edges', linestyle='--')

    plt.legend()
    plt.xticks(data.scale.unique())
    plt.xlabel('Demand Scale')
    plt.ylabel('Cost (USD)')
    plt.savefig('demands.png')
    plt.clf()


    # for each scale: for each r
    r_dfs = []
    scales = data.scale.unique()
    for s in scales:
        tmp = data[data.scale == s]
        rs = tmp.r.unique()
        r_data = []
        for r in rs:
            row = tmp[tmp.r == r].sort_values(by='cost').reset_index(drop=True).loc[0]
            r_data.append(row)
        r_data = pd.DataFrame.from_records(r_data)
        r_dfs.append(r_data)

    import math
    for df,s in zip(r_dfs, scales):
        plt.plot(df.r, df.cost, marker='o')
        plt.xticks(df.r)
        plt.xlabel('#edges added')
        plt.ylabel('Cost (USD)')
        #df.plot(x='r', y='cost', xticks=df.r, linestyle='--', marker='o', xlabel = '#edges added', ylabel = 'Cost (USD)')
        #max_cost = df.loc[(df['cost'].idxmax())]
        init_cost = df[df.r == 0].cost.loc[0]
        min_cost = df.loc[(df['cost'].idxmin())].cost

        init_cost_r = df[df.r == 0].r.loc[0]
        min_cost_r = df.loc[(df['cost'].idxmin())].r
        line_x = (init_cost_r+min_cost_r)/2

        plt.plot([line_x]*2, [init_cost, min_cost], color = 'black', linestyle = '--')
        plt.text(s=f'Cost Difference: {round((init_cost-min_cost)/1000000,2)} Millions\n{round(init_cost/min_cost,2)} times cheaper', x=line_x, y=(init_cost+min_cost)/2)


        plt.suptitle(f'scale={s}')
        plt.savefig(f'{s}.png')
        plt.clf()
        #plt.show()

top = pd_to_nx(read_topology('topology/B4'))
import ast
xs = []
for df, s in zip(r_dfs, scales):
    x = (df.loc[df.cost.idxmin()].added)
    x = ast.literal_eval(x)
    if s >= 2.:
        xs.append(x)
draw_baseline_comparisons(top, xs, save = False, show=True)
        
    
    
    #print(df)
#pd.read_csv('0.txt', sep=' ')
