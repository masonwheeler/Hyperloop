import math 
import numpy as np
import random
import time

import config
import heights
import clothoid
import util

def curvature(location1,location2,inList,pylonSpacing):
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
        print("b")
        while (truncatedSortedIndices[1] + 1 > indices[k]):
            k += 1
            print(k)
        i = k
        indices.insert(k, truncatedSortedIndices[1] + 1)
        del truncatedSortedIndices[0]
    return indices

def pylon_cost(rawHeights, pylonSpacing, maxSpeed, gTolerance,
               costPerPylonLength, pylonBaseCost):
    kTolerance = gTolerance / math.pow(maxSpeed, 2)
    fixedHeights = [max(rawHeights)] + rawHeights + [max(rawHeights)]
    print("a")
    indices = interpolating_indices(fixedHeights,pylonSpacing,kTolerance)
    print("c")
    indicesNum = len(indices)
    data = [clothoid.buildClothoid(indices[i] * pylonSpacing, 
        fixedHeights[indices[i]], 0, j[i+1] * pylonSpacing, 
        fixedHeights[indices[i+1]], 0)
        for i in range(indicesNum - 1)]
    kappas, kappaPs, Ls = zip(*data)
    x0s = [n * pylonSpacing for n in range(len(List))]
    xVals = util.fastConcat(
        [[x0s[indices[i]] + 
        s * bC.evalXY(kappaPs[i] * math.pow(s,2), kappas[i] * s, 0, 1)[0][0]
        for s in np.linspace(0, Ls[i], 100)]
        for i in range(len(indices)-1)])
    yVals = util.fastConcat(
        [[fixedHeights[indices[i]] + 
        s * bC.evalXY(kappaPs[i] * math.pow(s,2), kappas[i] * s, 0, 1)[1][0]
        for s in np.linspace(0, Ls[i], 100)]
        for i in range(len(indices)-1)])
    yValsPlot = [0] * len(fixedHeights)
    for indexA in range(len(indices)-1):
        for indexB in range(indices[indexA],indices[indexA+1]):
            yValsPlot[indexB] = yVals[100 * indexA
                + int((indexB - indices[indexA]) * 100 / 
                    (indices[indexA + 1] - indices[indexA]))]
    pylonHeights = [m.fabs(pylonHeight) for pylonHeight in 
        util.subtract(yvalsPlot,fixedHeights)]
    totalLength = sum(pylonHeights)
    numberOfPylons = len(fixedHeights)
    print("The total number of pylons used is: " + numberOfPylons + ".")
    print("The sum of the lengths of the pylons is: " + totalLength + ".")
    pylonCostTotal = baseCost * numberOfPylons + costPerLength * totalLength
    return pylonCostTotal

    
        
