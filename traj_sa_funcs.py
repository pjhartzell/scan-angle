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


def swath_indices(sa, j):
    # Given an array of scan angles that are ordered (ascending) in time, detect
    # change from increasing to decreasing scan angle, or vice versa. Returns
    # indices into the passed array at the scan angle direction change
    # locations.

    # mitigate scan angle 'jitter' caused by platform dynamics
    filter_size = j*2 + 1
    sa = np.convolve(sa, np.ones(filter_size), 'valid') / filter_size
    sa = np.insert(sa, 0, sa[0]*np.ones(j))
    sa = np.append(sa, sa[-1]*np.ones(j))
    sa = np.round(sa)

    d = np.diff(sa)
    d[d>0] = 1
    d[d<0] = -1

    idx = np.where(d!=0)[0]
    d_subset = d[idx]

    d2 = np.diff(d_subset)
    idx2 = np.where(d2!=0)[0]

    # np.set_printoptions(threshold=np.inf)
    # print(sa)
    # print(d)
    # print(idx)
    # print(d_subset)
    # print(d2)
    # print(idx2)
    # print(idx[idx2+1])
    # print(sa[idx[idx2+1]])
    # np.set_printoptions(threshold=1000)

    return idx[idx2+1] + 1
