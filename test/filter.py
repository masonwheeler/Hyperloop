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
        for pointA in sliceA:
            for pointB in sliceB:
                costA = pointA[3]
                costB = pointB[3]               
                pair = Path(costA + costB, costB, [pointA,pointB],
		pointA[0][0],pointA[0][1],pointB[0][1],0,0)
                pairs.append(pair)
    return pairs 

def filter_routes(lattice):
    
