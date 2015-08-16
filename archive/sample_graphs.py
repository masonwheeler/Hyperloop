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
import config
import util
import velocityprofile as vel
    

def random_sample(merged):    
    numSampled = 0
    sampled = []
    while numSampled < config.graphSampleSize:
        numSampled += 1
        sampled.append(random.choice(merged))
    return sampled

# xPointstovPoints(): 
# Outputs a discrete velocity profile {v_i} given a discrete route {x_i}.
# The velocity profile v is a rolling average of the maximum speed allowed
# by a .3g radial acceleration constraint:
#       v_i = (1/2k) * sum_{i-k <j< i+k} sqrt(.3g * r_j).
# where r_j is the radius of the circle through {x_{j-1},x_j, x_{j+1}}.

def triple_to_velocity(triple):
    velocity = min(np.sqrt(config.lateralAccel * vel.points_to_radius(triple)),
                   config.maxSpeed)
    return velocity

def xPointstovPoints(xPoints):
    xTriples = [xPoints[i:i+3] for i in range(len(xPoints)-3)]
    velocities = map(triple_to_velocity, xTriples)
    startVelocity = [velocities[0]]
    startVelocities = velocities[:3]
    averagedStartVelocities = [vel.mean(startVelocities)]
    velocity5Tuples = [velocities[i:i+5] for i in range(len(velocities) - 5)]
    averagedMiddleVelocities = map(vel.mean, velocity5Tuples)
    endVelocities = velocities[-3:]
    averagedEndVelocities = [vel.mean(endVelocities)]
    endVelocity = [velocities[-1]]
    combinedVelocities = [startVelocity,
                          startVelocity, 
                          averagedStartVelocities,
                          averagedMiddleVelocities,
                          averagedEndVelocities,
                          endVelocity,
                          endVelocity]
    velocityProfile = util.fast_concat(combinedVelocities)
    return velocityProfile

def velprofile_to_velvariation(velProfile):
    #print(velProfile)
    velVariation = sum([np.absolute(velProfile[i+1] - velProfile[i])
                       for i in range(len(velProfile)-1)])
    return velVariation

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

def variation_constrained(merged):
    graphsLength = len(merged[0].geospatials)
    #print(graphsLength)
    n = int(np.log2(graphsLength))    
    if n > 3:
        #print("Entered main branch")
        maxVariation = 9.81 * 1.0 * 2**n
        currentNumPaths = config.numPaths[n-1]
        for graph in merged:
            graph.velProfile = xPointstovPoints(graph.geospatials)
            graph.velVariation = velprofile_to_velvariation(graph.velProfile)
            graph.tripTime = vPointsto_triptime(graph.velProfile,
                                                graph.geospatials)            
            graph.sampleCriterion = ((graph.landCost + graph.pylonCost) *
                                     graph.tripTime)                    
        filtered = filter(lambda graph: graph.velVariation < maxVariation,
                          merged)
        filtered.sort(key = lambda graph: graph.sampleCriterion)
        selected = filtered[:currentNumPaths]
    else:
        #print("Entered alt branch")
        merged.sort(key = lambda graph: graph.landCost + graph.pylonCost)
        selected = merged[:config.numPaths[n-1]]
    return selected

