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
#import computev2

def build_directions(start, end):
    directionsLatLng = directions.get_directions(start, end)
    startLatLng, endLatLng = util.get_firstlast(directionsLatLng)
    proj.set_projection(startLatLng, endLatLng)
    directionsPoints = proj.latlngs_to_geospatials(directionsLatLng,
                                                   config.proj)
    plottableDirections = [zip(*directionsPoints), 'k-'] 
    config.plotQueue.append(plottableDirections)
    return directionsPoints

def build_lattice(directionsPoints):
    t0 = time.time()
    directionsEdges = util.to_pairs(directionsPoints)   
    sampledPoints = lattice.sample_edges(directionsEdges,
                             config.directionsSampleSpacing)
    xSpline, ySpline = lattice.get_spline(sampledPoints)    
    splineTValues = lattice.get_tvalues(len(sampledPoints))
    splineValues = lattice.get_splinevalues(xSpline, ySpline, splineTValues)
    plottableSpline = [splineValues, 'r-']
    config.plotQueue.append(plottableSpline)
    #curvature = lattice.get_curvature(xSpline, ySpline, splineTValues)
    sliceTValues = lattice.get_slicetvalues(splineTValues,
                                  config.splineSampleSpacing)
    newLattice = lattice.get_lattice(sliceTValues, sampledPoints,
                                               xSpline, ySpline)    
    latticeSlices = newLattice.latticeSlices
    t1 = time.time()
    print("Building the lattice took " + str(t1-t0) + " seconds.")
    return latticeSlices

#    config.degreeConstraint = min(math.fabs(math.pi - math.acos(min((config.distanceBtwnSlices*(config.gTolerance/330**2))**2/2-1,1))),math.pi)*(180./math.pi)

def build_graphs(latticeSlices):
    t0 = time.time()
    finishedEdgesSets = edges.get_edgessets(latticeSlices)
    #print(util.list_of_lists_len(finishedEdgesSets))
    #print(len(finishedEdgesSets))
    completeGraphs = graphs.get_graphs(finishedEdgesSets)
    plottableGraphs = [graph.to_plottable('b-') for graph in completeGraphs]
    config.plotQueue.append(random.choice(plottableGraphs))
    t1 = time.time()
    print("Building the graphs took " + str(t1-t0) + " seconds.")
    return completeGraphs

def pair_analysis(start,end):
    cacher.create_necessaryfolders(start, end)
    t0 = time.time()
    directionsPoints = build_directions(start, end)
    latticeSlices = build_lattice(directionsPoints)
    completeGraphs = build_graphs(latticeSlices)
    #fullRoutes = [computev2.route_to_fullRoute(route) for route in filteredRoutes] 
    t1 = time.time()
    print("Analysis of this city pair took " + str(t1-t0) + " seconds.")
    if config.visualMode:
        visualize.plot_objects(config.plotQueue)
    return 0
