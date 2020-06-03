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


def sweep_indices(a, j):
    # Given an array of scan angles that are ordered (ascending) in time, detect
    # change from increasing to decreasing scan angle, or vice versa. Returns
    # indices into the passed array at the approximate scan angle direction
    # change locations. The change locations are approximate due to a smoothing
    # filter that is applied to the scan angles to make the method resistant to
    # temporal "jitter" in the scan angle data.

    # mitigate scan angle "jitter" caused by platform dynamics
    filter_size = j*2 + 1
    a = np.convolve(a, np.ones(filter_size), 'valid') / filter_size
    a = np.insert(a, 0, a[0]*np.ones(j))
    a = np.append(a, a[-1]*np.ones(j))
    a = np.round(a)

    d = np.diff(a)
    d[d>0] = 1
    d[d<0] = -1

    idx = np.where(d!=0)[0]
    d_subset = d[idx]

    d2 = np.diff(d_subset)
    idx2 = np.where(d2!=0)[0]

    return idx[idx2+1] + 1


def point_pair_indices(a, min_delta_a):
    # We are interested in the maximum and minimum scan angles with highly
    # populated bins. By LAS specification, scan angles should be in [-90,90].
    hist, _ = np.histogram(a, bins=181, range=(-90.5,90.5))
    dense_bins = np.argwhere(hist >= np.median(hist[hist>0]))
    min_dense_a = dense_bins[0] - 90
    max_dense_a = dense_bins[-1] - 90

    # Check for sufficient scan angle geometry
    if (max_dense_a - min_dense_a) >= min_delta_a:
        low_idx = np.argwhere(a == min_dense_a)
        high_idx = np.argwhere(a == max_dense_a)
        # Check that we have enough points in the bins
        if len(low_idx > 1) and len(high_idx > 1):
            # First and last points in the bins gives us maximum, opposite error in
            # scan angle
            low_idx = np.squeeze(low_idx[[0,-1]])
            high_idx = np.squeeze(high_idx[[-1,0]])
        else:
            low_idx = []
            high_idx = []
    else:
        low_idx = []
        high_idx = []

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
