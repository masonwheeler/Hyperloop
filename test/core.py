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
#import routes


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
    print("directions points start: " + str(directionsPoints[0]))
    print("directions points end: " + str(directionsPoints[-1]))
    sampledPoints = interpolate.sample_path(directionsPoints,
                              config.directionsSampleSpacing)
    print("sampled points start: " + str(sampledPoints[0]))
    print("sampled points end: " + str(sampledPoints[-1]))
    sValues = interpolate.get_s_values(len(sampledPoints))
    spatialXSpline, spatialYSpline = lattice.get_directionsspline(sampledPoints)
    spatialLatticeSlicesSValues = interpolate.get_slice_s_values(sValues,
                                              config.splineSampleSpacing)       
    spatialLatticeSlicesXValues = interpolate.get_spline_values(spatialXSpline,
                                                   spatialLatticeSlicesSValues) 
    spatialLatticeSlicesYValues = interpolate.get_spline_values(spatialYSpline,
                                                   spatialLatticeSlicesSValues) 
    spatialLatticeSlicesSplinePoints = zip(spatialLatticeSlicesXValues,
                                           spatialLatticeSlicesYValues)
    spatialLatticeSlicesDirectionsPoints = sampledPoints[
                            ::config.splineSampleSpacing]
    spatialSlicesBounds = zip(spatialLatticeSlicesDirectionsPoints,
                                  spatialLatticeSlicesSplinePoints)
    print("spatial slice bounds" + str(len(spatialSlicesBounds)))
    #latticeSlices = lattice.get_lattice(sliceSValues, sampledPoints,
    #                                            xSpline, ySpline) 
    latticeSlices = lattice.get_lattice(spatialSlicesBounds) 
    print("num lattice slices: " + str(len(latticeSlices)))
    t1 = time.time()
    print("Building the lattice took " + str(t1-t0) + " seconds.")
    if config.visualMode:
        xValues = interpolate.get_spline_values(xSpline, sValues)
        yValues = interpolate.get_spline_values(ySpline, sValues)
        plottableSpline = [[xValues, yValues], 'r-']
        config.plotQueue.append(plottableSpline)
    return latticeSlices

#    config.degreeConstraint = min(math.fabs(math.pi - math.acos(min((config.distanceBtwnSlices*(config.gTolerance/330**2))**2/2-1,1))),math.pi)*(180./math.pi)

def build_graphs(latticeSlices):
    t0 = time.time()
    finishedEdgesSets = edges.get_edgessets(latticeSlices)
    #print(len(finishedEdgesSets))
    completeGraphs = graphs.get_graphs(finishedEdgesSets)
    print("graphs num edges: " + str(completeGraphs[0].numEdges))
    #for graph in completeGraphs:
    #    print("pylon cost: " + str(graph.pylonCost))
    #    print("land cost: " + str(graph.landCost))
    #    print("curvature: " + str(graph.curvatureMetric))
    #t1 = time.time()
    #print("Building the graphs took " + str(t1-t0) + " seconds.")
    if config.visualMode:
        plottableGraphs = [graph.to_plottable('b-') for graph in completeGraphs]    
        #costCurvature = [graph.plot_costcurvature() for graph in completeGraphs]
        #costs, curvatures = zip(*costCurvature)
        #visualize.scatter_plot(costs, curvatures)
        #print(plottableCostCurvature)
        config.plotQueue += plottableGraphs
        #config.plotQueue += plottableCostCurvature
    return completeGraphs

def pair_analysis(start,end):
    cacher.create_necessaryfolders(start, end)
    t0 = time.time()
    directionsPoints = build_directions(start, end)
    latticeSlices = build_lattice(directionsPoints)
    completeGraphs = build_graphs(latticeSlices)

    _2Droute = routes.graph_to_2Droute(completeGraphs[0])
    _3Droute = routes._2Droute_to_3Droute(_2Droute)


    #Test genLandscape( , "elevation"):
#    print "extracting geospatials of a single graph..."
#    x = completeGraphs[0].geospatials
#    print "converting geospatials from strings to floats..."
#    x = [[float(p[0]),float(p[1])] for p in x]
#    print "interpolating the geospatials..."
#    x = interp.paraSuperQ(x, 25)
#    print "generating the landscape..."
#    s, z = match.genLandscape(x, "elevation")
#    print "plotting the landscape..."
#    visualize.scatter_plot(s, z)

    """
    #Test genLandscape( , "velocity"):
    print "extracting geospatials of a single graph..."
    x = completeGraphs[0].geospatials
    print "converting geospatials from strings to floats..."
    x = [[float(p[0]),float(p[1])] for p in x]
    print "interpolating the geospatials..."
    x = interp.paraSuperQ(x, 25)
    print "generating the landscape..."
    s, v = match.genLandscape(x, "velocity")
    print "plotting the landscape..."
    visualize.scatter_plot(s, v)
    """


    t1 = time.time()
    print("Analysis of this city pair took " + str(t1-t0) + " seconds.")
    if config.visualMode:
        visualize.plot_objects(config.plotQueue)
    return 0
