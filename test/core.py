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

#Our Modules:
import config
import directions
import edges
import routes
import cacher
import visualize
import computev2
import util
import proj
import lattice

def build_directions(start, end):
    directionsLatLng = directions.get_directions(start, end)
    startLatLng, endLatLng = util.get_firstlast(directionsLatLng)
    proj.set_projection(startLatLng, endLatLng)
    directionsPoints = proj.latlngs_to_geospatials(directionsLatLng,
                                                   config.proj)
    #print(util.get_firstlast(directionsPoints))
    return directionsPoints

def build_lattice(directionsPoints):
    t0 = time.time()
    directionsEdges = util.to_pairs(directionsPoints)   
    sampledPoints = lattice.sample_edges(directionsEdges,
                             config.directionsSampleSpacing)
    xSpline, ySpline = lattice.get_spline(sampledPoints)    
    splineTValues = lattice.get_tvalues(len(sampledPoints))
    splineValues = lattice.get_splinevalues(xSpline, ySpline, splineTValues)
    curvature = lattice.get_curvature(xSpline, ySpline, splineTValues)
    sliceTValues = lattice.get_slicetvalues(splineTValues,
                                  config.splineSampleSpacing)
    geospatialLattice = lattice.get_lattice(sliceTValues, sampledPoints,
                                               xSpline, ySpline)    
    t1 = time.time()
    print("Building the lattice took " + str(t1-t0) + " seconds.")
    #if config.visualMode:
    #    visualize.plot_objects([
    #    [zip(*sampledPoints), 'go', 1,1],
    #    [splineValues, 'r-', 1, 1],
    #    [curvature, '-', 2, 1],
    #    [geospatialLattice.plottableSlices, 'bo', 1, 2],
    #    [geospatialLattice.plottableSlices, 'b-', 1, 2]
    #    ])
    return geospatialLattice

#    config.degreeConstraint = min(math.fabs(math.pi - math.acos(min((config.distanceBtwnSlices*(config.gTolerance/330**2))**2/2-1,1))),math.pi)*(180./math.pi)

def build_routes(geospatialLattice):
    #finishedEdgesSets, plottableFinishedEdges = edges.get_edgessets(
    #                                           geospatialLattice.latticeSlices)
    finishedEdgesSets = edges.get_edgessets(geospatialLattice.latticeSlices)
    filteredRoutes = routes.get_routes(finishedEdgesSets)
    if config.visualMode:
        visualize.plot_colorful_objects(plottableFinishedEdges)    
    
    return 0 #filteredRoutes

def pair_analysis(start,end):
    cacher.create_necessaryfolders(start, end)
    t0 = time.time()
    directionsPoints = build_directions(start, end)
    latticeSlices = build_lattice(directionsPoints)
    filteredRoutes = build_routes(latticeSlices)
    #fullRoutes = [computev2.route_to_fullRoute(route) for route in filteredRoutes] 
    t1 = time.time()
    print("Analysis of this city pair took " + str(t1-t0) + " seconds.")
    return 0
