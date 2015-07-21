"""
Original Developer: David Roberts
Purpose of Module: To determine the pylon cost component of an edge
Last Modified: 7/18/15
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
    waypointsBCSSets

    zCoeffs = sum([quint.minimum_jerk_interpolation(waypointsBCs) for
                   waypointsBCs in waypointsBCsSets],[])
    sVals = np.array(sVals)
    sPoints = np.array(sPoints)
    zVals = quint.coeffs_to_vals(zCoeffs, sVals, sPoints)
    return [sVals, zVals]

def szPointstoHeights(sPoints, zPoints, n):
    numSIntervals = len(sPoints) - 1
    numSets = int(math.ceil(float(numSIntervals) / float(n)))
    waypointsBCsSets = [0 for i in range(numSets)]
    if numWaypointsBCsSets == 1:
        waypointsBCsSets = [[sPoints, zPoints, 0, 0, 0, 0]]
    elif numWaypointsBCsSets == 2:
        waypointsBCsSets[0] = [sPoints[0:n+1],
                               zPoints[0:n+1],
                               0,
                               0,
                               ((zPoints[n+1] - zPoints[n])/
                                (sPoints[n+1] - sPoints[n])),
                               0]

        waypointsBCsSets[1] = [sPoints[n:N+1],
                               zPoints[n:N+1], 
                               ((zPoints[n+1]-zPoints[n])/
                                (sPoints[n+1]-sPoints[n])),
                               0,
                               0,
                               0]
    else:
        G[0] = [sPoints[0:n+1],zPoints[0:n+1],0,0, (zPoints[n+1]-zPoints[n])/(sPoints[n+1]-sPoints[n]),0]  
        for j in range(1,m-1):
            G[j] = [sPoints[j*n:(j+1)*n+1],zPoints[j*n:(j+1)*n+1], (zPoints[j*n+1]-zPoints[j*n])/(sPoints[j*n+1]-sPoints[j*n]),0,(zPoints[(j+1)*n+1]-zPoints[(j+1)*n])/(sPoints[(j+1)*n+1]-sPoints[(j+1)*n]),0]
        G[-1] = [sPoints[(m-1)*n:N+1], zPoints[(m-1)*n:N+1],(zPoints[(m-1)*n+1]-zPoints[(m-1)*n])/(sPoints[(m-1)*n+1]-sPoints[(m-1)*n]) ,0,0,0]

    zCoeffs = sum([quint.minimum_jerk_interpolation(g) for g in G],[])
    sSample = np.linspace(0,sPoints[-1],config.numHeights)
    sPoints = np.array(sPoints)
    Heights = quint.coeffs_to_vals(zCoeffs, sSample, sPoints)
    return Heights

def curvature(location1, location2, inList, pylonSpacing):
    #print("Called curvature with variables:")
    #print(location1, location2, inList, pylonSpacing)
    data = clothoid.buildClothoid(location1 * pylonSpacing, 
      inList[location1], 0, location2 * pylonSpacing, inList[location2], 0)
    if data[0] < 0:
        return data[1]
    else:
        return data[0] + data[2] * data[1]


def interpolating_indices(inList, pylonSpacing, kTolerance):
    truncatedList = inList[1 : len(inList) - 1]
    truncatedSortedIndices = util.get_indices(truncatedList)
    indices = [0, truncatedSortedIndices[0] + 1, len(inList) - 1]
    i = 1
    while (curvature(indices[i-1],indices[i],inList,pylonSpacing) < kTolerance
      and curvature(indices[i],indices[i+1],inList,pylonSpacing) < kTolerance
      and indices != range(len(inList))):
        k = 0
        while (truncatedSortedIndices[1] + 1 > indices[k]):
            k += 1
        i = k
        indices.insert(k, truncatedSortedIndices[1] + 1)
        del truncatedSortedIndices[0]
    return indices

def pylon_cost(rawHeights, pylonSpacing, maxSpeed, gTolerance,
               costPerPylonLength, pylonBaseCost):
    t0 = time.time()
    kTolerance = gTolerance / math.pow(maxSpeed, 2)
    fixedHeights = [max(rawHeights)] + rawHeights + [max(rawHeights)]
    indices = interpolating_indices(fixedHeights,pylonSpacing,kTolerance)
    indicesNum = len(indices)
    data = [clothoid.buildClothoid(indices[i] * pylonSpacing, 
        fixedHeights[indices[i]], 0, indices[i+1] * pylonSpacing, 
        fixedHeights[indices[i+1]], 0)
        for i in range(indicesNum - 1)]
    kappas, kappaPs, Ls = zip(*data)
    sVals = [n * pylonSpacing for n in range(len(fixedHeights))]
    sPoints = [sVals[index] for index in indices]
    zPoints = [fixedHeights[index] for index in indices]
    sVals, zVals = szPointstozVals(sPoints, zPoints, 5, sVals)
    Heights = szPointstoHeights(sPoints, zPoints, 5)
    pylonHeights = [math.fabs(pylonHeight) for pylonHeight in util.subtract(zVals,fixedHeights)]
    totalLength = sum(pylonHeights)
    numberOfPylons = len(fixedHeights)
    pylonCostTotal = pylonBaseCost * numberOfPylons + costPerPylonLength * totalLength   
#    print("The total number of pylons used is: " + str(numberOfPylons) + ".")
#    print("The sum of the lengths of the pylons is: " + str(totalLength) + ".")
    return [pylonCostTotal, Heights]

    
        
