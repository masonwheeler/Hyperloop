import math 
import numpy as np
import random
import time

import config
import clothoid
import util

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
        #print("b")
        while (truncatedSortedIndices[1] + 1 > indices[k]):
            #print("entered loop")
            k += 1
        #print(i)
        i = k
        indices.insert(k, truncatedSortedIndices[1] + 1)
        del truncatedSortedIndices[0]
    return indices

def pylon_cost(rawHeights, pylonSpacing, maxSpeed, gTolerance,
               costPerPylonLength, pylonBaseCost):
    kTolerance = gTolerance / math.pow(maxSpeed, 2)
    fixedHeights = [max(rawHeights)] + rawHeights + [max(rawHeights)]
    #print(fixedHeights)
    indices = interpolating_indices(fixedHeights,pylonSpacing,kTolerance)
    #print("c")
    indicesNum = len(indices)
    data = [clothoid.buildClothoid(indices[i] * pylonSpacing, 
        fixedHeights[indices[i]], 0, indices[i+1] * pylonSpacing, 
        fixedHeights[indices[i+1]], 0)
        for i in range(indicesNum - 1)]
    kappas, kappaPs, Ls = zip(*data)
    x0s = [n * pylonSpacing for n in range(len(fixedHeights))]
    xVals = util.fast_concat(
        [[x0s[indices[i]] + 
        s * clothoid.evalXY(kappaPs[i] * math.pow(s,2), kappas[i] * s, 0, 1)[0][0]
        for s in np.linspace(0, Ls[i], 100)]
        for i in range(len(indices)-1)])
    yVals = util.fast_concat(
        [[fixedHeights[indices[i]] + 
        s * clothoid.evalXY(kappaPs[i] * math.pow(s,2), kappas[i] * s, 0, 1)[1][0]
        for s in np.linspace(0, Ls[i], 100)]
        for i in range(len(indices)-1)])
    yValsPlot = [0] * len(fixedHeights)
    for indexA in range(len(indices)-1):
        for indexB in range(indices[indexA],indices[indexA+1]):
            yValsPlot[indexB] = yVals[100 * indexA
                + int((indexB - indices[indexA]) * 100 / 
                    (indices[indexA + 1] - indices[indexA]))]
    pylonHeights = [math.fabs(pylonHeight) for pylonHeight in 
        util.subtract(yValsPlot,fixedHeights)]
    totalLength = sum(pylonHeights)
    numberOfPylons = len(fixedHeights)
    print("The total number of pylons used is: " + str(numberOfPylons) + ".")
    print("The sum of the lengths of the pylons is: " + str(totalLength) + ".")
    pylonCostTotal = pylonBaseCost * numberOfPylons + costPerPylonLength * totalLength
    return pylonCostTotal

    
        
