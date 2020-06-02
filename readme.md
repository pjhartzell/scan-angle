# Airborne lidar sensor trajectory estimation from scan angle

Given point cloud data sorted by time, estimates of trajectory time and location (XYZ)
are generated from pairs of intersecting rays. For a given point pair (chosen to approximately maximize the difference between their scan angles), a pair of rays originating at the point XYZ locations are formed. The vertical ray directions are defined by each point's scan angle. Horizontally, the rays are directed at their counterpart, thereby forming a triangle. The XYZ location of the top of the triangle is an estimate of the trajectory location.

Similar to Gatziolis & McGaughey's multi-return method, the data is split into
time blocks and a single trajectory point computed for each time block. Each time block's estimated trajectory location (and time) is the average of many triangle solutions (and times) from many point pairs.

We have found that averaging hundreds to thousands of point pairs within each time block produces smoother trajectory solutions, essentially averaging out the error in the quantized (integer) scan angle values. The current method selects point pairs "from the outside in" until a minumum total angle (difference between the scan angles for each point pair) is reached. We have also found that eliminating the extreme scan angles improves the solution.

Note that the value of producing a smooth (low random error) trajectory estimate is tempered by the fact that systematic errors due to aircraft pitch (particularly evident in the horizontal errors) will likely be larger than the random errors produced by this method. Also note that if the scan angle values are stored per the LAS specification (scan angles relative to nadir, thus incorporating aircraft roll), systematic errors due to aircraft roll should be small.

User options are:
- **delta_t:** Time block duration (seconds).
- **min_delta_a:** Minimum total angle between points in a point pair solution (degrees).
- **min_num_sol:** Minimum number of point pair solutions required for a mean solution. This is typically not going to be a concern unless there are areas of very few returns (e.g., over water) or very small time blocks.
- **trim_a:** Extent of extreme scan angles to remove (degrees).

## Geometry sketch

The sketch below outlines the basic geometry of the point pair triangle solutions. The variable names match those in the `traj_xyz_mean` function in the `traj_sa_funcs.py` file.

![geometry sketch](./img/geometry_sketch.png)

## Sitka, AK example: Flightline 160503_011252

![800 pairs](./img/sitka/vt-dt01_mina15_minsol20_trim5.png)
![800 pairs](./img/sitka/hz-dt01_mina15_minsol20_trim5.png)

## UH example: Flightline 2 (C2_L2 file)

![6400 pairs](./img/uh/vt-dt01_mina15_minsol20_trim5.png)
![6400 pairs](./img/uh/hz-dt01_mina15_minsol20_trim5.png)
