import math

import config
import util
import cost
import time

class Path:
    cost = 0
    endCost = 0
    waypoints = []
    startXVal = 0
    startYVal = 0
    endYVal = 0
    startAngle = 0
    endAngle = 0
    triptime = 0
    plot_times = []
    points = []
    vel_points = [] 
    accel_points = []
    pylon_data = ["Data about pylon placement and pylon cost."]
    comfort = "not noticeable"

    def __init__(self,cost,endCost,waypoints,startXVal,startYVal,endYVal,
    startAngle,endAngle,comfort,triptime,plot_times,points,vel_points,accel_points,pylon_data):
        self.cost = cost
        self.comfort = comfort
        self.triptime = triptime
        self.plot_times = plot_times
        self.points = points
        self.vel_points = vel_points
        self.accel_points = accel_points
        self.pylon_data = pylon_data
        self.endCost = endCost
        self.waypoints = waypoints
        self.startXVal = startXVal
        self.startYVal = startYVal
        self.endYVal = endYVal
        self.startAngle = startAngle
        self.endAngle = endAngle

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
                pointA[0][0],pointA[0][1],pointB[0][1],0,0,0,0,0,0,0,0,0)
                slicePairs.append(pair)
        slicePairs.sort(key = lambda pair: pair.cost)
        pairs.append(slicePairs)       
    return pairs 

def merge_filter(pathsA, pathsB, degreeConstraint, angles, numPaths):
    merged = []
    m = 0
    for pathA in pathsA:
        for pathB in pathsB:
            m += 1
            if(pathA.endYVal == pathB.startYVal):
                if(abs(pathA.endAngle - pathB.startAngle) < degreeConstraint):
                    mergedPath = Path(pathA.cost + pathB.cost - pathA.endCost,
                    pathA.endCost + pathB.endCost,
                    pathA.waypoints + pathB.waypoints[1:],
                    pathA.startXVal, pathA.startYVal,
                    pathB.endYVal, pathA.startAngle, pathB.endAngle,0,0,0,0,0,0,0)
                    merged.append(mergedPath)
    merged.sort(key = lambda path: path.cost)
    selected = merged[:min(numPaths,len(merged))]
    return [selected, m]

def treefold(pairs, degreeConstraint, angles, numPaths):
    start_time = time.time()
    layers = [pairs]
    workingLayerIndex = 0
    breakFlag = False
    layersIndex = 0
    workingLayerSize = len(pairs)
    numLayers = 1
    n = 0
    while(numLayers != 1 or workingLayerSize != 1):
        if(workingLayerSize - workingLayerIndex == 0):
            if(numLayers - layersIndex == 1):
               breakFlag = True;
            else:
               layersIndex += 1
               workingLayerIndex = 0
               workingLayerSize = len(layers[layersIndex])
        elif(workingLayerSize - workingLayerIndex == 1):
            if(numLayers - layersIndex == 1):
                breakFlag = True;
            else:
                layers[layersIndex+1].append(
                layers[layersIndex][workingLayerIndex])
                layersIndex += 1
                workingLayerIndex = 0
                workingLayerSize = len(layers[layersIndex])
        else:
           if(numLayers - layersIndex == 1):
               layers.append([])
               numLayers += 1
           pathsA = layers[layersIndex][workingLayerIndex]
           pathsB = layers[layersIndex][workingLayerIndex + 1]
           merged, mplus = merge_filter(pathsA,pathsB,degreeConstraint,angles,numPaths)
           layers[layersIndex+1].append(merged)
           print "Catenating paths of length "+str(2**n)+"..."       
           workingLayerIndex += 2
        if breakFlag:
            break
    filteredRoutes = layers[layersIndex][0]
    print("Merged " +str(n) +"routes in  " + str(time.time() - start_time)) + " seconds."
    print ("there are " +str(len(filteredRoutes)) + " routes.")
    return filteredRoutes









