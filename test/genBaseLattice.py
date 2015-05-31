import config
import util

import sys

def gen_latticeXVals(baseScale, latticeXSpacing):
    latticeLength = int(baseScale /latticeXSpacing)
    latticeXVals = [latticeXSpacing * i for i in range(1,latticeLength)]
    return util.round_nums(latticeXVals)

def list_to_pairs(inList):
    return [ inList[i:i+2] for i in range(0,len(inList) -1)]

def is_edge_relevant(edge,xValue):
    return ((edge[0][0] != edge[1][0]) and 
            ((edge[0][0] <= xValue and xValue <= edge[1][0]) or
             (edge[1][0] <= xValue and xValue <= edge[0][0])))

def relevant_edges_for_xVal(edgeList, xVal):
    return [edge for edge in edgeList if is_edge_relevant(edge,xVal)]

def edge_to_slopeIntercept(edge):
    slope = (edge[1][1] - edge[0][1])/(edge[1][0] - edge[0][0])
    intercept = edge[1][1] - slope*edge[1][0]
    return [slope, intercept]

def get_intersections(relevantEdges, xValue):
    slopeInts = [edge_to_slopeIntercept(edge) for edge in relevantEdges]
    return [slopeInt[0] * xValue + slopeInt[1] for slopeInt in slopeInts]

def get_maxMin(inList):
    return [max(inList), min(inList)]

def truncateUp(inFloat):
    if (int(inFloat) == inFloat):
        return inFloat
    else:
        if (inFloat >0):
            return int(inFloat) + 1
        else:
            return int(inFloat)

def truncateDown(inFloat):
    if (int(inFloat) == inFloat):
        return inFloat
    else:
        if (inFloat > 0):
            return int(inFloat)
        else:
            return int(inFloat) + 1

def get_sliceCoordAbove(inFloat,sliceYSpacing):
    return truncateUp(util.round_num(inFloat/sliceYSpacing))
    
def get_sliceCoordBelow(inFloat,sliceYSpacing):
   return truncateDown(util.round_num(inFloat/sliceYSpacing))

def get_closestSlicePointAbove(inFloat,sliceYSpacing):
    return util.round_num(get_sliceCoordAbove(inFloat,sliceYSpacing)*sliceYSpacing)
   
def get_closestSlicePointBelow(inFloat,sliceYSpacing):
    return util.round_num(get_sliceCoordBelow(inFloat,sliceYSpacing)*sliceYSpacing)

def snap_maxMin_to_slice(maxMin,sliceYSpacing):
    return [get_closestSlicePointBelow(maxMin[0],sliceYSpacing),get_closestSlicePointAbove(maxMin[1],sliceYSpacing)]

def maxMin_isValid(maxMin):
    return (maxMin[0] - maxMin[1]) > 0

def get_maxMinAndYSpacing(maxMin, sliceYSpacing):
    while True:
        maxMinOnSlice = snap_maxMin_to_slice(maxMin,sliceYSpacing)
        if maxMin_isValid(maxMinOnSlice):
            break
        else:
            sliceYSpacing /= 2.0
    return [maxMinOnSlice, sliceYSpacing]

def build_latticeYSlice(maxMinAndYSpacing):
    ySpacing = maxMinAndYSpacing[1]
    gap = maxMinAndYSpacing[0][0] - maxMinAndYSpacing[0][1]
    numPoints = int(util.round_num(gap/ySpacing + 1))
    minVal = maxMinAndYSpacing[0][1]
    return [[util.round_num(minVal + ySpacing*i)] for i in range(0,numPoints)]

def gen_baseLattice(polygon,baseScale,sliceYSpacing,latticeXSpacing):
    edges = list_to_pairs(polygon)
    lattice = []
    latticeXVals = gen_latticeXVals(baseScale,latticeXSpacing)
    for xVal in latticeXVals:
        relevantEdges = relevant_edges_for_xVal(edges,xVal)
        intersections = util.round_nums(get_intersections(relevantEdges,xVal))
        maxMin = get_maxMin(intersections)
        maxMinAndYSpacing = get_maxMinAndYSpacing(maxMin,sliceYSpacing)
        lattice.append(build_latticeYSlice(maxMinAndYSpacing))
    return lattice
