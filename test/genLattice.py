import config
import util

def gen_latticeXVals(scale, latticeSpacing, ndigits):
    latticeLength = int(scale /latticesize)
    latticeXVals = [latticeSize * i for i in range(1,latticeLength)]
    return util.round_nums(latticeXVals)

def list_to_pairs(inList):
    return [ inList[i:i+2] for i in range(0,len(inList -1)]

def is_edge_relevant(edge,xValue):
    return ((edge[0][0] != edge[0][1]) and 
            ((edge[0][0] <= xValue and edge[0][1] >= xValue) or
            (edge[0][1] <= xValue and edge[0][0] >= xValue)))

def relevant_edges_for_xVal(edgeList, xVal):
    return [edge for edge in edgeList if is_edge_relevant(edge,xVal)]

def edge_to_slopeIntercept(edge):
    slope = (edge[1][1] - edge[0][1])/(edge[1][0] - edge[0][0]))
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

def get_sliceCoordAbove(inFloat,sliceSpacing,ndigits):
    return truncateUp(round(inFloat/sliceSpacing))
    
def get_sliceCoordBelow(inFloat,sliceSpacing,ndigits):
   return truncateDown(round(inFloat/sliceSpacing))

def get_closestSlicePointAbove(inFloat,sliceSpacing,ndigits):
    return round(get_sliceCoordAbove(inFloat,sliceSpacing,ndigits)*sliceSpacing,ndigits)
   
def get_closestSlicePointBelow(inFloat,sliceSpacing,ndigits):
    return round(get_sliceCoordBelow(inFloat,sliceSpacing,ndigits)*sliceSpacing,ndigits)

def snap_maxMin_to_slice(maxMin,sliceSpacing,ndigits):
    return [get_closestSlicePointBelow(maxMin[0],sliceSpacing,ndigits),get_closestSlicePointAbove(maxMin[1],sliceSpacing,ndigits)]

def maxMin_isValid(maxMin):
    return (maxMin[0] - maxMin[1]) > 0

def get_maxMinAndSpacing(maxMin, sliceSpacing, ndigits):
    while True:
        maxMinOnSlice = snap_maxMin_to_slice(maxMin,sliceSpacing,ndigits)
        if maxMin_isValid(maxMinOnSlice):
            break
        else:
            sliceSpacing /= 2.0
    return [maxMinOnSlice, sliceSpacing]

def build_latticeSlice(maxMinAndSpacing,ndigits):
    gap = maxMinAndSpacing[0][0] - maxMinAndSpacing[0][1]
    numPoints = int(round(gap/sliceSpacing + 1, ndigits))
    minVal = maxMinAndSpacing[0][1]
    spacing = maxMinAndSpacing[1]
    return [round(minVal + spacing*i ,ndigits) for i in range(0,numPoints)]

def generate_lattice(polygon,scale,latticeSpacing,ndigits):
    edges = list_to_pairs(polygon)
    for xVal in gen_latticeXVals(scale,latticeSpacing,ndigits):
        relevantEdges = relevant_edges_for_xVal(edges,xVal)
        intersections = util.round_nums(get_intersections(relevantEdges,xVal))
        maxMin = get_maxMin(intersections)
        maxMinAndSpacing = get_maxMinAndSpacing(maxMin,sliceSpacing,ndigits)
        lattice.append(build_latticeSlice(maxMinAndSpacing,ndigits))
    return lattice
        
