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

def build_directions(start, end):    
    directionsLatLng = directions.get_directions(start, end)
    startLatLng, endLatLng = util.get_firstlast(directionsLatLng)
    proj.set_projection(startLatLng, endLatLng)
    directionsPoints = proj.latlngs_to_geospatials(directionsLatLng,
                                                   config.proj)
    #if config.visualMode:
    #    plottableDirections = [zip(*directionsPoints), 'y-'] 
    #    config.plotQueue.append(plottableDirections)
    return directionsPoints

def build_lattice(directionsPoints):
    t0 = time.time()
    directionsEdges = util.to_pairs(directionsPoints)   
    sampledPoints = interpolate.sample_edges(directionsEdges,
                             config.directionsSampleSpacing)
    xSpline, ySpline = lattice.get_directionsspline(sampledPoints)    
    splineTValues = interpolate.get_tvalues(len(sampledPoints))
    splineValues = interpolate.get_splinevalues(xSpline, ySpline, splineTValues)
    sliceTValues = interpolate.get_slicetvalues(splineTValues,
                                  config.splineSampleSpacing)   
    newLattice = lattice.get_lattice(sliceTValues, sampledPoints,
                                               xSpline, ySpline) 
    latticeSlices = newLattice.latticeSlices
    print(latticeSlices)
    t1 = time.time()
    print("Building the lattice took " + str(t1-t0) + " seconds.")
    #if config.visualMode:
    #    plottableSpline = [splineValues, 'r-']
    #    config.plotQueue.append(plottableSpline)
    return latticeSlices

#    config.degreeConstraint = min(math.fabs(math.pi - math.acos(min((config.distanceBtwnSlices*(config.gTolerance/330**2))**2/2-1,1))),math.pi)*(180./math.pi)

def build_graphs(latticeSlices):
    t0 = time.time()
    finishedEdgesSets = edges.get_edgessets(latticeSlices)
    print(len(finishedEdgesSets))
    completeGraphs = graphs.get_graphs(finishedEdgesSets)
    #print(completeGraphs[0].numEdges)
    #for graph in completeGraphs:
    #    print("pylon cost: " + str(graph.pylonCost))
    #    print("land cost: " + str(graph.landCost))
    #    print("curvature: " + str(graph.curvatureMetric))
    t1 = time.time()
    print("Building the graphs took " + str(t1-t0) + " seconds.")
    if config.visualMode:
        #plottableGraphs = [graph.to_plottable('b-') for graph in completeGraphs]    
        costCurvature = [graph.plot_costcurvature() for graph in completeGraphs]
        costs, curvatures = zip(*costCurvature)
        visualize.scatter_plot(costs, curvatures)
        #print(plottableCostCurvature)
        #config.plotQueue += plottableGraphs
        #config.plotQueue += plottableCostCurvature
    return completeGraphs

def pair_analysis(start,end):
    cacher.create_necessaryfolders(start, end)
    t0 = time.time()
    directionsPoints = build_directions(start, end)
    latticeSlices = build_lattice(directionsPoints)
    completeGraphs = build_graphs(latticeSlices)
    t1 = time.time()
    print("Analysis of this city pair took " + str(t1-t0) + " seconds.")
    if config.visualMode:
        visualize.plot_objects(config.plotQueue)
    return 0
