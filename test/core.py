import time

import config
import database
import directions
import boundingpolygon
import lattice
import edges
import genroutes
import cacher
#import import_export as io
#import itertools

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
    #print(baseLattice)
    lnglatLattice = lattice.get_lnglatlattice(baseLattice)
    #print(lnglatLattice)
    rightofwayLattice = lattice.get_rightofway(lnglatLattice, directionsCoords)
    #print "exporting lattice..."
    #flattenedLattice = itertools.chain(*finishedLattice)
    #latticeXY = [point.xyCoords for point in flattenedLattice]
    #io.export(latticeXY,'lattice')
    return rightofwayLattice, envelope
"""
def get_routes(finishedLattice, envelope): 
    edgesSets = edges.build_edgessets(finishedLattice, envelope)    
    #routesSets = genroutes.edgessets_to_routessets(edgesSets)
    #filteredRoutes = genroutes.recursivemerge_routessets(routesSets)
    return filteredRoutes
"""
def pair_analysis(start,end):
    cacher.create_necessaryfolders(start, end)
    t0 = time.time()
    build_lattice(start, end)
    #finishedLattice, envelope = build_lattice(start,end)
    #routes = get_routes(finishedLattice, envelope)
    #for i in range(10):
    #   io.export(routes[i].xyCoords,'route'+str(i))
    t1 = time.time()
    print("Analysis of this city pair took " + str(t1-t0) + " seconds.")
    return 0
