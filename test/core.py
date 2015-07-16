import time
import transform
import config
import database
import directions
import edges
import routes
import cacher
import visualize
import import_export as io
import computev2
import util
import math

import util
import proj
import newlattice

def build_directions(start, end):
    directionsLatLng = directions.get_directions(start, end)
    startLatLng, endLatLng = util.get_firstlast(directionsLatLng)
    proj.set_projection(startLatLng, endLatLng)
    directionsPoints = proj.latlngs_to_geospatials(directionsLatLng, config.proj)
    return directionsPoints

def build_lattice(directionsPoints):
    t0 = time.time()
    directionsEdges = util.to_pairs(directionsPoints)   
    sampledPoints = newlattice.sample_edges(directionsEdges,
                             config.directionsSampleSpacing)
    xSpline, ySpline = newlattice.get_spline(sampledPoints)    
    splineTValues = newlattice.get_tvalues(len(sampledPoints))
    splineValues = newlattice.get_splinevalues(xSpline, ySpline, splineTValues)
    curvature = newlattice.get_curvature(xSpline, ySpline, splineTValues)
    sliceTValues = newlattice.get_slicetvalues(splineTValues,
                                  config.splineSampleSpacing)
    geospatialLattice = newlattice.get_lattice(sliceTValues, sampledPoints,
                                               xSpline, ySpline)    
    t1 = time.time()
    print("Building the Lattice took " + str(t1-t0) + " seconds.")
    #if config.visualMode:
    #    visualize.plot_objects([
    #    [zip(*sampledPoints), 'go', 1,1],
    #    [splineValues, 'r-', 1, 1],
    #    [curvature, '-', 2, 1],
    #    [geospatialLattice.plottableSlices, 'bo', 1, 2],
    #    [geospatialLattice.plottableSlices, 'b-', 1, 2]
    #    ])
    return geospatialLattice

#    angle, sizeFactor, startPoint = transform.get_params(startLatLng,endLatLng)
#    config.distanceBtwnSlices = util.norm(transform.transform_point(angle, sizeFactor, startPoint, [config.latticeXSpacing, 0]))
#    config.degreeConstraint = min(math.fabs(math.pi - math.acos(min((config.distanceBtwnSlices*(config.gTolerance/330**2))**2/2-1,1))),math.pi)*(180./math.pi)
#    if config.visualMode:
#        visualize.plot_polygon(boundingPolygon)

def build_routes(geospatialLattice):
    edgesSets = edges.build_edgessets(geospatialLattice.latticeSlices)  
    filteredEdges = edgesSets.filteredEdgesSets[-1]
    filteredRoutes = routes.get_routes(filteredEdges)
    if config.visualMode:
        #colorsList = ['r-', 'b-', 'm-', 'g-', 'k-', 'c-']
        #objectsList = [[edgesSets.plottableBaseEdges, 'y-', 1, 2]]
        #filterIterations = len(edgesSets.plottableFilteredEdges)
        #for index in range(filterIterations):
        #    objectsList.append([edgesSets.plottableFilteredEdges[index],
        #                        colorsList[index], 1, 2])
        visualize.plot_objects([
        [edgesSets.plottableFilteredEdges[-1],'k-', 1, 2],
        [filteredRoutes[0].to_plottable(), 'r-', 1, 1]
        ])        
    
    return 0 #filteredRoutes

def pair_analysis(start,end):
    cacher.create_necessaryfolders(start, end)
    t0 = time.time()
    directionsPoints = build_directions(start, end)
    latticeSlices = build_lattice(directionsPoints)
    filteredRoutes = build_routes(latticeSlices)
    """for i in range(10):
       io.export(routes[i].xyCoords,'route'+str(i))
    print "Computing comfort and triptime..."
    n = 0
    for i in range(10):
       n += 1
       print "Attaching comfort and triptime to "+ str(n) + "th route..."
       routes[i].comfort, routes[i].tripTime, routes[i].plotTimes, routes[i].points, routes[i].vel_points, routes[i].accel_points = compute.fetch_Interpolation_Data(routes[i].xyCoords, 5)
    for i in range(10):
       io.export(routes[i].points,'route'+str(i)+'points')
       print routes[i].points
       io.export(zip(routes[i].plotTimes,routes[i].vel_points),'route'+str(i)+'vel_points')
       print zip(routes[i].plotTimes,routes[i].vel_points)
       io.export(zip(routes[i].plotTimes,routes[i].accel_points),'route'+str(i)+'accel_points')
       print zip(routes[i].plotTimes,routes[i].accel_points)
       io.export(zip([0]*len(routes[i].comfort),routes[i].comfort),'route'+str(i)+'comfort')"""
    #fullRoutes = [computev2.route_to_fullRoute(route) for route in filteredRoutes] 
    t1 = time.time()
    print("Analysis of this city pair took " + str(t1-t0) + " seconds.")
    return 0
