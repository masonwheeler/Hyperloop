import scipy.interpolate 
import numpy as np
import time

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
        #print(pointId)
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


def sample_edge(edge, sampleSpacing, offset):
    edgeLength = util.norm(util.edge_to_vector(edge))
    edgePoints = []       
    while offset <= edgeLength:
        point = util.distance_to_point(edge, offset)
        edgePoints.append(point)
        offset += sampleSpacing
    offset -= edgeLength
    return [edgePoints, offset]

def sample_edges(edges, sampleSpacing):
    offset = 0   
    points = []
    pointsList = []
    for edge in edges:
        edgePoints, offset = sample_edge(edge, sampleSpacing, offset)
        pointsList.append(edgePoints)
        points += edgePoints
    return points 

def sample_edges(edges, sampleSpacing):
    offset = 0   
    points = []
    for edge in edges:
        edgePoints, offset = sample_edge(edge, sampleSpacing, offset)
        points += edgePoints
    return points 
    
def build_spline(directionsPoints):    
    xCoordsList, yCoordsList = zip(*directionsPoints)
    xArray, yArray = np.array(xCoordsList), np.array(yCoordsList)
    numPoints = len(directionsPoints)
    weights = np.ones(numPoints)

    weights[0] = 100000
    weights[-1] = 100000
    smoothingFactor = 10**13

    tValues = np.arange(numPoints)
    xSpline = scipy.interpolate.UnivariateSpline(tValues, xArray, weights)
    xSpline.set_smoothing_factor(smoothingFactor)
    ySpline = scipy.interpolate.UnivariateSpline(tValues, yArray, weights)
    ySpline.set_smoothing_factor(smoothingFactor)
    return [xSpline, ySpline]

def get_tvalues(numPoints):
    tValues = np.arange(0.0, float(numPoints))
    return tValues

def get_splinevalues(xSpline, ySpline, tValues):
    xValues = xSpline(tValues)
    yValues = ySpline(tValues)
    return xValues, yValues

def get_curvature(xSpline, ySpline, tValues):    
    xFirstDeriv = xSpline.derivative(n=1)
    yFirstDeriv = ySpline.derivative(n=1)
    xSecondDeriv = xSpline.derivative(n=2)
    ySecondDeriv = ySpline.derivative(n=2)
    xFirstDerivValues = xFirstDeriv(tValues)
    yFirstDerivValues = yFirstDeriv(tValues)
    xSecondDerivValues = xSecondDeriv(tValues)
    ySecondDerivValues = ySecondDeriv(tValues)

    tLength = tValues.size
    powers = np.empty(tLength)
    powers.fill(1.5)
    curvature = np.divide(
                  np.subtract(
                    np.multiply(xFirstDerivValues, ySecondDerivValues),
                    np.multiply(yFirstDerivValues, xSecondDerivValues)
                  ),
                  np.power(
                    np.add(
                      np.square(xFirstDerivValues), 
                      np.square(yFirstDerivValues)
                    ), 
                    powers
                  )
                )
    return [tValues, curvature]

def get_slicetvalues(tValues, nth):
    sliceTValues = tValues[::nth]
    return sliceTValues    

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
    
def get_spline(points):
    spline = cacher.get_object("spline", build_spline, [points],
                               cacher.save_spline, config.splineFlag)
    return spline

def get_lattice(sliceTValues, directionsPoints, xSpline, ySpline):
    lattice = cacher.get_object("lattice", build_lattice,
              [sliceTValues, directionsPoints, xSpline, ySpline],
              cacher.save_lattice, config.latticeFlag)
    return lattice

