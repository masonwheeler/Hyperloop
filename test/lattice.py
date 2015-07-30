"""
Original Developer: Jonathan Ward
Purpose of Module: To build a lattice using smoothing spline.
Last Modified: 7/30/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Moved some functions to util.py and interpolate.py
"""

#Standard Modules:
import scipy.interpolate 
import numpy as np
import time

#Our Modules:
import config
import util
import cacher
import proj

class SlicePoint:
    pointId = 0
    geospatialCoords = []
    latlngCoords = []
    isInRightOfWay = False
    
    def __init__(self, pointId, geospatialCoords, isInRightOfWay):
        self.pointId = pointId
        self.geospatialCoords = geospatialCoords
        self.isInRightOfWay = isInRightOfWay
        self.latlngCoords = proj.geospatial_to_latlng(geospatialCoords,
                                                      config.proj)
    
    def as_dict(self):
        pointDict = {"pointId" : self.pointId,
                     "geospatialCoords" : self.geospatialCoords,
                     "latlngCoords" : self.latlngCoords,
                     "isInRightOfWay" : self.isInRightOfWay}
        return pointDict


class Slice:
    idIndex = 0
    directionsPoint = []
    splinePoint = []
    slicePoints = []    
    pointSpacing = config.pointSpacing

    def build_slice(self, idIndex, directionsPoint, splinePoint):              
        sliceVector = util.subtract(directionsPoint, splinePoint)
        sliceGrid = util.build_grid(sliceVector, self.pointSpacing, splinePoint)
        sliceSplinePoint = SlicePoint(idIndex,splinePoint, False).as_dict()
        idIndex += 1
        if sliceGrid == None:            
            sliceDirectionsPoint = SlicePoint(idIndex,directionsPoint, True).as_dict()
            idIndex += 1
            slicePoints = [sliceSplinePoint, sliceDirectionsPoint]
        else:
            sliceGridPoints = []
            for point in sliceGrid:
                sliceGridPoints.append(SlicePoint(idIndex, point, False).as_dict())
                idIndex += 1
            sliceDirectionsPoint = SlicePoint(idIndex, directionsPoint, True).as_dict()
            idIndex += 1
            slicePoints = [sliceSplinePoint] + sliceGridPoints + \
                          [sliceDirectionsPoint]   
        return [slicePoints, idIndex]

    def __init__(self, idIndex, directionsPoint, splinePoint):   
        self.directionsPoint = directionsPoint
        self.splinePoint = splinePoint
        self.slicePoints, self.idIndex = self.build_slice(idIndex, 
                                      directionsPoint, splinePoint)

    def as_list(self):
        return self.slicePoints

    def plottable_slice(self):
        sliceGeospatialCoords = [point["geospatialCoords"]
                                 for point in self.slicePoints]
        plottableSlice = zip(*sliceGeospatialCoords)
        return plottableSlice

    def display(self):
        print("Spline Point: " + str(self.splinePoint))
        print("Directions Point: " + str(self.directionsPoint))


class Lattice:
    latticeSlices = []
    plottableSlices = []

    def __init__(self, slices):
        self.latticeSlices = [eachSlice.as_list() for eachSlice in slices]
        self.plottableSlices = [eachSlice.plottable_slice()
                                for eachSlice in slices]


def get_sliceendpoints(sliceTValue, sampledDirections, xSpline, ySpline):
    rawDirectionsPoint = sampledDirections[int(sliceTValue.tolist())]    
    rawSplinePoint = [xSpline(sliceTValue), ySpline(sliceTValue)]
    fixedDirectionsPoint = list(rawDirectionsPoint)
    fixedSplinePoint = [point.tolist() for point in rawSplinePoint]
    return [fixedDirectionsPoint, fixedSplinePoint]

def build_lattice(sliceTValues, directionsPoints, xSpline, ySpline):
    slices = []
    idIndex = 1
    for sliceTValue in np.nditer(sliceTValues):
        directionsPoint, splinePoint = get_sliceendpoints(sliceTValue,
                                       directionsPoints, xSpline, ySpline)
        newSlice = Slice(idIndex, directionsPoint, splinePoint)
        idIndex = newSlice.idIndex
        slices.append(newSlice)
    lattice = Lattice(slices)
    return lattice

def build_directionsspline(directionsPoints):
    xCoordsList, yCoordsList = zip(*directionsPoints)
    xArray, yArray = np.array(xCoordsList), np.array(yCoordsList)
    numPoints = len(directionsPoints)
    tValues = np.arange(numPoints)
    endWeights = 100000
    smoothingFactor = 10**13
    directionsSpline = interpolate.smoothing_splines(xArray, yArray, tValues,
                                                 endWeights, smoothingFactor)
    return directionsSpline
    
def get_directionsspline(directionsPoints):
    directionsSpline = cacher.get_object("spline", build_directionsspline,
       [directionsPoints], cacher.save_spline, config.splineFlag)
    return directionsSpline

def get_lattice(sliceTValues, directionsPoints, xSpline, ySpline):
    lattice = cacher.get_object("lattice", build_lattice,
              [sliceTValues, directionsPoints, xSpline, ySpline],
              cacher.save_lattice, config.latticeFlag)
    return lattice

