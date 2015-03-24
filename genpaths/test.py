"""
Jonathan Ward 3/18/2015

This file contains the function definitions and unit tests for evaluating 
the program output
"""

import time
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

def lattice_to_plotLattice(lattice):
    xValues = []
    yValues = []
    for latticeSlice in lattice:
        for point in latticeSlice:
            xValues.append(point[0])
            yValues.append(point[1])
    return [xValues,yValues]

def create_codes(route, isPolygon):
    numEdges = len(route) - isPolygon
    codes = [Path.MOVETO]
    for edgeNum in range(1, numEdges):
        codes.append(Path.LINETO)
    return codes

def unzip_polygon(polygon):
    xValues = []
    yValues = []
    for point in polygon:
        xValues.append(point[0])
        yValues.append(point[1])
    return [xValues, yValues]

def get_bounding_box(polygon):
    values = unzip_polygon(polygon) 
    xValues = values[0]
    yValues = values[1]
    xRange = get_maxANDmin(xValues)
    yRange = get_maxANDmin(yValues)
    return [xRange, yRange]