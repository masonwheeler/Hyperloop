"""
Original Developer: Jonathan Ward
Purpose of Module: To provide interpolation functions for use across program.
Last Modified: 7/31/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added function to compute curvature metric for graph
"""

#Standard Modules:
import scipy.interpolate
import numpy as np
import time

#Our Modules:
import util
import config

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
    return curvature

def smoothing_splines(xArray, yArray, tValues, endWeights, smoothingFactor):
    numPoints = tValues.size
    weights = np.ones(numPoints)
    weights[0] = weights[-1] = endWeights

    xSpline = scipy.interpolate.UnivariateSpline(tValues, xArray, weights)
    xSpline.set_smoothing_factor(smoothingFactor)
    ySpline = scipy.interpolate.UnivariateSpline(tValues, yArray, weights)
    ySpline.set_smoothing_factor(smoothingFactor)
    return [xSpline, ySpline]

def interpolating_splines(xArray, yArray, tValues):
    xSpline = scipy.interpolate.InterpolatedUnivariateSpline(tValues, xArray)
    ySpline = scipy.interpolate.InterpolatedUnivariateSpline(tValues, yArray)
    return [xSpline, ySpline]

def curvature_metric(graphCurvatureArray):
    curvatureSize = graphCurvatureArray.size
    curvatureThreshhold = np.empty(curvatureSize)
    curvatureThreshhold.fill(config.curvatureThreshhold)
    absoluteCurvature = np.absolute(graphCurvatureArray)
    relativeCurvature = np.subtract(absoluteCurvature, curvatureThreshhold)
    excessCurvature = relativeCurvature.clip(min=0)
    curvatureMetric = np.sqrt(np.mean(np.square(excessCurvature)))
    #print(" curvature Array: " + str(graphCurvatureArray))
    #print(" curvature threshhold: " + str(curvatureThreshhold))
    #print("curvature metric: " + str(curvatureMetric))
    return curvatureMetric * 10**10

def graph_curvature(graphPoints, graphSampleSpacing):
    #t0 = time.clock()
    graphEdges = points_to_edges(graphPoints)
    sampledGraphPoints = sample_edges(graphEdges, graphSampleSpacing)
    #t1 = time.clock()
    #print("sampling edges took " + str(t1 -t0) + " seconds.")
    xArray, yArray = points_to_arrays(sampledGraphPoints)
    numPoints = xArray.size
    tValues = get_tvalues(numPoints)
    #t2 = time.clock()
    xSpline, ySpline = interpolating_splines(xArray, yArray, tValues)
    #splineValues = get_splinevalues(xSpline, ySpline
    graphCurvatureArray = splines_curvature(xSpline, ySpline, tValues)
    graphCurvature = curvature_metric(graphCurvatureArray)
    #t3 = time.clock()
    #print("Interpolating samples took " + str(t1 -t0) + " seconds.")
    return graphCurvature
     
