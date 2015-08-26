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
    pointSpacing = config.pointSpacing #Sets the spacing between Slice points

    def build_slice(self, idIndex, directionsPoint, splinePoint):              
        """Constructs each SlicePoint in the Slice and its idIndex"""
        sliceVector = util.subtract(directionsPoint, splinePoint)       
        sliceGrid, distances = util.build_grid(sliceVector, self.pointSpacing,
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

    def __init__(self, spatialSliceBounds):
        slices = []
        idIndex = 1
        for spatialSliceBound in spatialSliceBounds:
            directionsPoint, splinePoint = spatialSliceBound
            newSlice = Slice(idIndex, directionsPoint, splinePoint)
            idIndex = newSlice.idIndex
            self.latticeSlices.append(newSlice.as_list())


def build_lattice_slices(spatialSliceBounds):
    lattice = Lattice(spatialSliceBounds)
    latticeSlices = lattice.latticeSlices
    return latticeSlices


def curvature_test(xSpline, ySpline, sValues):
    splinesCurvature = interpolate.parametric_splines_2d_curvature(
                                            xSpline, ySpline, sValues)
    isCurvatureValid = interpolate.is_curvature_valid(splinesCurvature,
                                            config.curvatureThreshhold)
    return isCurvatureValid

def iteratively_build_directions_spline(sampledDirectionsPoints):
    xCoordsList, yCoordsList = zip(*sampledDirectionsPoints)
    xArray, yArray = np.array(xCoordsList), np.array(yCoordsList)
    numPoints = len(sampledDirectionsPoints)
    sValues = np.arange(numPoints)
    INITIAL_END_WEIGHTS = 100000
    INITIAL_SMOOTHING_FACTOR = 10**13    
    xSpline, ySpline = interpolate.smoothing_splines_2d(xArray, yArray, sValues,
                               INITIAL_END_WEIGHTS, INITIAL_SMOOTHING_FACTOR)
    isCurvatureValid = curvature_test(xSpline, ySpline, sValues)
    if isCurvatureValid:
        testSmoothingFactor = INITIAL_SMOOTHING_FACTOR
        while isCurvatureValid:            
            testSmoothingFactor *= 0.5
            interpolate.set_smoothing_factors_2d(xSpline, ySpline,
                                              testSmoothingFactor)                    
            isCurvatureValid = curvature_test(xSpline, ySpline, sValues)
        testSmoothingFactor *= 2
        interpolate.set_smoothing_factors_2d(xSpline, ySpline,
                                          testSmoothingFactor)
        return [xSpline, ySpline]
    else:
        while not isCurvatureValid:            
            testSmoothingFactor *= 2
            interpolate.set_smoothing_factors_2d(xSpline, ySpline,
                                              testSmoothingValue)
            isCurvatureValid = curvature_test(xSpline, ySpline, sValues)
        return [xSpline, ySpline]
    
def get_directionsspline(sampledDirectionsPoints):
    directionsSpline = cacher.get_object("spline",
              iteratively_build_directions_spline, [sampledDirectionsPoints],
                                       cacher.save_spline, config.splineFlag)
    return directionsSpline

def get_lattice(spatialSliceBounds):
    lattice = cacher.get_object("lattice", build_lattice_slices,
              [spatialSliceBounds], cacher.save_lattice, config.latticeFlag)
    return lattice

