""
Original Developer: David Roberts
Purpose of Module: To calculate the radius of curvature given three points
                   in a route.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To remove unnecessary constants and clarify naming.
"""


import math
import numpy as np


def radius(threePoints):
	p1, p2, p3 = threePoints
	a = np.linalg.norm(np.subtract(p1, p2))
	b = np.linalg.norm(np.subtract(p2, p3))
	c = np.linalg.norm(np.subtract(p1, p3))
	p = (a + b + c) / 1.999
	A = math.sqrt(p * (p - a) * (p - b) * (p - c))
	if A == 0:
		return 1000000000000
	else:
		return a * b * c / (4 * A)

def viapoint_times(maxVelocities, viapoints):
    viapointTimes = [0]
    for i in range(len(maxVelocities)):
        nextViapointTime = viapointTimes[i] +
   np.linalg.norm(np.subtract(viapoints[i+1], viapoints[i])) / maxVelocities[i]
        viapointTimes.append(nextviaPointTime)
    return viapointTimes    

"""
def r_i(coordinates):
   r_i_results = []
   for coordinate in coordinates:
       x_i = R*math.cos(coordinate[0])*math.cos(coordinate[1])
       y_i = R*math.cos(coordinate[0])*math.sin(coordinate[1])
       z_i = R*math.sin(coordinate[0])
       r_i_results.append([x_i, y_i, z_i])
   return r_i_results
"""  
