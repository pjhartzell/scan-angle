import numpy as np
from traj_sa_funcs import read_las, save_traj, traj_sa
import matplotlib.pyplot as plt
import time
import os


# Data
# lasfile = 'F:/UH/C2_L2_sorted.las'
lasfile = 'F:/Sitka/helipod/autoclass - Scanner 1 - 160503_011252_VQ480i - originalpoints_timesorted.las'
txyza = read_las(lasfile)

# actual_traj_file = 'F:/UH/sbet_047_IGS08-UTM15N-Ellipsoid.txt'
actual_traj_file = 'F:/Sitka/helipod/apps_final_ATLANS-20160503_NAD83-UTM8N-Geoid12B.txt'
actual_traj = np.loadtxt(actual_traj_file, delimiter=',', skiprows=1)

# Variables
delta_t = 0.1
# min_delta_a = np.array([1,2,4,6,8,10,15,20,25,30,35,40,42,44,46])
min_delta_a = 25
min_num_sol = 20
# trim_a = 5
trim_a = np.array([0,1,2,3,4,5,6,7,8,9,10])

# Computations
mean_offset = []
roughness = []
for ta in trim_a:
# for mda in min_delta_a:

    # Estimated Trajectory
    start_time = time.time()
    traj_txyz = traj_sa(delta_t, min_delta_a, min_num_sol, ta, txyza)
    # traj_txyz = traj_sa(delta_t, mda, min_num_sol, trim_a, txyza)
    print("Iteration time = {}".format(time.time() - start_time))

    # Offset and Roughness
    # actual_interp_x = np.interp(traj_txyz[:,0], actual_traj[:,0], actual_traj[:,2])
    # actual_interp_y = np.interp(traj_txyz[:,0], actual_traj[:,0], actual_traj[:,1])
    actual_interp_z = np.interp(traj_txyz[:,0], actual_traj[:,0], actual_traj[:,3])

    dz = actual_interp_z - traj_txyz[:,3]
    mean_offset.append(np.mean(dz))
    roughness.append(np.std(dz - np.mean(dz)))

    # # Save estimated trajectory
    # root, _ = os.path.splitext(lasfile)
    # out_name = root + '_dt01_mda' + str(mda) + '_mns' + str(min_num_sol) + '_ta' + str(trim_a) + '.txt'
    # np.savetxt(out_name, traj_txyz, fmt="%0.6f,%0.3f,%0.3f,%0.3f")

# Show results
# print(mean_offset)
# print(roughness)

# fig, (ax1, ax2) = plt.subplots(1,2)
# ax1.plot(min_delta_a, mean_offset, '.')
# ax1.set_title('Mean Offset')
# ax1.set_xlabel('min_delta_a (degrees)')
# ax1.set_ylabel('Z Offset (m)')
# ax2.plot(min_delta_a, roughness, '.')
# ax2.set_title('Roughness (Demeaned Std.)')
# ax2.set_xlabel('min_delta_a (degrees)')
# ax2.set_ylabel('Std. (+/-m)')
# plt.show()

fig, (ax1, ax2) = plt.subplots(1,2)
ax1.plot(trim_a, mean_offset, '.')
ax1.set_title('Mean Offset')
ax1.set_xlabel('trim_a (degrees)')
ax1.set_ylabel('Z Offset (m)')
ax2.plot(trim_a, roughness, '.')
ax2.set_title('Roughness (Demeaned Std.)')
ax2.set_xlabel('min_delta_a (degrees)')
ax2.set_ylabel('Std. (+/-m)')
plt.show()






