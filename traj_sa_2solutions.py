import time
import numpy as np
import matplotlib.pyplot as plt
from traj_sa_funcs import read_las, sweep_indices, traj_xyz, save_traj

# ------------------------------------------------------------------------------
# Alternate sensor trajectory estimation that selects two point pairs based on
# their temporal location within two scan angle rank "bins" in a single sweep of
# the lidar mirror. By selecting point pairs from the temporal extremities of
# two common scan angle bins (one bin is comprised of scan angles close to the
# maximum scan angle in a single sweep of the lidar mirror, the other bin from
# angles close to the minimum), the average of the two point pair solutions will
# cancel most of the scan angle quantization error.

# This method works well when sensor dynamics have a minimal impact on the scan
# angle values.

# USER INPUT
filename = "G:/UH/C2_L2_sorted.las"
min_delta_a = 15  # degrees
jitter = 8
# ------------------------------------------------------------------------------


# Get time, x, y, z, and scan angle rank from timesorted LAS file
txyza = read_las(filename)

indices = sweep_indices(txyza[:,4], jitter)

traj_txyz = []

# Compute a mean trajectory location for each time block
for idx1, idx2 in zip(indices[:-1], indices[1:])

    # Sweep data
    a = txyza[idx1:idx2,4]
    xyz = txyza[idx1:idx2,1:4]
    t = txyza[idx1:idx2,0]

    # Discard extreme scan angles
    keep = np.logical_and(a >= (np.min(a)+trim_a), a <= (np.max(a)-trim_a))
    a = a[keep]
    xyz = xyz[keep,:]
    t = t[keep]

    # Check that we still have data (need at least 4 points)
    if len(a) >= 4

        # Point pair indices
        low_idx, high_idx = point_pair_indices

        # We are interested in the maximum and minimum scan angles with highly
        # populated bins
        hist, _ = np.histogram(a, bins=181, range=(-90.5,90.5))
        full_bins = np.argwhere(hist >= np.median(hist[hist>0])*1.0)
        min_full_bin_a = full_bins[0] - 90
        max_full_bin_a = full_bins[-1] - 90

        # Check that our point pairs have sufficient scan angle geometry
        if (max_full_bin_a - min_full_bin_a) >= min_delta_a:

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

save_traj(filename, traj_txyz)
