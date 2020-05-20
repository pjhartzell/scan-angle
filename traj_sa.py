import time
import numpy as np
import os
from traj_sa_funcs import read_las, swath_indices, quality_metrics, get_idx
import matplotlib.pyplot as plt


filename = "D:/Creeping Fault/final - VQ-580 - 170822_192752_VQ-580 - originalpoints_timesorted.las"
count = 10000000
min_delta = 10  # degrees
min_pnts = 5
rate = 1  # Hz

x,y,z,t,sa = read_las(filename, count)

indices = swath_indices(sa)
delta_sa, num_pnts = quality_metrics(indices, sa)

nominal_traj_times = np.arange(t[indices[0]], t[indices[-1]], 1/rate)
print(nominal_traj_times.shape)

idx = 0
for i in range(nominal_traj_times.shape[0]-1):
    t_cur = nominal_traj_times[i]
    t_next = nominal_traj_times[i+1]
    idx = get_idx(
        indices, idx,
        t, t_cur, t_next,
        delta_sa, num_pnts,
        min_delta, min_pnts)
    print("idx = {}".format(idx))






# sa_r = np.array([2,2,1,1,0,0,-1,-1,-2,-2,2,2,1,1,0,0,-1,-1,-2,-2,2,2,1,1,0,0,-1,-1,-2,-2,2,2,1,1,0,0,-1,-1,-2,-2])
# sa_o = np.array([2,2,1,1,0,0,-1,-1,-2,-2,-2,-2,-1,-1,0,0,1,1,2,2,2,2,1,1,0,0,-1,-1,-2,-2,-2,-2,-1,-1,0,0,1,1,2,2])
# sa_o = np.array([2,2,0,0,-1,-1,-2,-2,-2,-2,-1,-1,0,0,1,1,2,2,2,2,1,1,0,0,-1,-1,-2,-2,-2,-2,-1,-1,0,0,1,1,2,2])

# print(swath_indices(sa))