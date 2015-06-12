import config
import database
import boundingpolygon
import lattice_David
import routes
import time
import filterroutes

def pair_analysis(start,end):
    bounds,startLatLng,endLatLng = boundingpolygon.bounding_polygon(start,end)
    boundsXY,startXY,endXY = lattice_David.project_bounds(bounds,startLatLng,endLatLng)
    lattice.set_params(startXY,endXY)
    transformedBounds = lattice_David.transform_bounds(boundsXY,startXY,endXY)
    baseLattice, angles = lattice_David.base_lattice(transformedBounds)
    latticeWithLngLats,xPrimVec,yPrimVec = lattice_David.attach_lnglats(baseLattice)
    latticeWithCost = lattice_David.attach_cost(config.geotiffFilePath,
    	latticeWithLngLats,config.coordinatesList,xPrimVec)
    #routes.
    return [latticeWithCost, angles]

def sample_route(lattice, angles):
    pairs = filterroutes.get_pairs(lattice, angles)
    routes = filterroutes.treefold(pairs, degreeConstaint, angles, numPaths):
    sampleRoute = routes[0]
    return sampleRoute


start = "Los_Angeles"
end = "San_Francisco"
lattice, angles = pair_analysis(start,end):
print sample_route(lattice, angles) 