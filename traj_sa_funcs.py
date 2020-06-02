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


def point_pair_indices(a, min_delta_a):
    sort_idx = np.argsort(a)
    a_sorted = a[sort_idx]

    delta_a = a_sorted[::-1] - a_sorted[0:]
    threshold_idx = len(delta_a) - np.searchsorted(delta_a[::-1], min_delta_a)

    low_idx = sort_idx[0:threshold_idx]
    high_idx = sort_idx[:-threshold_idx-1:-1]

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
