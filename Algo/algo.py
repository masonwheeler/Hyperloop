import numpy as np
import random
import math
import time
from functools import partial
import itertools

def gen_lat(latLen, latHeight):
    heightRange = range(0, latHeight)
    lat = []
    eachSlice = np.array(heightRange)
    for i in range(0,latLen):
	lat.append(eachSlice)
    return lat

def gen_randomPath(lattice):
    randomPath = np.array([])
    for eachSlice in lattice:
        randomPath=np.append(randomPath,[eachSlice[random.randint(0,eachSlice.size-1)]])
    return randomPath

def yVals_to_angles(maxLatticeHeight):
    angles = np.array([])
    for i in range(-maxLatticeHeight, maxLatticeHeight+1):
       angles = np.append(angles,[math.degrees(math.atan(i))])
    return angles

def filterPath(degreeConstraint,angles,path):
    offset = (len(angles) - 1)/2
    valid=True
    for i in range(0, len(path)-2):
        if(abs(angles[path[i+1]-path[i]+offset]-angles[path[i+2]-path[i+1]+offset]) > degreeConstraint):
            #print(path[i],path[i+1],path[i+2])
            #print(angles[path[i+1] - path[i] + offset])
            #print(angles[path[i+2] - path[i+1] + offset])
	    valid=False
            break       
    return valid

def filterPair(degreeConstraint,angles,path0,path1):
    #print(pair)
    offset = (len(angles) -1)/2
    path0point0, path0point1 = path0[-2:]
    #print(edges0[1])
    path1point0,path1point1 = path1[:2]
    #print(angles[edges0[1] - edges0[0] + offset])
    valid = abs(angles[path0point1-path0point0+offset]-angles[path1point1-path1point0+offset])<degreeConstraint
    return valid

def gen_allPaths(lattice,latLen,latHeight):
    allPaths = []
    radix = np.zeros(latLen)
    allPaths.append(np.copy(radix))
    upper = np.full(latLen,latHeight-1)
    #print(upper)
    counter = 0
    lastValFilled = False
    #print(latlen)	
    while True:
	#print(counter)
	#print(radix)
        if (radix[counter] < upper[counter]):	    
            #allPaths.append(np.copy(radix))
            lastValFilled = False
	    if counter == 0:
		radix[counter] += 1
	    else:
        	radix[:counter] = np.zeros(counter)
	        radix[counter] += 1
	        counter = 0	    
	    #print(radix)	
            allPaths.append(np.copy(radix))		
        else:
            if (counter == (latLen - 1)):
		if lastValFilled:
		    break
		else:
                    lastValFilled = True
                    counter = 0
            else:
                counter += 1
    return allPaths

def filter_allPaths(allPaths,degreeConstraint,angles):
    return filter(partial(filterPath,degreeConstraint,angles),allPaths)
    
def treeFold(inList,func):
    layers=[inList]
    lowestLayer = layers[0]
    while not (len(layers) == 1 and len(layers[len(layers)-1]) == 1):
	if len(lowestLayer) > 1:
            if len(layers) == 1:
		nextLayer = []
		layers.insert(0,nextLayer)		
	    nextLayer = layers[0]
	    val1=lowestLayer.pop()
	    val0=lowestLayer.pop()	 
            newVal = func(val0,val1)		
	    nextLayer.insert(0,newVal)
	elif len(lowestLayer) == 1:
	    if len(layers) == 1:
		break
	    else:
		nextLayer = layers[0]
		nextLayer.insert(0,lowestLayer.pop())
	elif len(lowestLayer) == 0:		
	    if len(layers) == 1:
		break
	    else:
		nextLayer = layers[0]		
		layers.pop()
		lowestLayer = nextLayer
    return lowestLayer[0]

#print(testBinaryMerge([1,1,1,1,1,1],lambda x, y: x+y))

def lattice_to_potentialEdges(lattice, latLen,latHeight):
    potentialEdges = []
    for i in range(0,latLen - 1):
	slice0 = lattice[i]
        slice1 = lattice[i+1]
        potentialEdges.append([list(eachTuple) for eachTuple in list(itertools.product(*[slice0,slice1]))]) 
    return potentialEdges

def mergeFilter(paths0,paths1,func):
    merged = []
    for path0 in paths0:
	for path1 in paths1:
	    if path0[len(path0)-1] == path1[0]:
		if func(path0,path1):
		    merged.append(path0 + path1[1:])
    return merged

latLen = 10
latHeight = 10
degreeConstraint = 60
t0 = time.clock()
lattice = gen_lat(latLen,latHeight)
angles = yVals_to_angles(latHeight)
potentialEdges = lattice_to_potentialEdges(lattice,latLen,latHeight)
#edges0 = potentialEdges[0]
#edges1 = potentialEdges[1]
filterFunc = lambda edge0,edge1 : filterPair(degreeConstraint,angles,edge0,edge1)
mergeFunc = lambda edges0,edges1 : mergeFilter(edges0,edges1,filterFunc)
#print(merged)
treeFold(potentialEdges,mergeFunc)
t1 = time.clock()
print(t1 - t0)
"""
allPaths = gen_allPaths(lattice,latLen,latHeight)
print(len(allPaths))
filteredPaths = filter_allPaths(allPaths,degreeConstraint,angles)
print(len(filteredPaths))
#print(allPaths)
#randomPath = gen_randomPath(lattice)
#print(randomPath)
#print(filterPath(randomPath,90,angles))
#merged = [eachPair[0] + eachPair[1][1:0] for eachPair in list(itertools.product(*[edges0,edges1])) if (eachPair[0][len(eachPair[0])-1] == eachPair[1][0] and func(eachPair))]
#pairs = [eachPair for eachPair in list(itertools.product(*[edges0,edges1])) if eachPair[0][len(eachPair[0])-1] == eachPair[1][0]]
    #for pair in pairs:
	#if func(pair):
	    #merged.append(pair[0] + pair[1][1:])	    
"""
