from plot import *

# edge vs link plot

paths = [
#'experiments/003-link-adding-effect',
'experiments/008-link-adding-effect',
#'experiments/012-link-adding-effect',
]
paths = [
'experiments/002-link-adding-effect' ,]
#'experiments/005-link-adding-effect']
#'experiments/004-link-adding-effect']
show = False
plot_edge_vs_link(paths, show, 'cost_over_edges.pdf')
#plot_edge_vs_link(paths, show, 'cost_over_edges.svg')

paths = ['experiments/014-cost_over_time']
which = ['forward upgrade_capacity KSP-4','backward upgrade_capacity KSP-4', 'forward add_edges KSP-4','backward add_edges KSP-4']
which = ['forward upgrade_capacity KSP-4', 'forward add_edges KSP-4','backward add_edges KSP-4']
plot_cost_over_time(paths, which, show, 'cost_over_time.pdf')

which = ['forward upgrade_capacity KSP-4', 'backward upgrade_capacity KSP-4', 'forward add_edges KSP-4','backward add_edges KSP-4','forward upgrade_capacity PST-6', 'backward upgrade_capacity PST-6', 'forward add_edges PST-6','backward add_edges PST-6']
plot_cost_over_time(paths, which, show, 'path_comparison.pdf')
#plot_cost_over_time(paths, which, show, 'cost_over_time.svg')
#plot_cost_over_time(paths, None, show, 'cost_over_time.pdf')
