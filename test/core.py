import time

import config
import database
import boundingpolygon
import lattice
import edges
import genroutes
import import_export as io
import itertools

def build_lattice(start,end):
    bounds,startLatLng,endLatLng = boundingpolygon.bounding_polygon(start,end)
    boundsXY,startXY,endXY = lattice.project_bounds(bounds,startLatLng,endLatLng)
    print "exporting polygon..."
    io.export(boundsXY,'polygon')
    lattice.set_params(startXY,endXY)
    transformedBounds = lattice.transform_bounds(boundsXY,startXY,endXY)
    baseLattice, envelope = lattice.base_lattice(transformedBounds)
    lnglatLattice = lattice.attach_lnglats(baseLattice)    
    finishedLattice = lattice.add_rightOfWay(lnglatLattice, config.directionsCoords)
    print "exporting lattice..."
    flattenedLattice = itertools.chain(*finishedLattice)
    latticeXY = [point.xyCoords for point in flattenedLattice]
    io.export(latticeXY,'lattice')
    return finishedLattice, envelope

def get_routes(finishedLattice, envelope): 
    edgessets = edges.build_edgessets(finishedLattice, envelope)    
    #routessets = genroutes.edgessets_to_routessets(edgessets)
    #filteredRoutes = genroutes.recursivemerge_routessets(routessets)
    return 0 #filteredRoutes

def pair_analysis(start,end):
    t0 = time.time()
    finishedLattice, envelope = build_lattice(start,end)
    routes = get_routes(finishedLattice, envelope)
    t1 = time.time()
    print("Analysis of this city pair took " + str(t1-t0) + " seconds.")
    return 0
