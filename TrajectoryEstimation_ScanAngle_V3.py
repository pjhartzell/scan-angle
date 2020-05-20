import time
import math
import numpy as np
import pdal
import os
t0 = time.time()
os.chdir('D:\Research\ErrorEstimation\FlightLines')
# Import lidar xyz and time to numpy arrays, sort by time
json_string = '''[
    {
        "type":"readers.las",
        "filename":"192752_sorted.las"
    }
]'''
pipeline = pdal.Pipeline(json_string)
pipeline.validate()
pipeline.execute()
arrays = pipeline.arrays
view = arrays[0]
x = view['X']
y = view['Y']
z = view['Z']
t = view['GpsTime']
ScanAngle = view['ScanAngleRank']
t1 = time.time()
print("Reading of points took {} seconds".format(t1-t0))

TrajNegSA = [] # List for Trajectory calculated from negative scan angle
TrajPosSA = [] # List for Trajectory calculated from positive scan angle

count = 0               # absolute pulse position
j = 0                   # iterative value of laser pulses
t0 = time.time()
#while count < len(t):

value=0                 # value parameter for selective interpolation
while count < len(t):


    if j == len(ScanAngle):         # Check iteration doesn't exceed sample length
        break
    else:
        while ScanAngle[j] >= 0:        # iterate through positive scan angles
            j+=1
    if j == len(ScanAngle):         # Check iteration doesn't exceed sample length
        break
    else:
        while ScanAngle[j] < 0:         # iterate through negative scan angles
            j += 1


    if value == 100 :               # Sample every 100th scan cycle

        Sample = np.array([t[count:j], x[count:j], y[count:j], z[count:j], ScanAngle[count:j]]).T       # Sample scan cycle

        MinAng = np.argpartition(Sample[:, 4],20)       # Get index for 20 smallest scan angles
        MaxAng = np.argpartition(Sample[:, 4],-20)      # Get index for 20 largest scan angles

        n = Sample[MinAng[:20], :]                      # 20 minimum scan angles pulses
        p = Sample[MaxAng[-20:], :]                     # 20 maximum scan angles pulses
#
#        # Trajectory from Scan Angle
        nAVG=[]                                         # Negative pulse list
        pAVG=[]                                         # Positive pulse list
#
        for m in range(len(n)):
            BaseLength = math.sqrt(
                (p[m,1] - n[m,1]) ** 2 + (p[m,2] - n[m,2]) ** 2 + (p[m,3] - n[m,3]) ** 2)   # Length between selected points
            Gamma = (abs(p[m,4]) + abs(n[m,4]))                                             # Total scan angle
            NegAng = math.radians(90 - abs(n[m,4]))                                         # Angle from N
            PosAng = math.radians(90 - abs(p[m,4]))

            NegSide = math.sin(PosAng) * BaseLength / math.sin(math.radians(Gamma))     # Range to point n
            PosSide = math.sin(NegAng) * BaseLength / math.sin(math.radians(Gamma))     # Range to point p
            Ntheta = math.atan2(p[m,1] - n[m,1], p[m,2] - n[m,2])                       # Ground angle between points
            Ptheta = math.atan2(n[m,1] - p[m,1], n[m,2] - p[m,2])                       # Ground angle between points
#
            pAVG.append([(p[m,0], p[m,1] + PosSide * math.cos(PosAng) * math.sin(Ptheta),
                           p[m,2] + PosSide * math.cos(PosAng) * math.cos(Ptheta), p[m,3] + PosSide * math.sin(PosAng))])       # Append Trajectory for single positive pulse
            nAVG.append([(n[m,0], n[m,1] + NegSide * math.cos(NegAng) * math.sin(Ntheta),
                           n[m,2] + NegSide * math.cos(NegAng) * math.cos(Ntheta), n[m,3] + NegSide * math.sin(NegAng))])       # Append Trajectory for single negative pulse
#
        nAVG=np.sum(nAVG,axis=0)/len(n)         # Average of Trajectories from negative pulses within single scan cycle
        pAVG=np.sum(pAVG,axis=0)/len(p)         # Average of Trajectories from positive pulses within single scan cycle
        TrajPosSA.append(pAVG)                  # Append positive averaged trajectory to list
        TrajNegSA.append(nAVG)                  # Append negative averaged trajectory to list
        #print(len(TrajPosSA))
        count = j                               # Set absolute to current pulse
        j += 1                                  # Cycle to next pulse
        value=0                                 # Reset selection value
    else :
        count = j                               # Set absolute to current pulse
        j += 1                                  # Cycle to next pulse
        value+=1                                # Increase selection value by 1

AVG = ((np.array(TrajNegSA) + np.array(TrajPosSA)) / 2)     # Average negative and positive trajectory solutions
AVG = np.reshape(AVG, (AVG.shape[0], 4))

np.savetxt('TrajScanAngle_192752_V3.csv', AVG, delimiter=',')       # Save CSV file of Trajectory. FORMAT NAME
t1 = time.time()
print("Processing took {} seconds".format(t1-t0))