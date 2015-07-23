"""
Original Developer: Jonathan Ward
Purpose of Module: To sample routes from the route merging step.
Last Modified: 7/22/16
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module.
"""

#Standard Modules:
import random
import numpy as np

#Our Modules:
import velocityprofile as vel


# xPointstovPoints(): 
# Outputs a discrete velocity profile {v_i} given a discrete route {x_i}.
# The velocity profile v is a rolling average of the maximum speed allowed
# by a .3g radial acceleration constraint:
#       v_i = (1/2k) * sum_{i-k <j< i+k} sqrt(.3g * r_j).
# where r_j is the radius of the circle through {x_{j-1},x_j, x_{j+1}}.

def xPointstovPoints(x):
    v = [min(np.sqrt(9.81*.3*gen.points_to_radius(x[0:3])),330)] + \
        [min(np.sqrt(9.81*.3*gen.points_to_radius(x[0:3])),330)] + \
        [gen.mean([min(np.sqrt(9.81*.3*gen.points_to_radius(x[j-1:j+2])),330)
         for j in range(2-1,2+2)])] + \
        [gen.mean([min(np.sqrt(9.81*.3*gen.points_to_radius(x[j-1:j+2])),330)
         for j in range(i-2,i+3)]) for i in range(3,-4)] + \
        [gen.mean([min(np.sqrt(9.81*.3*gen.points_to_radius(x[j-1:j+2])),330)
         for j in range(-3-1,-3+2)])] + \
        [min(np.sqrt(9.81*.3*gen.points_to_radius(x[-3:len(x)])),330)] + \
        [min(np.sqrt(9.81*.3*gen.points_to_radius(x[-3:len(x)])),330)]
    return v

# vPointsto_triptime(): 
# Outputs triptime T of a discrete route {x_i} given its discrete velocity profile {v_i}.
# The triptime is computed assuming a piecewise linear interpolation of the {x_i} (into a set of line-segments),
# and assuming that the velocity in the segment connecting x_i to x_{i+1} is v_i:
#      T = sum_i s_i/v_i
# where s_i is the distance between x_i and x_{i+1}.

def vPointsto_triptime(v, x):
    s = [np.linalg.norm(x[i+1]-x[i]) for i in range(-1)]
    triptime = sum([s[i]/v[i] for i in range(len(s))])
    return triptime

def sample_routes(merged):
    n = int(np.log2(len(merged[0].geospatialCoords)))
    print len(merged[0].geospatialCoords)
    print n
    if n > 3:
       velocityProfiles = [xPointstovPoints(route.geospatials)
                           for route in merged]
       variations = [sum([np.absolute(v[i+1] - v[i]) for i in range(len(v)-1)])
                     for v in velocityProfiles]
       triptimes = [vPointsto_triptime(velocityProfiles[i],
                    merged[i].geospatialCoords) for i in range(len(merged))]
       costs = [route.landCost+route.pylonCost for route in merged]
       merged = filter(merged, lambda route:
                       variations[merged.index(route)] < 9.81 * .1 * 2**n)
       merged.sort(key = lambda route:
         (route.landCost + route.pylonCost) * triptimes[merged.index(route)])
       selected = merged[:config.numPaths[n-1]]
    else:
       merged.sort(key = lambda route: route.landCost + route.pylonCost)
       selected = merged[:config.numPaths[n-1]]
    return selected

