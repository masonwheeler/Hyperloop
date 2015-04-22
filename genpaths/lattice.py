"""
Jonathan Ward 4/22/2015

This file contains the function definitions for inputing a bounding polygonal
region and outputing a lattice.
"""

import math 
import random

def round_nums(listOfNums, ndigits):
    outputList = [round(value, ndigits) for value in listOfNums]
    return outputList    
    
def round_points(listOfPoints, ndigits):
    outputList = [round_nums(point, ndigits) for point in listOfPoints]
    return outputList

def get_distance(start, end):
    xDelta = end[0] - start[0]
    yDelta = end[1] - start[1]
    distance = math.sqrt(math.pow(xDelta,2) + math.pow(yDelta,2))
    return distance 
    
def get_angle(start, end):
    xDelta = end[0] - start[0]
    yDelta = end[1] - start[1]
    angleFromAxis = math.atan2(yDelta,xDelta)
    return angleFromAxis
    
def translate_point(start, point):
    translatedPoint = [point[i] - start[i] for i in range(0,len(start)) ] 
    return translatedPoint

def inverseTranslate_point(start, point):
    inverseTranslatedPoint = [point[i] + start[i] for i in range(0,len(start))]
    return inverseTranslatedPoint    
    
def rotate_point(angle, point):
    originalX = point[0]
    originalY = point[1]
    rotatedX = originalX * math.cos(angle) + originalY * math.sin(-angle)
    rotatedY = originalX * math.sin(angle) + originalY * math.cos(angle)
    rotatedPoint = [rotatedX, rotatedY]
    return rotatedPoint
    
def scale_point(distance, point, scale):
    scaledPt = [(point[0] / distance) * scale, (point[1] / distance) * scale]   
    return scaledPt

def inverseScale_point(distance, scale, point): 
    invScaledPt = [(point[0] * distance) / scale, (point[1] * distance) / scale]
    return invScaledPt    

def transform_point(start, end, point, scale):
    distance = get_distance(start, end)
    angle = get_angle(start, end)
    tPoint = translate_point(start, point)
    trPoint = rotate_point(-angle, tPoint)
    trsPoint = scale_point(distance, trPoint, scale)
    trsPoint = round_nums(trsPoint)
    return trsPoint
    
def transform_polygon(start, end, polygon, scale):
    transPolygon = [transform_point(start, end, point, scale) for point in polygon]
    return transPolygon

def inverseTransform_point(distance, angle, scale, start, trspoint, ndigits):
    trpoint = inverseScale_point(distance, scale, trspoint)
    tpoint = inverseRotate_point(angle, trpoint)
    point = inverseTranslate_point(start, tpoint)
    original = round_nums(point,ndigits)
    return original

def inverseTransform_object(distance, angle, scale, start, anObject, ndigits):
    invTransObject = [inverseTransform_point(distance, angle, scale, start, trspoint, ndigits) for trspoint in anObject]
    return invTransObject
    
def create_x_lattice(scale, latticeSize, ndigits):
    numPointsInLattice = int(scale / latticeSize)
    rawXLattice = [ latticeSize * i for i in range(1, numPointsInLattice) ]
    xLattice = round_nums(rawXLattice,ndigits)
    return xLattice
    
def list_to_pairs(inList):
    pairs = [ [inList[i], inList[i+1]] for i in range(0, len(inList) - 1)]
    return pairs

def is_edge_relevant(edge, xValue):
    firstPointXValue = edge[0][0]
    secondPointXValue = edge[1][0]
    rel = (((firstPointXValue <= xValue and xValue <= secondPointXValue ) or
            (secondPointXValue <= xValue and xValue <= firstPointXValue )) and
                                   firstPointXValue != secondPointXValue )   
    return rel

def relevant_edges_for_xvalue(edgeList, xValue):
    relEdges = [edge for edge in edgeList if is_edge_relevant(edge, xValue)]
    return relEdges
    
def edge_to_slopeIntercept(edge):
    slope = ((edge[1][1] - edge[0][1]) / (edge[1][0] - edge[0][0]))
    intercept = edge[1][1] - slope*edge[1][0]
    slopeIntercept = [slope, intercept]
    return slopeIntercept

def get_intersections(relevantEdges, xValue):
    slopeInts = [edge_to_slopeIntercept(edge) for edge in relevantEdges]
    inters = [slopeInt[0] * xValue + slopeInt[1] for slopeInt in slopeInts]
    return inters
    
def get_maxANDmin(inputList):
    maxANDmin = [max(inputList), min(inputList)]
    return maxANDmin

def truncateUp(inFloat):
    if (int(inFloat) == inFloat):
        outInt = inFloat
    else:        
        if (inFloat > 0):
            outInt = int(inFloat) + 1
        else:
            outInt = int(inFloat)
    return outInt

def truncateDown(inFloat):
    if (int(inFloat) == inFloat):
        outInt = inFloat
    else:        
        if (inFloat > 0):
            outInt = int(inFloat)
        else:
            outInt = int(inFloat) - 1
    return outInt

def get_sliceCoordinateAbove(inFloat,sliceSpacing,ndigits):
    roughSliceCoordinate = inFloat/sliceSpacing
    sliceCoordinate = round(roughSliceCoordinate,ndigits)
    sliceCoordinateAbove = truncateUp(sliceCoordinate)
    return sliceCoordinateAbove

def get_sliceCoordinateBelow(inFloat,sliceSpacing,ndigits):
    roughSliceCoordinate = inFloat/sliceSpacing
    sliceCoordinate = round(roughSliceCoordinate,ndigits)
    sliceCoordinateBelow = truncateDown(sliceCoordinate)
    return sliceCoordinateBelow

def get_closestSlicePointAbove(inFloat,sliceSpacing,ndigits):
    sliceCoordinateAbove=get_sliceCoordinateAbove(inFloat,sliceSpacing,ndigits)
    roughClosestSlicePointAbove = sliceCoordinateAbove * sliceSpacing
    closestSlicePointAbove = round(roughClosestSlicePointAbove,ndigits)
    return closestSlicePointAbove

def get_closestSlicePointBelow(inFloat,sliceSpacing,ndigits):
    sliceCoordinateBelow=get_sliceCoordinateBelow(inFloat,sliceSpacing,ndigits)
    roughClosestSlicePointBelow = sliceCoordinateBelow * sliceSpacing
    closestSlicePointBelow = round(roughClosestSlicePointBelow,ndigits)
    return closestSlicePointBelow

def move_maxMin_onto_slice(maxMin,sliceSpacing,ndigits):
    maxVal = maxMin[0]
    minVal = maxMin[1]
    maxOnSliceInPolygon=get_closestSlicePointBelow(maxVal,sliceSpacing,ndigits)
    minOnSliceInPolygon=get_closestSlicePointAbove(minVal,sliceSpacing,ndigits)
    maxMinOnSlice = [maxOnSliceInPolygon,minOnSliceInPolygon]
    return maxMinOnSlice 

def maxMin_isValid(maxMin):
    maxVal = maxMin[0]
    minVal = maxMin[1]
    gap = (maxVal - minVal)
    isValid = (gap > 0)
    return isValid

def get_sliceBounds(maxMin,initialSliceSpacing,ndigits):
    #print(maxMin)
    currentSliceSpacing = initialSliceSpacing
    maxMinOnSlice = move_maxMin_onto_slice(maxMin,currentSliceSpacing,ndigits)
    isValid = maxMin_isValid(maxMinOnSlice)
    while (not isValid):
        #print(currentSliceSpacing)
        currentSliceSpacing = currentSliceSpacing/2.0
        maxMinOnSlice = move_maxMin_onto_slice(maxMin,currentSliceSpacing,ndigits)
        isValid = maxMin_isValid(maxMinOnSlice)
    sliceBounds = [maxMinOnSlice,currentSliceSpacing]        
    return sliceBounds

def build_latticeYSlice(sliceBounds,ndigits):
    maxMin = sliceBounds[0]
    maxVal = maxMin[0]
    minVal = maxMin[1]
    sliceSpacing = sliceBounds[1]
    gap = maxVal - minVal
    roughFloatNumPoints = gap/sliceSpacing + 1
    floatNumPoints = round(roughFloatNumPoints,ndigits)
    numPoints = int(floatNumPoints)
    latticeYSlice = [round(minVal + sliceSpacing*index,ndigits) for index in range(0,numPoints)]
    return latticeYSlice

def add_xValue(latticeYSlice,xValue):
    latticeSlice = [[xValue,yValue] for yValue in latticeYSlice]
    return latticeSlice

def generate_lattice(polygon,scale,latticeSize,ndigits):
    initialSliceSpacing = latticeSize
    lattice = []
    xLattice = create_x_lattice(scale,latticeSize,ndigits)
    edgeList = list_to_pairs(polygon, False)
    for xValue in xLattice:
        relevantEdges = relevant_edges_for_xvalue(edgeList, xValue)
        roughIntersections = get_intersections(relevantEdges, xValue)
        intersections = round_nums(roughIntersections,ndigits)
        maxMin = get_maxMin(intersections)
        sliceBounds = get_sliceBounds(maxMin,initialSliceSpacing,ndigits)
        latticeYSlice = build_latticeYSlice(sliceBounds,ndigits)
        latticeSlice = add_xValue(latticeYSlice,xValue)
        lattice.append(latticeSlice)
    return lattice
