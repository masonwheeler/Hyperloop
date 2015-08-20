"""
Original Developer: Jonathan Ward
Purpose of Module: To provide interpolation functions for use across program.
Last Modified: 8/13/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added function to set smoothing factor
"""

#Standard Modules:
import scipy.interpolate
import numpy as np

#Our Modules:
import util
import config

########## For Edge Sampling ##########

def points_to_edges(points):
    return util.to_pairs(points)

def distance_along_edge_to_point(edge, distanceAlongEdge):
    edgeStart, edgeEnd = edge
    edgeVector = util.subtract(edgeEnd, edgeStart)
    edgeLength = util.norm(edgeVector)
    scaleFactor = distanceAlongEdge / edgeLength
    scaledVector = util.scale(scaleFactor, edgeVector)
    point = util.add(scaledVector, edgeStart)
    return point

def sample_edge(edge, sampleSpacing, distanceAlongEdge):
    edgeLength = util.norm(util.edge_to_vector(edge))
    edgePoints = []
    while distanceAlongEdge <= edgeLength:
        point = distance_along_edge_to_point(edge, distanceAlongEdge)
        edgePoints.append(point)
        distanceAlongEdge += sampleSpacing
    distanceAlongEdge -= edgeLength
    return [edgePoints, distanceAlongEdge]

def sample_edges(edges, sampleSpacing):
    distanceAlongEdge = 0
    points = []
    for edge in edges:
        edgePoints, distanceAlongEdge = sample_edge(edge, sampleSpacing,
                                                      distanceAlongEdge)
        points += edgePoints
    return points

def sample_path(pathPoints, pathSampleSpacing):
    pathEdges = points_to_edges(pathPoints)
    sampledPathPoints = sample_edges(pathEdges, pathSampleSpacing)
    return sampledPathPoints

########## Auxilary Functions ##########

def points_2d_to_arrays(points2d):
    xCoordsList, yCoordsList = zip(*points2d)
    xArray, yArray = np.array(xCoordsList), np.array(yCoordsList)
    return [xArray, yArray]

def points_3d_to_arrays(points3d):
    xCoordsList, yCoordsList, zCoordsList = zip(*points3d)
    xArray = np.array(xCoordsList)
    yArray = np.array(yCoordsList)
    zArray = np.array(zCoordsList)
    return [xArray, yArray, zArray]

def get_s_values(numPoints):
    sValues = np.arange(0.0, float(numPoints))
    return sValues

def get_spline_values(spline, sValues):
    splineValues = spline(sValues)
    return splineValues

def get_slicesValues(sValues, nth):
    slicesValues = sValues[::nth]
    return slicesValues

########## For 2d Smoothing Splines ##########

def smoothing_splines(xArray, yArray, sValues, endWeights, smoothingFactor):
    numPoints = sValues.size
    weights = np.ones(numPoints)
    weights[0] = weights[-1] = endWeights

    xSpline = scipy.interpolate.UnivariateSpline(sValues, xArray, weights)
    xSpline.set_smoothing_factor(smoothingFactor)
    ySpline = scipy.interpolate.UnivariateSpline(sValues, yArray, weights)
    ySpline.set_smoothing_factor(smoothingFactor)
    return [xSpline, ySpline]

def set_smoothing_factors(xSpline, ySpline, smoothingFactor):
    xSpline.set_smoothing_factor(smoothingFactor)
    ySpline.set_smoothing_factor(smoothingFactor)
    return [xSpline, ySpline]

########## For Interpolating Splines ##########

def interpolating_splines_2d(xArray, yArray, sValues):
    xSpline = scipy.interpolate.InterpolatedUnivariateSpline(sValues, xArray)
    ySpline = scipy.interpolate.InterpolatedUnivariateSpline(sValues, yArray)
    return [xSpline, ySpline]

def interpolate_points_2d(points2d):
    numPoints = len(points3d)
    sValues = get_s_values(numPoints)
    xArray, yArray = points_2d_to_arrays(points2d) 
    xSpline, ySpline = interpolating_splines_3d(xArray, yArray, sValues)
    return [xSpline, ySpline]

def interpolating_splines_3d(xArray, yArray, zArray, sValues):
    xSpline = scipy.interpolate.InterpolatedUnivariateSpline(sValues, xArray)
    ySpline = scipy.interpolate.InterpolatedUnivariateSpline(sValues, yArray)
    zSpline = scipy.interpolate.InterpolatedUnivariateSpline(sValues, zArray)
    return [xSpline, ySpline, zSpline]

def interpolate_points_3d(points3d):
    numPoints = len(points3d)
    sValues = get_s_values(numPoints)
    xArray, yArray, zArray = points_3d_to_arrays(points3d) 
    xSpline, ySpline, zSpline = interpolating_splines_3d(xArray, yArray,
                                                        zArray, sValues)
    return [xSpline, ySpline, zSpline, sValues]

########## For Curvature Computations ##########

def get_derivative_values(spline, sValues):
    firstDeriv = spline.derivative(n=1)
    secondDeriv = spline.derivative(n=2)
    firstDerivValues = firstDeriv(sValues)
    secondDerivValues = secondDeriv(sValues)
    return [firstDerivValues, secondDerivValues]

def compute_explicit_curvature(firstDerivValues, secondDerivValues):
    sLength = firstDerivValues.size
    powers = np.empty(sLength)
    powers.fill(1.5)
    ones = np.ones(sLength)
    curvatureArray = np.divide(
                         np.absolute(secondDerivValues),
                         np.power(
                             np.add(ones, firstDerivValues),
                             powers
                         )
                      )
    return curvatureArray
                                                       
def compute_curvature_array_2d(xFirstDerivValues, xSecondDerivValues,
                               yFirstDerivValues, ySecondDerivValues):
    sLength = xFirstDerivValues.size
    powers = np.empty(sLength)
    powers.fill(1.5)
    curvatureArray2d = np.divide(
                           np.subtract(
                               np.multiply(xFirstDerivValues,
                                           ySecondDerivValues),
                               np.multiply(yFirstDerivValues,
                                           xSecondDerivValues)
                           ),
                           np.power(
                               np.add(
                                  np.square(xFirstDerivValues),
                                  np.square(yFirstDerivValues)
                               ),
                               powers
                           )
                       )
    return curvatureArray2d

def compute_curvature_array_3d(xFirstDerivValues, xSecondDerivValues,
                               yFirstDerivValues, ySecondDerivValues,
                               zFirstDerivValues, zSecondDerivValues):
    sLength = xFirstDerivValues.size
    powers = np.empty(sLength)
    powers.fill(1.5)

    firstTerm = np.square(
                    np.subtract(
                        np.multiply(zSecondDerivValues, yFirstDerivValues),
                        np.multiply(ySecondDerivValues, zFirstDerivValues)
                    )
                )
    secondTerm = np.square(
                     np.subtract(
                         np.multiply(xSecondDerivValues, zFirstDerivValues),
                         np.multiply(zSecondDerivValues, xFirstDerivValues)
                     )
                 )
    thirdTerm = np.square(
                    np.subtract(
                        np.multiply(ySecondDerivValues, xFirstDerivValues),
                        np.multiply(xSecondDerivValues, yFirstDerivValues)
                    )
                )
    curvatureArray3d = np.divide(
                    np.sqrt(
                        np.add(
                            np.add(firstTerm, secondTerm),
                            thirdTerm
                        )
                    ),
                    np.power(
                        np.add(
                            np.add(
                                np.square(xFirstDerivValues),
                                np.square(yFirstDerivValues)
                            ),
                            np.square(zFirstDerivValues)
                        ),
                    powers
                    )                                         
                )
    return curvatureArray3d

def parameteric_splines_2d_curvature(xSpline, ySpline, sValues):
    xFirstDerivValues, xSecondDerivValues = get_derivative_values(xSpline,
                                                                  sValues)
    yFirstDerivValues, ySecondDerivValues = get_derivative_values(ySpline,
                                                                  sValues)
    curvatureArray2d = compute_curvature_array_2d(
            xFirstDerivValues, xSecondDerivValues,
            yFirstDerivValues, ySecondDerivValues)            
    return curvatureArray2d

def parameteric_splines_3d_curvature(xSpline, ySpline, zSpline, sValues):
    xFirstDerivValues, xSecondDerivValues = get_derivative_values(xSpline,
                                                                  sValues)
    yFirstDerivValues, ySecondDerivValues = get_derivative_values(ySpline,
                                                                  sValues)
    zFirstDerivValues, zSecondDerivValues = get_derivative_values(zSpline,
                                                                  sValues)
    curvatureArray3d = compute_curvature_array_3d(
            xFirstDerivValues, xSecondDerivValues,
            yFirstDerivValues, ySecondDerivValues,
            zFirstDerivValues, zSecondDerivValues)            
    return curvatureArray3d

def parametric_splines_vertical_and_lateral_curvatures(xSpline, ySpline,
                                                       zSpline, sValues):    
    xFirstDerivValues, xSecondDerivValues = get_derivative_values(xSpline,
                                                                  sValues)
    yFirstDerivValues, ySecondDerivValues = get_derivative_values(ySpline,
                                                                  sValues)
    zFirstDerivValues, zSecondDerivValues = get_derivative_values(zSpline,
                                                                  sValues)    
    verticalCurvatureARray = compute_explicit_curvature(zFirstDerivValues,
                                                        zSecondDerivValues)
    lateralCurvatureArray = compute_curvature_array_2d(        
                 xFirstDerivValues, xSecondDerivValues,
                 yFirstDerivValues, ySecondDerivValues)            
    return [verticalCurvatureArray, lateralCurvatureArray]    

def curvature_array_to_max_allowed_vels(curvatureArray, accelConstraint):
    maxAllowedVels = np.sqrt(
                            np.divide(accelConstraintArray,
                                            curvatureArray)
                           )
    return maxAllowedVels

def vertical_curvature_array_to_max_allowed_vels(verticalCurvatureArray):
    maxAllowedVels = curvature_array_to_max_allowed_vels(
            verticalCurvatureArray, config.verticalAccelConstraint)
    return maxAllowedVels

def lateral_curvature_array_to_max_allowed_vels(lateralCurvatureArray):
    maxAllowedVels = curvature_array_to_max_allowed_vels(
              lateralCurvatureArray, config.lateralAccelConstraint)
    return maxAllowedVels

def curvature_array_3d_to_max_allowed_vels(curvatureArray3d):
    maxAllowedvels = curvature_array_to_max_allowed_vels(
                       curvatureArray3d, config.totalAccelConstraint)
    return maxAllowedvels

def effective_max_allowed_vels(xSpline, ySpline, zSpline, sValues):
    verticalCurvatureArray, lateralCurvatureArray = \
        parametic_splines_vertical_and_lateral_curvature(xSpline, ySpline,
                                                         zSpline, sValues)
    maxAllowedVels_vertical = \
        vertical_curvature_array_to_max_allowed_vels(
                                    verticalCurvatureArray) 
    maxAllowedVels_lateral = \
        lateral_curvature_array_to_max_allowed_vels(
                                    lateralCurvatureArray)
    effectiveMaxAllowedVels = np.minimum(maxAllowedVels_vertical,
                                         maxAllowedVels_lateral) 
    return effectiveMaxAllowedVels

def points_3d_local_max_allowed_vels(points3d):
    xSpline, ySpline, zSpline, sValues = interpolate_points_3d(points3d)
    localMaxAllowedVels = effective_max_allowed_vels(xSpline, ySpline, zSpline,
                                                                       sValues)
    return localMaxAllowedVels

def is_curvature_valid(curvatureArray, curvatureThreshhold):
    curvatureSize = curvatureArray.size
    curvatureThreshholdArray = np.empty(curvatureSize)
    curvatureThreshholdArray.fill(curvatureThreshhold)
    absoluteCurvatureArray = np.absolute(curvatureArray)
    relativeCurvatureArray = np.subtract(absoluteCurvatureArray,
                                         curvatureThreshholdArray)
    excessCurvatureArray = relativeCurvatureArray.clip(min=0)
    totalExcessCurvature = np.sum(excessCurvatureArray)
    isCurvatureValid = (totalExcessCurvature == 0)
    return isCurvatureValid    

"""
def curvature_metric(graphCurvatureArray):
    curvatureSize = graphCurvatureArray.size
    curvatureThreshhold = np.empty(curvatureSize)
    curvatureThreshhold.fill(config.curvatureThreshhold)
    absoluteCurvature = np.absolute(graphCurvatureArray)
    relativeCurvature = np.subtract(absoluteCurvature, curvatureThreshhold)
    excessCurvature = relativeCurvature.clip(min=0)
    curvatureMetric = np.sqrt(np.mean(np.square(excessCurvature)))
    return curvatureMetric * 10**10

def graph_curvature(graphPoints, graphSampleSpacing):
    graphEdges = points_to_edges(graphPoints)
    sampledGraphPoints = sample_edges(graphEdges, graphSampleSpacing)
    xArray, yArray = points_to_arrays(sampledGraphPoints)
    numPoints = xArray.size
    sValues = get_sValues(numPoints)
    xSpline, ySpline = interpolating_splines(xArray, yArray, sValues)
    graphCurvatureArray = splines_curvature(xSpline, ySpline, sValues)
    graphCurvature = curvature_metric(graphCurvatureArray)
    return graphCurvature
"""
     
