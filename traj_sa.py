import time
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
# filename = "F:/UH/C2_L2_sorted.las"
filename = "F:/Sitka/helipod/autoclass - Scanner 1 - 160503_011252_VQ480i - originalpoints_timesorted.las"
delta_t = 0.1       # Time block duration (seconds)
min_delta_a = 15    # Minimum scan angle range within a time block (degrees)
num_ests = 100      # Number of trajectory estimates to average in a time block
# ------------------------------------------------------------------------------


# Get time, x, y, z, and scan angle rank from timesorted LAS file
txyza = read_las(filename)

start_time = time.time()

# Time block start locations
indices = time_block_indices(txyza[:,0], delta_t)

traj_txyz = []

# Compute a mean trajectory location for each time block
for idx1, idx2 in zip(indices[:-1], indices[1:]):

    a = txyza[idx1:idx2,4]

    # Max and min scan angles introduce uncompensated systematic error
    a_max = np.max(a) - 1
    a_min = np.min(a) + 1

    # Check for sufficient geometry
    if (a_max - a_min) >= min_delta_a:

        keep = np.logical_and(a >= a_min, a <= a_max)
        a = a[keep]

        # Check for sufficient number of points
        if len(a) > (2*num_ests):

            sort_idx = np.argsort(a)
            low_idx = sort_idx[0:num_ests]
            high_idx = sort_idx[-num_ests:]

            a_low = a[low_idx]
            a_high = a[high_idx]

            # Guard against parallel rays
            if not np.isin(a_low, a_high).any():  

                xyz = txyza[idx1:idx2,1:4]
                xyz = xyz[keep,:]
                xyz_low = xyz[low_idx,:]
                xyz_high = xyz[high_idx,:]

                t = txyza[idx1:idx2,0]
                t = t[keep]
                t_low = t[low_idx]
                t_high = t[high_idx]

                # randomize the data
                p_low = np.random.permutation(num_ests)
                p_high = np.random.permutation(num_ests)
                a_low = a_low[p_low]
                a_high = a_high[p_high]
                xyz_low = xyz_low[p_low,:]
                xyz_high = xyz_high[p_high,:]
                t_low = t_low[p_low]
                t_high = t_high[p_high]

                x_mean, y_mean, z_mean = traj_xyz_mean(
                    xyz_low,
                    xyz_high,
                    a_low,
                    a_high)
                t_mean = np.mean(np.hstack((t_low, t_high)))

                traj_txyz.append([t_mean, x_mean, y_mean, z_mean])

end_time = time.time()
print("Time = {}".format(end_time-start_time))

save_traj(filename, traj_txyz)

