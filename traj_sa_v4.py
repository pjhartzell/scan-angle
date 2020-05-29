import time
import numpy as np
import os
from traj_sa_funcs import read_las, time_block_indices, traj_xyz_mean
import matplotlib.pyplot as plt


filename = "F:/Sitka/helipod/autoclass - Scanner 1 - 160503_011252_VQ480i - originalpoints_timesorted.las"
# filename = "G:/UH/C2_L2_sorted.las"
count = 2000000
min_delta_a = 15  # degrees
num_intersections = 100
delta_t = 0.1

txyza = read_las(filename, count=0)

start_time = time.time()

indices = time_block_indices(txyza[:,0], delta_t)

# np.set_printoptions(threshold=5000)
# print(txyza[indices[0]:indices[0]+499,4])
# exit()

i = 1
traj_txyz = []
for idx1, idx2 in zip(indices[:-1], indices[1:]):

    a = txyza[idx1:idx2,4]

    # print(a)
    # print(idx1, idx2)
    # input("Hit a key...")

    if (np.max(a) - np.min(a)) >= min_delta_a:  # Sufficient geometry

        if a.shape[0] > (2*num_intersections):  # Sufficient number of points

            sort_idx = np.argsort(a)
            low_idx = sort_idx[0:num_intersections]
            # high_idx = sort_idx[:-(num_intersections+1):-1]
            high_idx = sort_idx[-num_intersections:]

            a_low = a[low_idx]
            a_high = a[high_idx]

            if not np.isin(a_low, a_high).any():  # Guard against parallel rays

                xyz = txyza[idx1:idx2,1:4]
                t = txyza[idx1:idx2,0]

                x_mean, y_mean, z_mean = traj_xyz_mean(
                    xyz[low_idx,:],
                    xyz[high_idx,:],
                    a_low,
                    a_high)
                t_mean = np.mean(t[np.hstack((low_idx, high_idx))])

                traj_txyz.append([t_mean, x_mean, y_mean, z_mean])

                # print('saved record {}'.format(i))
                # print(x_mean, y_mean, z_mean, t_mean)
                # input("Hit a key...")
                # i += 1
                # print(i)


elapsed_time = time.time() - start_time
print(elapsed_time)

np.savetxt("F:/Sitka/helipod/est_traj.txt", traj_txyz, fmt="%0.6f,%0.3f,%0.3f,%0.3f")
# np.savetxt("G:/UH/est_252.txt", traj_txyz, fmt="%0.6f,%0.3f,%0.3f,%0.3f")

np.set_printoptions(threshold=1000)