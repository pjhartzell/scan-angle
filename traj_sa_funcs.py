import os
import json
import numpy as np
import pdal


def read_las(filename):
    json_pipe = [
        {
            "type":"readers.las", 
            "filename":filename
        }
    ]

    pipeline = pdal.Pipeline(json.dumps(json_pipe))
    pipeline.validate()
    pipeline.execute()
    arrays = pipeline.arrays
    view = arrays[0]
    x = view['X']
    y = view['Y']
    z = view['Z']
    t = view['GpsTime']
    a = view['ScanAngleRank']

    return np.vstack((t,x,y,z,a)).T


def time_block_indices(t, delta_t):
    t = t - t[0]
    start_times = np.arange(0, t[-1], delta_t)
    indices = np.searchsorted(t, start_times)

    return indices


def point_pair_indices(a, pct_pairs):
    sort_idx = np.argsort(a)

    total_num_pairs = int(len(sort_idx)/2)
    use_num_pairs = int(total_num_pairs * (pct_pairs/100))

    # Points are paired from outside in with respect to scan angle
    low_idx = sort_idx[0:use_num_pairs]
    high_idx = sort_idx[:-use_num_pairs-1:-1]

    return low_idx, high_idx


def traj_xyz_mean(L, H, alpha_l, alpha_h):
    b = np.sqrt(np.sum((H-L)**2, axis=1))
    beta_l = np.deg2rad(90 + alpha_l)
    beta_h = np.deg2rad(90 - alpha_h)
    alpha = np.deg2rad(alpha_h - alpha_l)
    gamma = beta_h - np.arcsin((L[:,2]-H[:,2]) / b)
    d = (b * np.sin(gamma)) / np.sin(alpha)
    theta = np.arctan2(H[:,1]-L[:,1], H[:,0]-L[:,0])

    x = L[:,0] + d*np.cos(beta_l)*np.cos(theta)
    y = L[:,1] + d*np.cos(beta_l)*np.sin(theta)
    z = L[:,2] + d*np.sin(beta_l)

    return np.mean(x), np.mean(y), np.mean(z)


def save_traj(in_name, traj_txyz):
    root, _ = os.path.splitext(in_name)
    out_name = root + '_EstimatedTrajectory.txt'
    np.savetxt(out_name, traj_txyz, fmt="%0.6f,%0.3f,%0.3f,%0.3f")


def traj_sa(delta_t, pct_pairs, min_num_sol, trim_a, txyza):
    # Time block start locations
    indices = time_block_indices(txyza[:,0], delta_t)

    traj_txyz = []

    # Compute a mean trajectory location for each time block
    for idx1, idx2 in zip(indices[:-1], indices[1:]):

        # Time block data
        a = txyza[idx1:idx2,4]
        xyz = txyza[idx1:idx2,1:4]
        t = txyza[idx1:idx2,0]

        # print(np.min(a))
        # print(np.max(a))

        # Discard extreme scan angles
        keep = np.logical_and(a >= (np.min(a)+trim_a), a <= (np.max(a)-trim_a))
        a = a[keep]
        xyz = xyz[keep,:]
        t = t[keep]

        # Check that we still have sufficient data
        if len(a) >= (min_num_sol*2):

            # Point pairs with sufficient scan angle geometry
            low_idx, high_idx = point_pair_indices(a, pct_pairs)

            # print(len(low_idx))

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

    return np.asarray(traj_txyz)

