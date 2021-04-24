import os
import numpy as np
from scipy.stats import uniform

i = 0
for demand in sorted(os.listdir('topology/my_B4/demand'))[0:10]:
    #print(demand[7:10])

    for j in range(10):
        os.mkdir(f'topology/my_B4/demand/{i:03d}')
        d = np.loadtxt(f'topology/my_B4/demand/demand_{demand[7:10]}.demand')
        ds = [d]
        for k in range(9):
            scaler = uniform(loc = 1.0, scale = 1.0).rvs(d.shape)
            d = scaler*d
            ds.append(d)

        for k, d in enumerate(ds):
            np.savetxt(f'topology/my_B4/demand/{i:03d}/{k:03d}.demand', d)

        i += 1
