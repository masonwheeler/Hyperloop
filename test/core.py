"""
Original Developer: Jonathan Ward
Purpose of Module: To perform the core computations for each city pair.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To remove unnecessary imports.
"""

#Standard Modules:
import time
import math
import random

#Our Modules:
import config
import util
import visualize
import cacher
import directions
import proj
import lattice
import edges
import graphs
import interpolate
# import match_landscape as match
# import advanced_interpolate as interp
import routes


def build_directions(start, end):    
    directionsLatLngs = directions.get_directions(start, end)
    startLatLng, endLatLng = util.get_firstlast(directionsLatLngs)
    proj.set_projection(startLatLng, endLatLng)
    directionsPoints = proj.latlngs_to_geospatials(directionsLatLngs,
                                                   config.proj)
    if config.visualMode:
        plottableDirections = [zip(*directionsPoints), 'y-'] 
        config.plotQueue.append(plottableDirections)
    return directionsPoints

def build_lattice(directionsPoints):
    t0 = time.time()
    sampledPoints = interpolate.sample_path(directionsPoints,
                              config.directionsSampleSpacing)
    sValues = interpolate.get_s_values(len(sampledPoints))
    spatialXSpline, spatialYSpline = lattice.get_directionsspline(sampledPoints)
    spatialLatticeSlicesSValues = interpolate.get_slice_s_values(sValues,
                                     config.spatialSliceSValueStepSize)       
    spatialLatticeSlicesXValues = interpolate.get_spline_values(spatialXSpline,
                                                   spatialLatticeSlicesSValues) 
    spatialLatticeSlicesYValues = interpolate.get_spline_values(spatialYSpline,
                                                   spatialLatticeSlicesSValues) 
    spatialLatticeSlicesSplinePoints = zip(spatialLatticeSlicesXValues,
                                           spatialLatticeSlicesYValues)
    spatialLatticeSlicesDirectionsPoints = util.smart_sample_nth_points(
                           sampledPoints, config.spatialSliceSValueStepSize)
    spatialSlicesBounds = zip(spatialLatticeSlicesDirectionsPoints,
                                  spatialLatticeSlicesSplinePoints)
    latticeSlices = lattice.get_lattice(spatialSlicesBounds) 
    t1 = time.time()
    print("Building the lattice took " + str(t1-t0) + " seconds.")
    if config.visualMode:
        splineXValues = interpolate.get_spline_values(spatialXSpline, sValues)
        splineYValues = interpolate.get_spline_values(spatialYSpline, sValues)
        plottableSpline = [[splineXValues, splineYValues], 'r-']
        config.plotQueue.append(plottableSpline)
    return latticeSlices

#    config.degreeConstraint = min(math.fabs(math.pi - math.acos(min((config.distanceBtwnSlices*(config.gTolerance/330**2))**2/2-1,1))),math.pi)*(180./math.pi)

def build_graphs(latticeSlices):
    t0 = time.time()
    finishedEdgesSets = edges.get_edgessets(latticeSlices)
    t2 = time.time()
    edges.build_pylons(finishedEdgesSets)
    t3 = time.time()
    print("Building the pylons took " + str(t3 - t2) + " seconds.")
    completeGraphs = graphs.get_graphs(finishedEdgesSets)
    #print("graphs num edges: " + str(completeGraphs[0].numEdges))
    #for graph in completeGraphs:
    #    print("pylon cost: " + str(graph.pylonCost))
    #    print("land cost: " + str(graph.landCost))
    #    print("curvature: " + str(graph.curvatureMetric))
    t1 = time.time()
    print("Building the graphs took " + str(t1-t0) + " seconds.")
    #if config.visualMode:
    #    plottableGraphs = [graph.to_plottable('b-') for graph in completeGraphs]    
        #costCurvature = [graph.plot_costcurvature() for graph in completeGraphs]
        #costs, curvatures = zip(*costCurvature)
        #visualize.scatter_plot(costs, curvatures)
        #print(plottableCostCurvature)
        #config.plotQueue += plottableGraphs
        #config.plotQueue += plottableCostCurvature
    return completeGraphs

#def build_routes(completeGraphs):
    

def pair_analysis(start,end):
    cacher.create_necessaryfolders(start, end)
    t0 = time.time()
    directionsPoints = build_directions(start, end)
    latticeSlices = build_lattice(directionsPoints)
    completeGraphs = build_graphs(latticeSlices)
    completeRoutes = [routes.graph_to_route(graph) for graph in completeGraphs]
    

    t1 = time.time()
    print("Analysis of this city pair took " + str(t1-t0) + " seconds.")
    if config.visualMode:
        visualize.plot_objects(config.plotQueue)
    return 0
