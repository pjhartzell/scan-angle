import time
import numpy as np
import os
from traj_sa_funcs import read_las, swath_indices, traj_xyz
import matplotlib.pyplot as plt


# filename = "G:/Sitka/helipod/autoclass - Scanner 1 - 160503_011252_VQ480i - originalpoints_timesorted.las"
filename = "G:/UH/C2_L2_sorted.las"
count = 20000000
min_delta = 15  # degrees
min_pnts = 10
jitter = 8
# rate = 10  # Hz

txyza = read_las(filename, count)

start_time = time.time()

indices = swath_indices(txyza[:,4], jitter)

traj_txyz = []
# print(indices[0:20])
np.set_printoptions(threshold=5000)
# print(txyza[indices[0]:indices[0]+499,4])
# np.set_printoptions(threshold=1000)
# exit()
i = 1
for idx1, idx2 in zip(indices[:-1], indices[1:]):
    # print(idx1, idx2)

    # Scan angles from single sweep
    a = txyza[idx1:idx2,4]

    low_idx = (a == (np.min(a)+1))
    high_idx = (a == (np.max(a)-1))

    low_a = a[low_idx]
    high_a = a[high_idx]

    # print(a)
    # print("low_a={}".format(low_a))
    # print("high_a={}".format(high_a))

    # input("hit a key...")

    if (low_a.shape[0] >= min_pnts) and (high_a.shape[0] > min_pnts):  # Sufficient points
        if (high_a[0] - low_a[0]) > min_delta:  # Sufficient geometry

            xyz = txyza[idx1:idx2,1:4]
            low_xyz = xyz[low_idx,:]
            high_xyz = xyz[high_idx,:]
            t = txyza[idx1:idx2,0]
            low_t = t[low_idx]
            high_t = t[high_idx]


            x1, y1, z1 = traj_xyz(low_xyz[0,:], high_xyz[-1,:], low_a[0], high_a[0])
            t1 = (low_t[0] + high_t[-1]) / 2
            x2, y2, z2 = traj_xyz(low_xyz[-1,:], high_xyz[0,:], low_a[0], high_a[0])
            t2 = (low_t[-1] + high_t[0]) / 2

            traj_txyz.append([(t1+t2)/2, (x1+x2)/2, (y1+y2)/2, (z1+z2)/2])
            
            # print('saved record {}'.format(i))
            # print(x1, y1, z1)
            # print(x2, y2, z2)
            # # input("Hit a key...")
            # if i == 7:
            #     input("press enter...")
            # i += 1


elapsed_time = time.time() - start_time
print(elapsed_time)

# np.savetxt("F:/Sitka/helipod/est_252.txt", traj_txyz, fmt="%0.6f,%0.3f,%0.3f,%0.3f")
np.savetxt("G:/UH/est_252.txt", traj_txyz, fmt="%0.6f,%0.3f,%0.3f,%0.3f")