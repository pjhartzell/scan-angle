import time
import math
import numpy as np
import pdal
import os
t0 = time.time()
os.chdir('D:\Creeping Fault')
# Import lidar xyz and time to numpy arrays, sort by time
json_string = '''[
    {
        "type":"readers.las", 
        "filename":"final - VQ-580 - 170822_192752_VQ-580 - originalpoints_timesorted.las",
        "count":100000
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
ScanInterval=0.025
TimeInterval= 1
break_true = False
while count < len(t):

    while t[j] < t[count]+ScanInterval:
        j += 1
        #print(j)
        if j == len(t):
            break_true = True
            break
    if break_true:
        break

    Sample = np.array([t[count:j], x[count:j], y[count:j], z[count:j], ScanAngle[count:j]]).T       # Sample of points
    #input("Press Enter to continue...")
    if -8 in Sample[:,4] and 8 in Sample[:,4]:
        #if len(Sample) < 80:
        #    j += 1
        #    continue
        MinAng = np.argpartition(Sample[:, 4],20)       # Get index for 20 smallest scan angles
        MaxAng = np.argpartition(Sample[:, 4],-20)      # Get index for 20 largest scan angles

        n = Sample[MinAng[:20], :]                      # 20 minimum scan angles pulses
        p = Sample[MaxAng[-20:], :]                     # 20 maximum scan angles pulses

        # Trajectory from Scan Angle
        nAVG=[]                                         # Negative pulse list
        pAVG=[]                                         # Positive pulse list

        for m in range(len(n)):
            BaseLength = math.sqrt((p[m,1] - n[m,1])**2
                                 + (p[m,2] - n[m,2])**2
                                 + (p[m,3] - n[m,3])**2)        # Length between selected points
            Gamma = math.radians(abs(n[m,4]) + abs(p[m,4]))
            N_AngRightTri = math.radians(90 - abs(n[m,4]))
            P_AngRightTri = math.radians(90 - abs(p[m,4]))

            # Compute the true interior angles of the triangle
            BaseHzLength = math.sqrt((n[m,1] - p[m,1])**2
                                   + (n[m,2] - p[m,2])**2)
            N_Ang = N_AngRightTri - math.atan((p[m,3] - n[m,3]) / BaseHzLength)
            P_Ang = P_AngRightTri - math.atan((n[m,3] - p[m,3]) / BaseHzLength)

            # Use the true angles in the Law of Sines for the side lengths
            N_Side = math.sin(P_Ang) * BaseLength / math.sin(Gamma)     # Range to point n
            P_Side = math.sin(N_Ang) * BaseLength / math.sin(Gamma)     # Range to point p

            # I changed the order of parameters passed to atan2 (pass y first, then x)
            N_theta = math.atan2(p[m,2] - n[m,2], p[m,1] - n[m,1])                       # Ground angle between points
            P_theta = math.atan2(n[m,2] - p[m,2], n[m,1] - p[m,1])                       # Ground angle between points

            # Note that the results of the Negative and Positive side solutions are now Identical, so storing both sides can be eliminated
            # Note that the true interior angles of the triangle are Not used here
            # I reversed some of the math for the x and y trajectory coordinates to match the sketch (this is a result of correcting the atan2 parameter order)
            nAVG.append([(n[m,0],
                          n[m,1] + N_Side * math.cos(N_AngRightTri) * math.cos(N_theta),
                          n[m,2] + N_Side * math.cos(N_AngRightTri) * math.sin(N_theta),
                          n[m,3] + N_Side * math.sin(N_AngRightTri))])                        # Append Trajectory for single negative pulse
            pAVG.append([(p[m,0], 
                          p[m,1] + P_Side * math.cos(P_AngRightTri) * math.cos(P_theta),
                          p[m,2] + P_Side * math.cos(P_AngRightTri) * math.sin(P_theta),
                          p[m,3] + P_Side * math.sin(P_AngRightTri))])                        # Append Trajectory for single positive pulse

        nAVG=np.sum(nAVG,axis=0)/len(n)         # Average of Trajectories from negative pulses within single scan cycle
        pAVG=np.sum(pAVG,axis=0)/len(p)         # Average of Trajectories from positive pulses within single scan cycle
        TrajPosSA.append(pAVG)                  # Append positive averaged trajectory to list
        TrajNegSA.append(nAVG)                  # Append negative averaged trajectory to list
        #print(len(TrajPosSA))
        count = j                               # Set absolute to current pulse
        j += 1                                  # Cycle to next pulse
        value=0                                 # Reset selection value


    #else :
     #   count=j
        #input("Press Enter to continue...")
      #  continue

    while t[j] < t[count] + TimeInterval:
        j += 1
        # print(j)
        if j == len(t):
            break_true = True
            break
    if break_true:
        break
    count = j
    j += 1

AVG = ((np.array(TrajNegSA) + np.array(TrajPosSA)) / 2)     # Average negative and positive trajectory solutions
AVG = np.reshape(AVG, (AVG.shape[0], 4))

np.savetxt('TrajScanAngle_CA_2752_V4_again.csv', AVG, delimiter=',')       # Save CSV file of Trajectory. FORMAT NAME
t1 = time.time()
print("Processing took {} seconds".format(t1-t0))