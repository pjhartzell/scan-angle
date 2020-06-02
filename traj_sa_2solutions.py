import time
import numpy as np
import matplotlib.pyplot as plt
from traj_sa_funcs import read_las, swath_indices, traj_xyz, save_traj


# filename = "F:/Sitka/helipod/autoclass - Scanner 1 - 160503_011252_VQ480i - originalpoints_timesorted.las"
filename = "G:/UH/C2_L2_sorted.las"
count = 200000
min_delta_a = 15  # degrees
# min_bin_pnts = 100
jitter = 8

txyza = read_las(filename, count=0)

start_time = time.time()

indices = swath_indices(txyza[:,4], jitter)

# np.set_printoptions(threshold=5000)
# print(txyza[indices[0]:indices[0]+499,4])
# exit()

i = 1
traj_txyz = []
for idx1, idx2 in zip(indices[:-1], indices[1:]):
    # print(idx1, idx2)

    # Swath data
    a = txyza[idx1:idx2,4]
    xyz = txyza[idx1:idx2,1:4]
    t = txyza[idx1:idx2,0]

    # Max and min scan angles introduce uncompensated systematic error
    keep = np.logical_and(a > (np.min(a)+4), a < (np.max(a)-4))
    a = a[keep]
    xyz = xyz[keep,:]
    t = t[keep]

    if a.any():

        # We are interested in the maximum and minimum scan angles with highly populated bins
        hist, _ = np.histogram(a, bins=181, range=(-90.5,90.5))
        # print(np.max(hist), np.max(hist)*0.8, np.median(hist[hist>0]), np.median(hist[hist>0])*0.9)
        full_bins = np.argwhere(hist >= np.median(hist[hist>0])*1.0)
        min_full_bin_a = full_bins[0] - 90
        max_full_bin_a = full_bins[-1] - 90

        # print(hist)
        # print(min_full_bin_a, max_full_bin_a)
        # input('hit a key...')

        if (max_full_bin_a - min_full_bin_a) >= min_delta_a:  # Sufficient geometry

            low_idx = (a == min_full_bin_a)
            high_idx = (a == max_full_bin_a)

            # low_a = a[low_idx]
            # high_a = a[high_idx]
            low_xyz = xyz[low_idx,:]
            high_xyz = xyz[high_idx,:]
            low_t = t[low_idx]
            high_t = t[high_idx]

            x1, y1, z1 = traj_xyz(low_xyz[0,:], high_xyz[-1,:], min_full_bin_a[0], max_full_bin_a[0])
            t1 = (low_t[0] + high_t[-1]) / 2
            x2, y2, z2 = traj_xyz(low_xyz[-1,:], high_xyz[0,:], min_full_bin_a[0], max_full_bin_a[0])
            t2 = (low_t[-1] + high_t[0]) / 2

            traj_txyz.append([(t1+t2)/2, (x1+x2)/2, (y1+y2)/2, (z1+z2)/2])

            # if i >= 430:

            #     print(hist)
            #     print(np.median(hist[hist>0]), np.median(hist[hist>0])*0.9)
            #     print((z1+z2)/2)
            #     plt.plot(t, a,'.')
            #     plt.show()
                # input("hit a key")

            # if (z1+z2)/2 < 525:
            #     print("i={}".format(i))
            #     exit()

            

            # print('saved record {}'.format(i))
            # print(x_mean, y_mean, z_mean, t_mean)
            # input("Hit a key...")
            i += 1
            # print(i)

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