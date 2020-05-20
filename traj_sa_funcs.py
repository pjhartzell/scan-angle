import json
import numpy as np
import pdal


def read_las(filename, count):

    json_pipe = [
        {
            "type":"readers.las", 
            "filename":filename,
            "count":count
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
    sa = view['ScanAngleRank']

    return x, y, z, t, sa


def swath_indices(sa):
    # Given an array of scan angles that are ordered (ascending) in time, detect
    # change from increasing to decreasing scan angle, or vice versa. Returns
    # indices into the passed array at the scan angle direction change
    # locations.

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


def quality_metrics(indices, sa):

    num_indices = indices.shape[0]
    delta_sa = np.zeros((num_indices-1))
    min_pnts = np.zeros((num_indices-1))

    for i in range(num_indices - 1):
        angles = sa[indices[i]:indices[i+1]]

        min_angle = np.min(angles)
        max_angle = np.max(angles)
        delta_sa[i] = max_angle - min_angle

        num_min_angles = np.sum(angles==min_angle)
        num_max_angles = np.sum(angles==max_angle)
        min_pnts[i] = np.min([num_min_angles, num_max_angles])

    return delta_sa, min_pnts


def get_idx(indices, idx,
            t, t_cur, t_next,
            delta_sa, num_pnts,
            min_delta, min_pnts):

    # increment the swath until the first swath point time is >= the current
    # trajectory time
    while (t[indices[idx]] < t_cur):
        idx += 1

    # If swath fails the quality metrics, increment to the next swath until we
    # find a swath with good metrics or we reach the next trajectory time
    while (t[indices[idx]] < t_next) and (
            (delta_sa[idx] < min_delta) or 
            (num_pnts[idx] < min_pnts)):
        idx += 1

    # If we didn't find a good swath, return -1
    if (t[indices[idx]] > t_next):
        return -1
    else:
        return idx

