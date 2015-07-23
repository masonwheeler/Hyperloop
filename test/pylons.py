"""
Original Developer: David Roberts
Purpose of Module: To determine the pylon cost component of an edge
Last Modified: 7/21/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify naming and fix formatting.
"""

#Standard Modules:
import math 
import numpy as np
import random
import time

#Our Modules:
import util
import config
import clothoid
import quintic as quint


def build_waypoints_bcs_sets(sPoints, zPoints, n):    
    numSIntervals = len(sPoints) - 1
    numSets = int(math.ceil(float(numSIntervals) / float(n)))
    waypointsBCsSets = [0 for i in range(numWaypointsBCsSets)]

    #Each set of waypoints and boundary conditions contains the following:
    # Take N to be the number of waypoints.
    # [list of independent variable values e.g. "t_i",
    #  list of dependent variable values e.g. "x_i = x(t_i)",
    #  initial first derivative of dependent variable e.g. "dx/dt|(t_0)"
    #  initial second derivative of dependent variable e.g. "dx^2/dt^2|(t_0)"     
    #  final first derivative of dependent variable e.g. "dx/dt|(t_N)"
    #  final second derivative of dependent variable e.g. "dx^2/dt^2|(t_N)"]
     
    if numSets == 1:
        waypointsBCsSets = [[sPoints, zPoints, 0, 0, 0, 0]]
    elif numSets == 2:
        waypointsBCsSets[0] = [sPoints[0 : n+1],
                               zPoints[0 : n+1],
                               0,               
                               0,               
                               ((zPoints[n+1] - zPoints[n])/
                                (sPoints[n+1] - sPoints[n])),
                               0]                       

        waypointsBCsSets[1] = [sPoints[n : numSIntervals+1],
                               zPoints[n : numSIntervals+1],
                               ((zPoints[n+1] - zPoints[n])/
                                (sPoints[n+1] - sPoints[n])),
                               0,
                               0,
                               0]
    else:
        waypointsBCsSets[0] = [sPoints[0 : n+1],
                               zPoints[0: n+1],
                               0,
                               0,
                               ((zPoints[n+1]-zPoints[n])/
                                (sPoints[n+1]-sPoints[n])),
                               0]  
        for j in range(1, numSets-1):
            waypointsBCSSets[j] = [sPoints[j*n : (j+1)*n+1],
                                   zPoints[j*n : (j+1)*n+1],
                                   ((zPoints[j*n+1]-zPoints[j*n])/
                                    (sPoints[j*n+1]-sPoints[j*n])),
                                   0,
                                   ((zPoints[(j+1)*n+1] - zPoints[(j+1)*n])/
                                    (sPoints[(j+1)*n+1] - sPoints[(j+1)*n])),
                                   0]

        waypointsBCsSets[-1] = [sPoints[(numSets-1)*n : numSIntervals+1],
                                zPoints[(numSets-1)*n : numSIntervals+1],
        ((zPoints[(numSets-1)*n+1] - zPoints[(numSets-1)*n])/
         (sPoints[(numSets-1)*n+1] - sPoints[(numSets-1)*n])),
                                0,
                                0,
                                0]
    return waypointsBCsSets

def szPointstozVals(sPoints, zPoints, n, sVals):
    waypointsBCSSets = build_waypoints_bcs_sets(sPoints, zPoints, n)
    zCoeffs = [quint.minimum_jerk_interpolation(waypointsBCs) for
               waypointsBCs in waypointsBCsSets]
    sVals = np.array(sVals)
    sPoints = np.array(sPoints)
    zVals = quint.coeffs_to_vals(zCoeffs, sVals, sPoints)
    return [sVals, zVals]

def szPointstoHeights(sPoints, zPoints, n):
    waypointsBCSSets = build_waypoints_bcs_sets(sPoints, zPoints, n)
    zCoeffs = [quint.minimum_jerk_interpolation(waypointsBCs) for
               waypointsBCs in waypointsBCsSets]
    sSample = np.linspace(0,sPoints[-1],config.numHeights)
    sPoints = np.array(sPoints)
    Heights = quint.coeffs_to_vals(zCoeffs, sSample, sPoints)
    return Heights

def curvature(location1, location2, paddedElevations, pylonSpacing):
    "Computes the curvature of the clothoid"
    x0 = location1 * pylonSpacing
    x1 = location2 * pylonSpacing
    theta0 = 0
    theta1 = 0
    y0 = inList[location1]
    y1 = inList[location2]
    kappa, kappaPrime, L = clothoid.buildClothoid(x0, y0, theta0,
                                                  x1, y1, theta1)
    if kappa < 0:
        return kappaPrime
    else:
        return kappa + L * kappaPrime

def reversesort_elevationindices(elevations):
    elevationsIndices = range(len(elevations))
    sortedIndices = sorted(elevationsIndices,
                            key = lambda i: elevations[i], reverse=True)
    return sortedIndices

def get_relevant_indices(paddedElevations, pylonSpacing, curvatureTolerance):
    elevations = paddedElevations[1:-1]
    sortedIndices = reversesort_elevationindices(elevations)    
    relevantIndices = [0, sortedIndices[1] , len(paddedElevations) - 1]
    i = 1
    j = 1
    curvatureA = curvature(relevantIndices[i-1], relevantIndices[i],
                                paddedElevations, pylonSpacing)
    curvatureB = curvature(relevantIndices[i], relevantIndices[i+1],
                               paddedElevations, pylonSpacing)    
    while (curvatureA < curvatureTolerance
           and curvatureB < curvatureTolerance
           and len(relevantIndices) < len(paddedElevations) ):
        k = 0
        while (sortedIndices[j] + 1 > relevantIndices[k]):
            k += 1
        relevantIndices.insert(k, sortedIndices[j] + 1)
        j += 1
        i = k
        backwardCurvature = curvature(relevantIndices[i-1], relevantIndices[i],
                                      paddedElevations, pylonSpacing)
        forwardCurvature = curvature(relevantIndices[i], relevantIndices[i+1],
                                     paddedElevations, pylonSpacing)
    return relevantIndices

def build_pylons(pylonLocations):
    pylonLocationElevations = [pylonLocation["elevation"] for pylonLocation in pylonLocations]
    curvatureTolerance = config.gTolerance * math.pow(config.maxSpeed, 2)
    paddedElevations = [max(pylonLocationElevations)] + pylonLocationElevations + [max(pylonLocationElevations)]
    relevantIndices = get_relevant_indices(paddedElevations, config.pylonSpacing,
                                           curvatureTolerance)

    sVals = [n * config.pylonSpacing for n in range(len(pylonLocations))]
    sPoints = [sVals[relevantIndex] for relevantIndex in relevantIndices]
    zPoints = [paddedElevations[relevantIndex] for relevantIndex
                                               in relevantIndices]
    sVals, zVals = szPointstozVals(sPoints, zPoints, 5, sVals)
    Heights = szPointstoHeights(sPoints, zPoints, 5)
    pylonHeights = [math.fabs(pylonHeight) for pylonHeight in util.subtract(zVals,fixedHeights)]
    for pylonLocation in pylonLocations:
        pylonLocation["pylonHeight"] = \
          highestElevation - pylonLocation["elevation"]
    return pylonLocations

    pylonCostTotal = pylonBaseCost * numberOfPylons + costPerPylonLength * totalLength   
    return pylonCostTotal


def build_pylons(pylonLocations):
    pylonLocationsByElevation = sorted(pylonLocations,
        key=lambda pylonLocation : pylonLocation["elevation"])
    highestPylonLocation = pylonLocationsByElevation[-1]
    highestElevation = highestPylonLocation["elevation"]
    for pylonLocation in pylonLocations:
        pylonLocation["pylonHeight"] = \
          highestElevation - pylonLocation["elevation"]
    return pylonLocations
        
def get_pyloncosts(pylonLocations):
    for pylonLocation in pylonLocations:
        pylonLocation["pylonCost"] = (config.pylonBaseCost + 
            pylonLocation["pylonHeight"] * config.pylonCostPerMeter)
    return pylonLocations

def edge_pyloncost(pylonLocations):
    edgePylonCost = sum([pylonLocation["pylonCost"] for pylonLocation
                         in pylonLocations])
    return edgePylonCost

