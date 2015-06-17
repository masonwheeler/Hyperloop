import time

import config
import database
import boundingpolygon
import lattice
import edges
import genroutes

def build_lattice(start,end):
    bounds,startLatLng,endLatLng = boundingpolygon.bounding_polygon(start,end)
    boundsXY,startXY,endXY = lattice.project_bounds(bounds,startLatLng,endLatLng)
    lattice.set_params(startXY,endXY)
    transformedBounds = lattice.transform_bounds(boundsXY,startXY,endXY)
    baseLattice = lattice.base_lattice(transformedBounds)
    finishedLattice = lattice.attach_lnglats(baseLattice)    
    return finishedLattice

def get_routes(finishedLattice): 
    edgessets = edges.get_edgessets(finishedLattice)
    #routessets = genroutes.edgessets_to_routessets(edgessets)
    #filteredRoutes = genroutes.recursivemerge_routessets(routessets)
    return 0 #filteredRoutes

def pair_analysis(start,end):
    t0 = time.time()
    finishedLattice = build_lattice(start,end)
    filteredRoutes = get_routes(finishedLattice)
    t1 = time.time()
    print("Analysis of a single pair took " + str(t1-t0) + " seconds.")
    return 0
