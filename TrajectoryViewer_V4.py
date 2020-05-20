import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
import scipy
from scipy.signal import savgol_filter
from scipy.interpolate import make_lsq_spline

os.chdir('D:\Creeping Fault')

ActualTrajectory = np.genfromtxt('trajectory_00002.txt')

ScanAngleTrajectory = np.genfromtxt('TrajScanAngle_CA_2752_V4.csv',delimiter=',')
ScanAngleTrajSmoothZ= savgol_filter(ScanAngleTrajectory[:,3],41,3)
ScanAngleTrajSmoothX= savgol_filter(ScanAngleTrajectory[:,1],13,3)
ScanAngleTrajSmoothY= savgol_filter(ScanAngleTrajectory[:,2],13,3)
TrajInterpZ= np.interp(ScanAngleTrajectory[:,0],ActualTrajectory[:,0], ActualTrajectory[:,3])
TrajInterpX= np.interp(ScanAngleTrajectory[:,0],ActualTrajectory[:,0], ActualTrajectory[:,2])
TrajInterpY= np.interp(ScanAngleTrajectory[:,0],ActualTrajectory[:,0], ActualTrajectory[:,1])
Area= 'CA'
flight= '2752'
sample=0.025
every=1

## Height with Difference, Roll and Pitch
fig,axs =plt.subplots(4)
plt.subplots_adjust(hspace=0.5)
axs[0].plot(ActualTrajectory[:,0], ActualTrajectory[:,3],ScanAngleTrajectory[:,0],ScanAngleTrajectory[:,3],ScanAngleTrajectory[:,0],ScanAngleTrajSmoothZ)
axs[0].legend(('Actual Trajectory','Scan Angle Trajectory','Scan Angle Trajectory Smoothed'))
axs[0].set(xlabel='Time (s)', ylabel='Height (m)',title='{} {} Trajectory Height, {} seconds every {} seconds '.format(Area,flight,sample,every))
axs[0].grid(True)
axs[1].plot(ScanAngleTrajectory[:,0],TrajInterpZ-ScanAngleTrajectory[:,3],ScanAngleTrajectory[:,0],TrajInterpZ-ScanAngleTrajSmoothZ)
axs[1].legend(('Height Difference','Smoothed Difference'))
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
plt.savefig("{}_{}_TrajectoryHeightDifference_{}_seconds_every_{} seconds.png".format(Area,flight,sample,every),bbox_inches='tight')

## X and Y Trajectory Difference with Roll and Pitch
fig,axs =plt.subplots(4)
plt.subplots_adjust(hspace=0.5)
axs[0].plot(ScanAngleTrajectory[:,0],TrajInterpX-ScanAngleTrajectory[:,1],ScanAngleTrajectory[:,0],TrajInterpX-ScanAngleTrajSmoothX)
axs[0].legend(('X Difference','Smoothed X Difference'))
axs[0].set(xlabel='Time (s)', ylabel='X Difference (m)',title='{} {} Trajectory X and Y Difference, {} seconds every {} seconds'.format(Area,flight,sample,every))
axs[0].grid(True)
axs[1].plot(ScanAngleTrajectory[:,0],TrajInterpY-ScanAngleTrajectory[:,2],ScanAngleTrajectory[:,0],TrajInterpY-ScanAngleTrajSmoothY)
axs[1].legend(('Y Difference','Smoothed Y Difference'))
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
plt.savefig("{}_{}_TrajectoryXYDifference_{}_seconds_every_{}_seconds.png".format(Area,flight,sample,every),bbox_inches='tight')