import sys
import util
import math

import config

def lattice_xvals(baseScale, latticeXSpacing):
    latticeLength = int(baseScale /latticeXSpacing)
    latticeXVals = [latticeXSpacing * i for i in range(1,latticeLength)]
    return util.round_nums(latticeXVals)

def list_to_pairs(inList):
    return [ inList[i:i+2] for i in range(0,len(inList) -1)]

def edge_relevant(edge,xValue):
    return ((edge[0][0] != edge[1][0]) and 
            ((edge[0][0] <= xValue and xValue <= edge[1][0]) or
             (edge[1][0] <= xValue and xValue <= edge[0][0])))

def relevant_edges_for_xval(edgeList, xVal):
    return [edge for edge in edgeList if edge_relevant(edge,xVal)]

def slope_intercept(edge):
    slope = (edge[1][1] - edge[0][1])/(edge[1][0] - edge[0][0])
    intercept = edge[1][1] - slope*edge[1][0]
    return [slope, intercept]

def get_intersections(relevantEdges, xValue):
    slopeInts = [slope_intercept(edge) for edge in relevantEdges]
    return [slopeInt[0] * xValue + slopeInt[1] for slopeInt in slopeInts]

def get_maxmin(inList):
    return [max(inList), min(inList)]

def truncate_up(inFloat):
    if (int(inFloat) == inFloat):
        return inFloat
    else:
        if (inFloat >0):
            return int(inFloat) + 1
        else:
            return int(inFloat)

def truncate_down(inFloat):
    if (int(inFloat) == inFloat):
        return inFloat
    else:
        if (inFloat > 0):
            return int(inFloat)
        else:
            return int(inFloat) + 1

def slice_coord_above(inFloat,ySpacing):
    return truncate_up(util.round_num(inFloat/ySpacing))
    
def slice_coord_below(inFloat,ySpacing):
    return truncate_down(util.round_num(inFloat/ySpacing))

def closest_slicepoint_above(inFloat,ySpacing):
    return util.round_num(
            slice_coord_above(inFloat, ySpacing) * ySpacing)
   
def closest_slicepoint_below(inFloat,ySpacing):
    return util.round_num(
            slice_coord_below(inFloat, ySpacing) * ySpacing)

def maxmin_on_slice(maxMin,ySpacing):
    return [closest_slicepoint_below(maxMin[0],ySpacing),
            closest_slicepoint_above(maxMin[1],ySpacing)]

def maxmin_valid(maxMin):
    return (maxMin[0] - maxMin[1]) > 0

def get_stepup_stepdown(maxMins):
    stepUps = []
    stepDowns = []
    for maxMinIndex in range(len(maxMins)-1):
        maxA, minA = maxMins[maxMinIndex]
        maxB, minB = maxMins[maxMinIndex+1]
        stepUps.append(maxB - minA)
        stepDowns.append(minB - maxA)
    stepUp = max(stepUps)
    stepDown = min(stepDowns)
    return [stepUp,stepDown]

def get_ySpacing(maxMins,initialYSpacing):
    if all([maxMin[1] - maxMin[0] > initialYSpacing for maxMin in maxMins]):
        return initialYSpacing
    else:
        return min([maxMin[0] - maxMin[1] for maxMin in maxMins])        

def build_slice(maxMin,ySpacing,xVal):
    maxVal = int(maxMin[0] / ySpacing)
    minVal = int(maxMin[1] / ySpacing) + 1
    rawSlice = range(minVal,maxVal+1)
    ySlice = map(lambda y: [[xVal, util.round_num(y * ySpacing)]], rawSlice)   
    return ySlice

def get_angles(stepUp,stepDown,ySpacing,xSpacing):
    maxIndex,holder = divmod(stepUp, ySpacing)        
    minIndex,holder = divmod(stepDown, ySpacing)
    angleIndices = range(int(minIndex),int(maxIndex))
    angles = [math.degrees(math.atan2(float(angleIndex) * ySpacing, xSpacing))
            for angleIndex in angleIndices]
    return angles

def base_lattice(polygon,baseScale,initialYSpacing,latticeXSpacing):
    edges = list_to_pairs(polygon)
    lattice = []
    maxMins = []
    numPoints = 0
    latticeXVals = lattice_xvals(baseScale,latticeXSpacing)

    for xVal in latticeXVals:
        relevantEdges = relevant_edges_for_xval(edges,xVal)
        intersections = util.round_nums(get_intersections(relevantEdges,xVal))
        maxMin = get_maxmin(intersections)
        maxMins.append(maxMin)    
  
    ySpacing = get_ySpacing(maxMins, initialYSpacing)
    print("Using a vertical spacing of " + str(ySpacing) + " between lattice points.")
    stepUp, stepDown = get_stepup_stepdown(maxMins)
    angles = get_angles(stepUp, stepDown, ySpacing, latticeXSpacing)

    for index in range(len(latticeXVals)):
        newSlice = build_slice(maxMins[index],ySpacing,latticeXVals[index])
        numPoints += len(newSlice)
        lattice.append(newSlice)
    print("The lattice consists of " + str(numPoints) + " points in total.")
    
    return [lattice, angles, ySpacing]

