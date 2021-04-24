import numpy as np

def weibull(n_sample,scale=0.001, shape=0.8):
    return scale * np.random.weibull(a=shape, size=n_sample)
