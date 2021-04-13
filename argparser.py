import numpy as np
import os
import argparse
from configargparse import ArgumentParser

def get_arguments():
    parser = ArgumentParser('Argument Parser')

    parser.add('-c', '--config', is_config_file = True, help = 'Path to config file')
    parser.add('--path', type = str, default = '.', help = 'Path to experiment')

    # Arguments for demand history
    parser.add('--demand_scale', type = float, default = 1., help = 'How should the stored demand be scaled. demand_scale * demand[demand_no] is the initial demand.')
    parser.add('--timesteps', type = int, default = 5, help = 'Number of timesteps to optimize for')
    parser.add('--demand_no', type = int, default = 0, help = 'Demand file in TOPOLOGY\'s folder')

    # Topology arguments
    parser.add('--topology', type = str, default = 'my_B4', help = 'Name of the topology that can be found in the topology folder')

    # SLA arguments
    parser.add('--alpha', type = float, default = 0.999, help = 'Minimum availability for each flow')

    # Path arguments
    parser.add('--n_paths', type = int, default = 4, help = 'Number of paths per flow')
    
    # Cost relevant arguments
    parser.add('--wavelength_capacity', type = float, default = 400, help = 'Number of Gbps per wavelength')
    parser.add('--n_wavelengths_fiber', type = float, default = 64, help = 'Number of wavelengths per fiber')
    parser.add('--gbps_cost', type = float, default = 10, help = 'Cost in $ per Gbps for transceivers')
    parser.add('--transceiver_amortization_years', type = float, default = 3, help = 'Amortization years for transceivers')
    parser.add('--fiber_cost', type = float, default = 3600, help = 'Cost in $ per year per fiber') 
    parser.add('--n_fibers_per_fiberduct', type = float, default = 200, help = 'Number of fibers built together')

    args = parser.parse_args()

    return args

def write_config_file(args, path='config.cfg'):
    with open(path, 'w') as f:
        for flag in sorted(args.__dict__):
            f.write(f'{flag} = {args.__dict__[flag]}\n')
