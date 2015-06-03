import sys
import util

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

def slice_coord_above(inFloat,sliceYSpacing):
    return truncate_up(util.round_num(inFloat/sliceYSpacing))
    
def slice_coord_below(inFloat,sliceYSpacing):
    return truncate_down(util.round_num(inFloat/sliceYSpacing))

def closest_slicepoint_above(inFloat,sliceYSpacing):
    return util.round_num(
            slice_coord_above(inFloat, sliceYSpacing) * sliceYSpacing)
   
def closest_slicepoint_below(inFloat,sliceYSpacing):
    return util.round_num(
            slice_coord_below(inFloat, sliceYSpacing) * sliceYSpacing)

def maxmin_on_slice(maxMin,sliceYSpacing):
    return [closest_slicepoint_below(maxMin[0],sliceYSpacing),
            closest_slicepoint_above(maxMin[1],sliceYSpacing)]

def maxmin_valid(maxMin):
    return (maxMin[0] - maxMin[1]) > 0

def maxmin_yspacing(maxMin, sliceYSpacing):
    while True:
        maxMinOnSlice = maxmin_on_slice(maxMin,sliceYSpacing)
        if maxmin_valid(maxMinOnSlice):
            break
        else:
            sliceYSpacing /= 2.0
    return [maxMinOnSlice, sliceYSpacing]

def lattice_yslice(maxMinAndYSpacing):
    ySpacing = maxMinAndYSpacing[1]
    gap = maxMinAndYSpacing[0][0] - maxMinAndYSpacing[0][1]
    numPoints = int(util.round_num(gap/ySpacing + 1))
    minVal = maxMinAndYSpacing[0][1]
    return [[util.round_num(minVal + ySpacing*i)] for i in range(0,numPoints)]

def base_lattice(polygon,baseScale,sliceYSpacing,latticeXSpacing):
    edges = list_to_pairs(polygon)
    lattice = []
    latticeXVals = lattice_xvals(baseScale,latticeXSpacing)
    for xVal in latticeXVals:
        relevantEdges = relevant_edges_for_xval(edges,xVal)
        intersections = util.round_nums(get_intersections(relevantEdges,xVal))
        maxMin = get_maxmin(intersections)
        maxMinAndYSpacing = maxmin_yspacing(maxMin,sliceYSpacing)
        lattice.append(lattice_yslice(maxMinAndYSpacing))
    return lattice
