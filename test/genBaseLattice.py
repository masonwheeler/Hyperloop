import config
import util

def gen_latticeXVals(scale, latticeSpacing):
    latticeLength = int(scale /latticesize)
    latticeXVals = [latticeSize * i for i in range(1,latticeLength)]
    return util.round_nums(latticeXVals)

def list_to_pairs(inList):
    return [ inList[i:i+2] for i in range(0,len(inList -1))]

def is_edge_relevant(edge,xValue):
    return ((edge[0][0] != edge[0][1]) and 
            ((edge[0][0] <= xValue and edge[0][1] >= xValue) or
            (edge[0][1] <= xValue and edge[0][0] >= xValue)))

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

def get_sliceCoordAbove(inFloat,sliceSpacing):
    return truncateUp(util.round_num(inFloat/sliceSpacing))
    
def get_sliceCoordBelow(inFloat,sliceSpacing):
   return truncateDown(util.round_num(inFloat/sliceSpacing))

def get_closestSlicePointAbove(inFloat,sliceSpacing):
    return round_num(get_sliceCoordAbove(inFloat,sliceSpacing)*sliceSpacing)
   
def get_closestSlicePointBelow(inFloat,sliceSpacing):
    return round_num(get_sliceCoordBelow(inFloat,sliceSpacing)*sliceSpacing)

def snap_maxMin_to_slice(maxMin,sliceSpacing):
    return [get_closestSlicePointBelow(maxMin[0],sliceSpacing),get_closestSlicePointAbove(maxMin[1],sliceSpacing)]

def maxMin_isValid(maxMin):
    return (maxMin[0] - maxMin[1]) > 0

def get_maxMinAndSpacing(maxMin, sliceSpacing):
    while True:
        maxMinOnSlice = snap_maxMin_to_slice(maxMin,sliceSpacing)
        if maxMin_isValid(maxMinOnSlice):
            break
        else:
            sliceSpacing /= 2.0
    return [maxMinOnSlice, sliceSpacing]

def build_latticeSlice(maxMinAndSpacing):
    gap = maxMinAndSpacing[0][0] - maxMinAndSpacing[0][1]
    numPoints = int(round_num(gap/sliceSpacing + 1))
    minVal = maxMinAndSpacing[0][1]
    spacing = maxMinAndSpacing[1]
    return [round_num(minVal + spacing*i) for i in range(0,numPoints)]

def generate_lattice(polygon,scale,latticeSpacing):
    edges = list_to_pairs(polygon)
    for xVal in gen_latticeXVals(scale,latticeSpacing):
        relevantEdges = relevant_edges_for_xVal(edges,xVal)
        intersections = util.round_nums(get_intersections(relevantEdges,xVal))
        maxMin = get_maxMin(intersections)
        maxMinAndSpacing = get_maxMinAndSpacing(maxMin,sliceSpacing)
        lattice.append(build_latticeSlice(maxMinAndSpacing))
    return lattice
        
