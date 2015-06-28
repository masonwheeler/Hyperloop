import time

import config
import database
import directions
import boundingpolygon
import lattice
import edges
import routes
import cacher
import visualize
import import_export as io
import compute

def build_lattice(start,end):
    directionsCoords = directions.get_directions(start, end)
    startLatLng, endLatLng = directionsCoords[0], directionsCoords[-1]
    lattice.set_projection(startLatLng, endLatLng)
    startXY, endXY = lattice.project_startend(startLatLng, endLatLng)
    boundingPolygon = boundingpolygon.get_boundingpolygon(directionsCoords)
    boundsXY = lattice.get_boundsxy(boundingPolygon)
    lattice.set_params(startXY,endXY)
    latticeBounds = lattice.get_latticebounds(boundsXY)
    baseLattice, envelope = lattice.get_baselattice(latticeBounds)
    lnglatLattice = lattice.get_lnglatlattice(baseLattice)
    finishedLattice,rightOfWay = lattice.get_rightofway(lnglatLattice,
                                                      directionsCoords)
    if config.visualMode:
        visualize.plot_polygon(boundingPolygon)
    return finishedLattice, envelope

def build_routes(finishedLattice, envelope): 
    edgesSets = edges.get_edgessets(finishedLattice, envelope)    
    filteredRoutes = routes.get_routes(edgesSets)
    return filteredRoutes

def pair_analysis(start,end):
    cacher.create_necessaryfolders(start, end)
    t0 = time.time()
    build_lattice(start, end)
    lattice, envelope = build_lattice(start,end)
    filteredRoutes = build_routes(lattice, envelope)
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
    t1 = time.time()
    print("Analysis of this city pair took " + str(t1-t0) + " seconds.")
    return 0
