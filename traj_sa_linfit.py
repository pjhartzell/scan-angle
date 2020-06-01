import time
import numpy as np
import matplotlib.pyplot as plt
from traj_sa_funcs import read_las, swath_indices, traj_xyz_mean, save_traj, a_linfit


filename = "F:/Sitka/helipod/autoclass - Scanner 1 - 160503_011252_VQ480i - originalpoints_timesorted.las"
# filename = "F:/UH/C2_L2_sorted.las"
count = 200000
min_delta_a = 15  # degrees
num_ests = 400
jitter = 8
discard = 5

txyza = read_las(filename, count=0)

start_time = time.time()

indices = swath_indices(txyza[:,4], jitter)

i = 1
traj_txyz = []
for idx1, idx2 in zip(indices[:-1], indices[1:]):

    # Swath data
    a = txyza[idx1:idx2,4]
    xyz = txyza[idx1:idx2,1:4]
    t = txyza[idx1:idx2,0]

    # Check for sufficient geometry
    if (np.max(a) - np.min(a)) > (min_delta_a + 2*discard):

        # Discard extreme angle data
        keep = np.logical_and(a >= (np.min(a)+discard), a <= (np.max(a)-discard))
        a = a[keep]
        xyz = xyz[keep,:]
        t = t[keep]

        # Check for sufficient number of points
        if a.shape[0] > (2*num_ests):

            a_fit, m, b = a_linfit(t, a)

            sort_idx = np.argsort(a_fit)
            low_idx = sort_idx[0:num_ests]
            high_idx = sort_idx[-num_ests:]

            a_low = a_fit[low_idx]
            a_high = a_fit[high_idx]

            # Guard against parallel rays
            if not np.isin(a_low, a_high).any():

                x_mean, y_mean, z_mean = traj_xyz_mean(
                    xyz[low_idx,:],
                    xyz[high_idx,:],
                    a_low,
                    a_high)
                t_mean = np.mean(t[np.hstack((low_idx, high_idx))])

                traj_txyz.append([t_mean, x_mean, y_mean, z_mean])

                # if i >= 200:
                #     print((z1+z2)/2)
                    # print(m, b)
                    # plt.plot(t, a,'.', t, a_fit, '.')
                    # plt.show()
                #     # input("hit a key")

                i += 1


# txyz = np.asarray(traj_txyz)
# t = txyz[:,0]
# x = txyz[:,1]
# y = txyz[:,2]
# z = txyz[:,3]
# filter_size = 200
# x = np.convolve(x, np.ones(filter_size), 'same') / filter_size
# y = np.convolve(y, np.ones(filter_size), 'same') / filter_size
# z = np.convolve(z, np.ones(filter_size), 'same') / filter_size
# traj_txyz = np.vstack((t,x,y,z)).T

elapsed_time = time.time() - start_time
print(elapsed_time)

save_traj(filename, traj_txyz)

np.set_printoptions(threshold=1000)