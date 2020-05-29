import numpy as np
from traj_sa_funcs import read_las, time_block_indices, traj_xyz_mean, save_traj


# ------------------------------------------------------------------------------
# Sensor trajectory estimation from LAS scan angle rank field. Similar to
# Gatziolis & McGaughey's multi-return method, the data is split into time
# blocks and a single trajectory point estimated for each time block. 
#
# Note that the data must be sorted by time. This can be added to the pdal
# pipeline in the read_las function if desired.

# USER INPUT
filename = "F:/UH/C2_L2_sorted.las"
delta_t = 0.1       # Time block duration (seconds)
min_delta_a = 15    # Minimum scan angle range within a time block (degrees)
num_ests = 6400      # Number of trajectory estimates to average in a time block
# ------------------------------------------------------------------------------


# Get time, x, y, z, and scan angle rank from timesorted LAS file
txyza = read_las(filename)

# Time block start locations
indices = time_block_indices(txyza[:,0], delta_t)

traj_txyz = []

# Compute a mean trajectory location for each time block
for idx1, idx2 in zip(indices[:-1], indices[1:]):

    a = txyza[idx1:idx2,4]

    # Check for sufficient geometry
    if (np.max(a) - np.min(a)) >= min_delta_a:

        # Check for sufficient number of points
        if a.shape[0] > (2*num_ests):

            sort_idx = np.argsort(a)
            low_idx = sort_idx[0:num_ests]
            # high_idx = sort_idx[-num_ests:]
            high_idx = sort_idx[:-(num_ests+1):-1]

            a_low = a[low_idx]
            a_high = a[high_idx]

            # Guard against parallel rays
            if not np.isin(a_low, a_high).any():  

                xyz = txyza[idx1:idx2,1:4]
                t = txyza[idx1:idx2,0]

                x_mean, y_mean, z_mean = traj_xyz_mean(
                    xyz[low_idx,:],
                    xyz[high_idx,:],
                    a_low,
                    a_high)
                t_mean = np.mean(t[np.hstack((low_idx, high_idx))])

                traj_txyz.append([t_mean, x_mean, y_mean, z_mean])

save_traj(filename, traj_txyz)

