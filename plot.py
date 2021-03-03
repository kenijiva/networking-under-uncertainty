import matplotlib
matplotlib.use("tkagg")
import matplotlib.pyplot as plt

for run in range(3):
    rs = []
    costs = []
    time = 0
    with open(f'{run}.txt') as f:
        lines = f.readlines()
        for l in lines:
            if 'TIME' in l:
                time = float(lines[-1].split()[2])/3600
                continue
            words = l.split()
            r = int(words[0])
            cheapest = float(words[1])
            rs.append(r)
            costs.append(cheapest)
    
    for i in range(len(rs), 94):
        rs.append(i)
        costs.append(costs[-1])
    
    best_impr = round((costs[0]/min(costs)),2)
    time = round(time, 2)
    
    plt.suptitle('Cost per added edges', fontsize=16)
    plt.title(f'Runtime: {time} - best improvement: {best_impr}')
    plt.xlabel('# of added edges')
    plt.ylabel('Cost in $')
    plt.xticks([i for i in range(94) if i % 5 == 0])
    plt.plot(rs, costs)
    plt.show()
