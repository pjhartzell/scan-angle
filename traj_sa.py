import numpy as np
from traj_sa_funcs import (
    point_pair_indices,
    read_las,
    save_traj,
    time_block_indices,
    traj_xyz_mean)

# ------------------------------------------------------------------------------
# Sensor trajectory estimation from LAS scan angle rank field. Similar to
# Gatziolis & McGaughey's multi-return method, the data is split into time
# blocks and a single trajectory point estimated for each time block. 
#
# Note that the data must be sorted by time. This can be added to the PDAL
# pipeline in the read_las function if desired.

# USER INPUT
filename = 'G:/Sitka/helipod/autoclass - Scanner 1 - 160503_011252_VQ480i - originalpoints_timesorted.las'
filename = 'G:/UH/C2_L2_sorted.las'
delta_t = 0.1       # Time block duration (seconds)
min_delta_a = 15    # Minimum scan angle difference between point pairs (degrees)
min_num_sol = 20    # Minimum number of ray intersections
trim_a = 5          # Extent of extreme scan angles to remove (degrees)
# ------------------------------------------------------------------------------


# Get time, x, y, z, and scan angle rank from timesorted LAS file
txyza = read_las(filename)

# Time block start locations
indices = time_block_indices(txyza[:,0], delta_t)

traj_txyz = []

# Compute a mean trajectory location for each time block
for idx1, idx2 in zip(indices[:-1], indices[1:]):

    # Time block data
    a = txyza[idx1:idx2,4]
    xyz = txyza[idx1:idx2,1:4]
    t = txyza[idx1:idx2,0]

    # Discard extreme scan angles
    keep = np.logical_and(a >= (np.min(a)+trim_a), a <= (np.max(a)-trim_a))
    a = a[keep]
    xyz = xyz[keep,:]
    t = t[keep]

    # Check that we still have sufficient data
    if len(a) >= (min_num_sol*2):

        # Point pairs with sufficient scan angle geometry
        low_idx, high_idx = point_pair_indices(a, min_delta_a)

        # Check that we still have sufficient data
        if len(low_idx) >= min_num_sol:

            # Mean trajectory solution in space and time
            x_mean, y_mean, z_mean = traj_xyz_mean(
                xyz[low_idx,:],
                xyz[high_idx,:],
                a[low_idx],
                a[high_idx])
            t_mean = np.mean(t[np.hstack((low_idx, high_idx))])

            traj_txyz.append([t_mean, x_mean, y_mean, z_mean])

save_traj(filename, traj_txyz)


