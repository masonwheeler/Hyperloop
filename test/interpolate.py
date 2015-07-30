"""
Original Developer: Jonathan Ward
Purpose of Module: To provide interpolation functions for use across program.
Last Modified: 7/30/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

#Standard Modules:

#Our Modules:
import util

def points_to_edges(points):
    return util.to_pairs(points)

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

def points_to_arrays(points):
    xCoordsList, yCoordsList = zip(*points)
    xArray, yArray = np.array(xCoordsList), np.array(yCoordsList)
    return [xArray, yArray]

def get_tvalues(numPoints):
    tValues = np.arange(0.0, float(numPoints))
    return tValues

def get_splinevalues(xSpline, ySpline, tValues):
    xValues = xSpline(tValues)
    yValues = ySpline(tValues)
    return xValues, yValues

def get_slicetvalues(tValues, nth):
    sliceTValues = tValues[::nth]
    return sliceTValues

def splines_curvature(xSpline, ySpline, tValues):
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

def smoothing_splines(xArray, yArray, tValues, endWeights, smoothingFactor):
    weights = np.ones(numPoints)
    weights[0] = weights[-1] = endWeights

    xSpline = scipy.interpolate.UnivariateSpline(tValues, xArray, weights)
    xSpline.set_smoothing_factor(smoothingFactor)
    ySpline = scipy.interpolate.UnivariateSpline(tValues, yArray, weights)
    ySpline.set_smoothing_factor(smoothingFactor)
    return [xSpline, ySpline]

def interpolating_splines(xArray, yArray, tValues):
    xSpline = scipy.interpolate.InterpolatedUnivariateSpline(tValues, xArray)
    xSpline = scipy.interpolate.InterpolatedUnivariateSpline(tValues, xArray)
    return [xSpline, ySpline]
