"""
Jonathan Ward 3/18/2015

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
    
def create_x_lattice(scale, latticeSize):
    numPointsInLattice = int(scale / latticeSize)
    xLattice = [ latticeSize * i for i in range(1, numPointsInLattice) ]
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

def value_to_lattice(value, latticeSize, shiftUp):
    latticeSteps = value/latticeSize
    truncatedLatticeSteps = int(value/latticeSize)
    shiftedTruncatedLatticeSteps = truncatedLatticeSteps + shiftUp
    shiftedValue = shiftedTruncatedLatticeSteps * latticeSize
    return shiftedValue

def onLattice(value, latticeSize):
    isOnLattice = (value_to_lattice(value, latticeSize, 0) == value)
    return isOnLattice
    
def maxANDmin_to_lattice(maxANDmin, latticeSize):
    maxOnLattice = value_to_lattice(maxANDmin[0], latticeSize, 0)
    if onLattice(maxANDmin[1]):
        minOnLattice = value_to_lattice(maxANDmin[1], latticeSize, 0)
    else:
        minOnLattice = value_to_lattice(maxANDmin[1], latticeSize, 1)
    maxANDminOnLattice = [ maxOnLattice, minOnLattice ]
    return maxANDminOnLattice
    
def build_lattice_slice(maxANDmin, xValue, latticeSize):
    maxim = maxANDmin[0]
    minim = maxANDmin[1]
    gap = maxANDmin[0] - maxANDmin[1]
    ySteps = int(round(gap/latticeSize)) + 1
    latticeYSlice = [minim + (latticeSize * i) for i in range(0, ySteps)]
    latticeSlice = [[xValue, yValue] for yValue in latticeYSlice]
    return latticeSlice
    
def generate_lattice(polygon, scale, latticeSize):
    lattice = []
    xLattice = create_x_lattice(scale, latticeSize)
    edgeList = list_to_pairs(polygon)
    for xValue in xLattice:
        relevantEdges = relevant_edges_for_xvalue(edgeList, xValue)
        roughIntersections = get_intersections(relevantEdges, xValue)
        intersections = round_nums(roughIntersections, ndigits)
        roughMaxAndMin = get_maxANDmin(intersections, latticeSize)
        maxANDmin = maxANDmin_to_lattice(roughMaxAndMin, latticeSize)
        RoughLatticeSlice = build_lattice_slice(maxANDmin, xValue, latticeSize)
        latticeSlice = round_points(RoughLatticeSlice, ndigits)
        lattice.append(latticeSlice)
    return lattice

