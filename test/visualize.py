import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

import util

def lists_to_tuples(lists):
    tuples = [tuple(eachList) for eachList in lists]
    return tuples

def get_boundingbox(polygon):
    xValues, yValues = zip(*polygon)
    xRange, yRange = util.get_maxmin(xValues), util.get_maxmin(yValues)
    return [xRange, yRange]

def plot_polygon(latlngPolygon):
    lnglatPolygon = util.swap_pairs(latlngPolygon)
    polygonVerts = lists_to_tuples(lnglatPolygon)
    plottablePolygon = patches.Polygon(polygonVerts, closed=True, fill=True)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.add_patch(plottablePolygon)
    lngRange, latRange = get_boundingbox(lnglatPolygon)
    latMax, latMin = latRange
    lngMax, lngMin = lngRange
    ax.set_xlim(lngMin,lngMax)
    ax.set_ylim(latMin,latMax)
    plt.show()
    
    
    
    
