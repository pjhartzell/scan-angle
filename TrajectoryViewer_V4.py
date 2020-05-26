import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
import scipy
from scipy.signal import savgol_filter
from scipy.interpolate import make_lsq_spline

actual_252 = 'G:/Sitka/helipod/apps_final_ATLANS-20160503_NAD83-UTM8N-Geoid12B.txt'
# actual_252 = 'G:/Sitka/helipod/trajectory_252.txt'
est_252 = 'G:/Sitka/helipod/est_252.txt'

ActualTrajectory = np.loadtxt(actual_252, delimiter=',', skiprows=1)
# ActualTrajectory = np.loadtxt(actual_252, delimiter=' ')
ScanAngleTrajectory = np.loadtxt(est_252, delimiter=',')

# Trim actual trajectory to estimated time bounds
min_t = np.min(ScanAngleTrajectory[:,0])
max_t = np.max(ScanAngleTrajectory[:,0])
mask = np.logical_and(ActualTrajectory[:,0] >= min_t, ActualTrajectory[:,0] <= max_t)
ActualTrajectory = ActualTrajectory[mask,:]

# ScanAngleTrajSmoothZ= savgol_filter(ScanAngleTrajectory[:,3],41,3)
# ScanAngleTrajSmoothX= savgol_filter(ScanAngleTrajectory[:,1],13,3)
# ScanAngleTrajSmoothY= savgol_filter(ScanAngleTrajectory[:,2],13,3)
TrajInterpZ= np.interp(ScanAngleTrajectory[:,0],ActualTrajectory[:,0], ActualTrajectory[:,3])
TrajInterpX= np.interp(ScanAngleTrajectory[:,0],ActualTrajectory[:,0], ActualTrajectory[:,2])
TrajInterpY= np.interp(ScanAngleTrajectory[:,0],ActualTrajectory[:,0], ActualTrajectory[:,1])
Area= 'Sitka'
flight= '252'
sample=0.025
every=1

## Height with Difference, Roll and Pitch
fig,axs =plt.subplots(4)
plt.subplots_adjust(hspace=0.5)
axs[0].plot(ActualTrajectory[:,0], ActualTrajectory[:,3],ScanAngleTrajectory[:,0],ScanAngleTrajectory[:,3])
axs[0].legend(('Actual Trajectory','Scan Angle Trajectory'))
axs[0].set(xlabel='Time (s)', ylabel='Height (m)',title='{} {} Trajectory Height, {} seconds every {} seconds '.format(Area,flight,sample,every))
axs[0].grid(True)
axs[1].plot(ScanAngleTrajectory[:,0],TrajInterpZ-ScanAngleTrajectory[:,3])
axs[1].legend(('Height Difference'))
axs[1].set(xlabel='Time (s)', ylabel='Height Difference(m)',title='Actual Trajectory and ScanAngle Trajectory Height Difference')
axs[1].grid(True)
axs[2].plot(ActualTrajectory[:,0],ActualTrajectory[:,4],'g-',ActualTrajectory[:,0],ActualTrajectory[:,5],'c-')
axs[2].legend(('Roll','Pitch'))
axs[2].set(xlabel='Time (s)', ylabel='Degrees',title='Trajectory Rotation')
axs[2].grid(True)
axs[3].plot(ActualTrajectory[:,0],ActualTrajectory[:,6],'g-')
axs[3].legend(('Heading'))
axs[3].set(xlabel='Time (s)', ylabel='Degrees',title='Trajectory Heading')
axs[3].grid(True)
figure = plt.gcf()
figure.set_size_inches(32, 18)
plt.show()
# plt.savefig("{}_{}_TrajectoryHeightDifference_{}_seconds_every_{} seconds.png".format(Area,flight,sample,every),bbox_inches='tight')

## X and Y Trajectory Difference with Roll and Pitch
fig,axs =plt.subplots(4)
plt.subplots_adjust(hspace=0.5)
axs[0].plot(ScanAngleTrajectory[:,0],TrajInterpX-ScanAngleTrajectory[:,1])
axs[0].legend(('X Difference'))
axs[0].set(xlabel='Time (s)', ylabel='X Difference (m)',title='{} {} Trajectory X and Y Difference, {} seconds every {} seconds'.format(Area,flight,sample,every))
axs[0].grid(True)
axs[1].plot(ScanAngleTrajectory[:,0],TrajInterpY-ScanAngleTrajectory[:,2])
axs[1].legend(('Y Difference'))
axs[1].set(xlabel='Time (s)', ylabel='Y Difference (m)')
axs[1].grid(True)
axs[2].plot(ActualTrajectory[:,0],ActualTrajectory[:,4],'g-',ActualTrajectory[:,0],ActualTrajectory[:,5],'c-')
axs[2].legend(('Roll','Pitch'))
axs[2].set(xlabel='Time (s)', ylabel='Degrees',title='Trajectory Rotation')
axs[2].grid(True)
axs[3].plot(ActualTrajectory[:,0],ActualTrajectory[:,6],'g-')
axs[3].legend(('Heading'))
axs[3].set(xlabel='Time (s)', ylabel='Degrees',title='Trajectory Heading')
axs[3].grid(True)
figure = plt.gcf()
figure.set_size_inches(32, 18)
plt.show()
# plt.savefig("{}_{}_TrajectoryXYDifference_{}_seconds_every_{}_seconds.png".format(Area,flight,sample,every),bbox_inches='tight')