import numpy as np
from traj_sa_funcs import (
    point_pair_indices,
    read_las,
    save_traj,
    sweep_indices,
    traj_xyz_mean)

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
filename = "F:/UH/C2_L2_sorted.las"
trim_a = 5          # Extent of extreme scan angles to remove (deg)
min_delta_a = 15    # Minimum scan angle difference between point pairs (deg)
jitter = 8          # Half-size of box filter applied to scan angles when 
                    # identifying scan sweeps
# ------------------------------------------------------------------------------


# Get time, x, y, z, and scan angle rank from timesorted LAS file
txyza = read_las(filename)

# Scan sweep start locations
indices = sweep_indices(txyza[:,4], jitter)

traj_txyz = []

# Compute a mean trajectory location for each scan sweep
for idx1, idx2 in zip(indices[:-1], indices[1:]):

    # Sweep data
    a = txyza[idx1:idx2,4]
    xyz = txyza[idx1:idx2,1:4]
    t = txyza[idx1:idx2,0]

    # Discard extreme scan angles
    keep = np.logical_and(a >= (np.min(a)+trim_a), a <= (np.max(a)-trim_a))
    a = a[keep]
    xyz = xyz[keep,:]
    t = t[keep]

    # Check that we still have sufficient data (need at least 4 points)
    if len(a) >= 4:

        # Point pair indices with sufficient scan angle geometry
        low_idx, high_idx = point_pair_indices(a, min_delta_a)

        # Check that we still have sufficient data
        if len(low_idx == 2) and len(high_idx == 2):

            # Mean trajectory solution in space and time
            x_mean, y_mean, z_mean = traj_xyz_mean(
                xyz[low_idx,:],
                xyz[high_idx,:],
                a[low_idx],
                a[high_idx])
            t_mean = np.mean(t[np.hstack((low_idx, high_idx))])

            traj_txyz.append([t_mean, x_mean, y_mean, z_mean])

save_traj(filename, traj_txyz)
