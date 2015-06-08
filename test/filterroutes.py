import numpy as np
import random
import math
from functools import partial
import itertools

import config
import util
import cost

class Path:
    cost = 0
    endCost = 0
    points = []
    startXVal = 0
    startYVal = 0
    endYVal = 0
    startAngle = 0
    endAngle = 0
    def __init__(self,cost,endCost,points,startXVal,startYVal,endYVal,
    startAngle,endAngle):
        self.cost = cost
        self.endCost = endCost
        self.points = points
        self.startXVal = startXVal
        self.startYVal = startYVal
        self.endYVal = endYVal
        self.startAngle = startAngle
        self.endAngle = endAngle

def get_angles(ydelta):
    angles = [math.atan2(config.latticeXSpacing,yVal) for
	 yVal in range(-yDelta,yDelta+1)]
    return angles

def get_pairs(lattice, angles):
    offset = (len(angles) -1)/2
    pairs = []
    for sliceIndex in range(len(lattice)-1):
        sliceA = lattice[sliceIndex]
        sliceB = lattice[sliceIndex + 1]
        slicePairs = []
        for pointA in sliceA:
            for pointB in sliceB:
                costA = pointA[3]
                costB = pointB[3]               
                pair = Path(costA + costB, costB, [pointA,pointB],
                pointA[0][0],pointA[0][1],pointB[0][1],0,0)
                slicePairs.append(pair)
        slicePairs.sort(key = lambda pair: pair.cost)
        pairs.append(slicePairs)       
    return pairs 

def merge_filter(pathsA, pathsB, degreeConstraint, angles, numPaths):
    merged = []
    for pathA in pathsA:
        for pathB in pathsB:
            if(pathA.endYVal == pathB.startYVal):
                if(abs(pathA.endAngle - pathB.startAngle) < degreeConstraint):
                    mergedPath = Path(pathA.cost + pathB.cost - pathA.endCost,
                    pathA.endCost + pathB.endCost,
                    pathA.points + pathB.points,
                    pathA.startXVal, pathA.startYVal,
                    pathB.endYVal, pathA.startAngle, pathB.endAngle)
                    merged.append(mergedPath)
    merged.sort(key = lambda path: path.cost)
    selected = merged[:min(numPaths,len(merged))]
    return selected

def treefold(pairs, degreeConstaint, angles, numPaths):
    layers = [pairs]
    workingLayerIndex = 0
    layersIndex = 0
    workingLayerSize = len(pairs)
    numLayers = 1
    while(numLayers != 0 or workingLayerSize != 1):
        if(workingLayerSize - workingLayerIndex == 0):
            if(layersSize - layersIndex == 1):
               breakFlag = True;
            else:
               layersIndex += 1
               workingLayerIndex = 0
               workingLayerSize = len(layers[layersIndex])
        elif(workingLayerSize - workingLayerIndex == 1):
            if(layersSize - layersIndex == 1):
                breakFlag = True;
            else:
                layers[layersIndex+1].append(
                layers[layersIndex][workingLayerIndex])
                layersIndex += 1
                workingLayerIndex = 0
                workingLayerSize = len(layers[layersIndex])
        else:
           if(layersSize - layersIndex == 1):
               layers.append([])
               layersSize += 1
           pathsA = layers[layersIndex][workingLayerIndex]
           pathsB = layers[layersIndex][workingLayerIndex + 1]
           merged = merg_filter(pathsA,pathsB,degreeConstraint,angles,numPaths)
        if breakFlag:
            break
    filteredRoutes = layers[layersIndex][0]
    return filteredRoutes








