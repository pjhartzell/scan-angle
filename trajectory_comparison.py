import numpy as np
import matplotlib.pyplot as plt


actual_traj_file = 'D:/OneDrive - University Of Houston/2018-10-25 - ERDC BAA/ActualWork/sri/sri_data/ak_sitka/apps_final_ATLANS-20160503_NAD83-UTM8N-Geoid12B.txt'
est_traj_file = 'D:/OneDrive - University Of Houston/2018-10-25 - ERDC BAA/ActualWork/sri/sri_data/ak_sitka/autoclass - Scanner 1 - 160503_011744_VQ480i - originalpoints_4-method2-EstimatedTrajectory.txt'

# actual_traj_file = 'F:/UH/sbet_047_IGS08-UTM15N-Ellipsoid.txt'
# est_traj_file = 'F:/UH/selective_ta5_mda15_j8.txt'

actual_traj = np.loadtxt(actual_traj_file, delimiter=',', skiprows=1)
est_traj = np.loadtxt(est_traj_file, delimiter=',', skiprows=1)

# Trim actual trajectory to time bounds of estimated trajectory
min_t = np.min(est_traj[:,0])
max_t = np.max(est_traj[:,0])
mask = np.logical_and(actual_traj[:,0] >= min_t, actual_traj[:,0] <= max_t)
actual_traj = actual_traj[mask,:]

# Interpolate actual trajectory at estimated trajectory times for comparison
actual_interp_x = np.interp(est_traj[:,0], actual_traj[:,0], actual_traj[:,2])
actual_interp_y = np.interp(est_traj[:,0], actual_traj[:,0], actual_traj[:,1])
actual_interp_z = np.interp(est_traj[:,0], actual_traj[:,0], actual_traj[:,3])

# Trajectory heights, height differences, roll/pitch/heading from actual trajectory
fig, axs =plt.subplots(4)
plt.subplots_adjust(hspace=0.5)
axs[0].plot(actual_traj[:,0], actual_traj[:,3], est_traj[:,0], est_traj[:,3])
axs[0].legend(('Actual Trajectory','Estimated Trajectory'))
axs[0].set(xlabel='Time (s)', ylabel='Height (m)', title='Trajectory Height')
axs[0].grid(True)
axs[1].plot(est_traj[:,0], actual_interp_z-est_traj[:,3])
axs[1].set(xlabel='Time (s)', ylabel='Height Difference(m)',title='Height Difference (Actual - Estimated)')
axs[1].grid(True)
axs[2].plot(actual_traj[:,0], actual_traj[:,4], 'g-', actual_traj[:,0], actual_traj[:,5], 'c-')
axs[2].legend(('Roll', 'Pitch'))
axs[2].set(xlabel='Time (s)', ylabel='Degrees', title='Actual Trajectory Roll and Pitch')
axs[2].grid(True)
axs[3].plot(actual_traj[:,0], actual_traj[:,6], 'g-')
axs[3].legend(('Actual Trajectory Heading'))
axs[3].set(xlabel='Time (s)', ylabel='Degrees', title='Actual Trajectory Heading')
axs[3].grid(True)
figure = plt.gcf()
figure.set_size_inches(18,9)
plt.show()
# plt.savefig("{}_{}_TrajectoryHeightDifference_{}_seconds_every_{} seconds.png".format(Area,flight,sample,every),bbox_inches='tight')

# Trajectory X and Y differences, roll/pitch/heading from actual trajectory
fig, axs =plt.subplots(4)
plt.subplots_adjust(hspace=0.5)
axs[0].plot(est_traj[:,0], actual_interp_x-est_traj[:,1])
axs[0].legend(('X Difference'))
axs[0].set(xlabel='Time (s)', ylabel='X Difference (m)', title='X Difference (Actual - Estimated)')
axs[0].grid(True)
axs[1].plot(est_traj[:,0], actual_interp_y-est_traj[:,2])
axs[1].legend(('Y Difference'))
axs[1].set(xlabel='Time (s)', ylabel='Y Difference (m)', title='Y Difference (Actual - Estimated)')
axs[1].grid(True)
axs[2].plot(actual_traj[:,0], actual_traj[:,4], 'g-',actual_traj[:,0], actual_traj[:,5], 'c-')
axs[2].legend(('Roll','Pitch'))
axs[2].set(xlabel='Time (s)', ylabel='Degrees', title='Actual Trajectory Roll and Pitch')
axs[2].grid(True)
axs[3].plot(actual_traj[:,0], actual_traj[:,6], 'g-')
axs[3].legend(('Heading'))
axs[3].set(xlabel='Time (s)', ylabel='Degrees', title='Actual Trajectory Heading')
axs[3].grid(True)
figure = plt.gcf()
figure.set_size_inches(18,9)
plt.show()
# plt.savefig("{}_{}_TrajectoryXYDifference_{}_seconds_every_{}_seconds.png".format(Area,flight,sample,every),bbox_inches='tight')