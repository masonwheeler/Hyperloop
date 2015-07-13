import time
import transform
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
import computev2
import util
import math

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
    angle, sizeFactor, startPoint = transform.get_params(startLatLng,endLatLng)
    config.distanceBtwnSlices = util.norm(transform.transform_point(angle, sizeFactor, startPoint, [config.latticeXSpacing, 0]))
    config.degreeConstraint = min(math.fabs(math.pi - math.acos(min((config.distanceBtwnSlices*(config.gTolerance/330**2))**2/2-1,1))),math.pi)*(180./math.pi)
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
    fullRoutes = [computev2.route_to_fullRoute(route) for route in filteredRoutes] 
    t1 = time.time()
    print("Analysis of this city pair took " + str(t1-t0) + " seconds.")
    return 0
