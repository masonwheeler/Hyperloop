"""
Original Developer: Jonathan Ward
Purpose of Module: To build a lattice using smoothing spline.
Last Modified: 8/13/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added Iteratively Spline construction
"""

#Standard Modules:
import numpy as np

#Our Modules:
import config
import util
import cacher
import proj
import interpolate

class SlicePoint:
    """Builds a point from geospatial coordinates, id, and a rightofway flag"""
    pointId = 0 #Unique identifier used in merging process.
    geospatialCoords = [] #
    latlngCoords = []
    isInRightOfWay = False #Denotes whether the point is on state property.
    
    def __init__(self, pointId, geospatialCoords, isInRightOfWay):
        self.pointId = pointId
        self.geospatialCoords = geospatialCoords
        self.isInRightOfWay = isInRightOfWay
        self.latlngCoords = proj.geospatial_to_latlng(geospatialCoords,
                                                      config.proj)
    
    def as_dict(self):
        """Returns the SlicePoint data as a dictionary"""
        pointDict = {"pointId" : self.pointId,
                     "geospatialCoords" : self.geospatialCoords,
                     "latlngCoords" : self.latlngCoords,
                     "isInRightOfWay" : self.isInRightOfWay}
        return pointDict


class Slice:
    """Builds Lattice Slice from a directions point and a spline point."""
    idIndex = 0 #Unique identifier for the first SlicePoint in the Slice
    directionsPoint = [] #The SlicePoint in the right of way
    splinePoint = [] #The SlicePoint in the interpolating spline
    slicePoints = [] #Contains all SlicePoints in the Slice
    pointSpacing = config.pointSpacing #Sets the spacing between Slice points

    def build_slice(self, idIndex, directionsPoint, splinePoint):              
        """Constructs each SlicePoint in the Slice and its idIndex"""
        sliceVector = util.subtract(directionsPoint, splinePoint)        
        sliceGrid = util.build_grid(sliceVector, self.pointSpacing,
                                                 splinePoint)
        sliceSplinePoint = SlicePoint(idIndex,splinePoint, False).as_dict()
        idIndex += 1
        if sliceGrid == None:            
            sliceDirectionsPoint = SlicePoint(idIndex, 
                                     directionsPoint, True).as_dict()
            idIndex += 1
            slicePoints = [sliceSplinePoint, sliceDirectionsPoint]
        else:
            sliceGridPoints = []
            for point in sliceGrid:
                sliceGridPoints.append(SlicePoint(idIndex, point,
                                                  False).as_dict())
                idIndex += 1
            sliceDirectionsPoint = SlicePoint(idIndex, directionsPoint,
                                              True).as_dict()
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
    """Builds Lattice from the directions, the splines and the arc-parameter"""
    latticeSlices = []
    plottableSlices = []

    def get_sliceendpoints(self, sliceTValue, sampledDirections, xSpline,
                                                                 ySpline):          
        rawDirectionsPoint = sampledDirections[int(sliceTValue.tolist())]    
        rawSplinePoint = [xSpline(sliceTValue), ySpline(sliceTValue)]
        fixedDirectionsPoint = list(rawDirectionsPoint)
        fixedSplinePoint = [point.tolist() for point in rawSplinePoint]
        return [fixedDirectionsPoint, fixedSplinePoint]

    def __init__(self, sliceTValues, directionsPoints, xSpline, ySpline):
        slices = []
        idIndex = 1
        for sliceTValue in np.nditer(sliceTValues):
            directionsPoint, splinePoint = self.get_sliceendpoints(sliceTValue,
                                           directionsPoints, xSpline, ySpline)
            newSlice = Slice(idIndex, directionsPoint, splinePoint)
            idIndex = newSlice.idIndex
            self.latticeSlices.append(newSlice.as_list())
            self.plottableSlices.append(newSlice.plottable_slice())


def iterativelybuild_directionsspline(directionsPoints):
    xCoordsList, yCoordsList = zip(*directionsPoints)
    xArray, yArray = np.array(xCoordsList), np.array(yCoordsList)
    numPoints = len(directionsPoints)
    tValues = np.arange(numPoints)
    INITIAL_END_WEIGHTS = 100000
    INITIAL_SMOOTHING_FACTOR = 10**13    
    xSpline, ySpline = interpolate.smoothing_splines(xArray, yArray, tValues,
                               INITIAL_END_WEIGHTS, INITIAL_SMOOTHING_FACTOR)
    splinesCurvature = interpolate.splines_curvature(xSpline, ySpline, tValues)
    isCurvatureValid = interpolate.is_curvature_valid(splinesCurvature,
                                            config.curvatureThreshhold)
    if isCurvatureValid:
        testSmoothingFactor = INITIAL_SMOOTHING_FACTOR
        while isCurvatureValid:            
            testSmoothingFactor *= 0.5
            interpolate.set_smoothing_factors(xSpline, ySpline,
                                              testSmoothingFactor)
            splinesCurvature = interpolate.splines_curvature(xSpline, ySpline,
                                                                      tValues)
            isCurvatureValid = interpolate.is_curvature_valid(splinesCurvature,
                                                    config.curvatureThreshhold)
        
        testSmoothingFactor *= 2
        interpolate.set_smoothing_factors(xSpline, ySpline,
                                          testSmoothingFactor)
        return [xSpline, ySpline]
    else:
        while not isCurvatureValid:            
            testSmoothingFactor *= 2
            interpolate.set_smoothing_factors(xSpline, ySpline,
                                              testSmoothingValue)
            splinesCurvature = interpolate.splines_curvature(xSpline, ySpline,
                                                                      tValues)
            isCurvatureValid = interpolate.is_curvature_valid(splinesCurvature,
                                                    config.curvatureThreshhold)
        return [xSpline, ySpline]
    
def build_directionsspline(directionsPoints):
    xCoordsList, yCoordsList = zip(*directionsPoints)
    xArray, yArray = np.array(xCoordsList), np.array(yCoordsList)
    numPoints = len(directionsPoints)
    tValues = np.arange(numPoints)
    endWeights = 100000
    smoothingFactor = 10**13
    xSpline, ySpline = interpolate.smoothing_splines(xArray, yArray, tValues,
                                                 endWeights, smoothingFactor)
    return [xSpline, ySpline]
    
def get_directionsspline(directionsPoints):
    directionsSpline = cacher.get_object("spline", iterativelybuild_directionsspline,
       [directionsPoints], cacher.save_spline, config.splineFlag)
    return directionsSpline

def get_lattice(sliceTValues, directionsPoints, xSpline, ySpline):
    lattice = cacher.get_object("lattice", Lattice,
              [sliceTValues, directionsPoints, xSpline, ySpline],
              cacher.save_lattice, config.latticeFlag)
    return lattice

