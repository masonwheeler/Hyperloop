import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

import util

def lists_to_tuples(lists):
    tuples = [tuple(eachList) for eachList in lists]
    return tuples

def get_boundingbox(polygon):
    xValues, yValues = unzip_polygon(polygon)
    xRange, yRange = util.get_maxmin(xValues), util.get_maxmin(yValues)
    return [xRange, yRange]

def plot_polygon(polygon):
    polygonVerts = lists_to_tuples(polygon)
    plottablePolygon = patches.Polygon(polygonVerts, closed=True, fill=False)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xRange, yRange = get_boundingbox(polyconCoords)
    
    
    
    
    
