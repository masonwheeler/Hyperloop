import config
import database
import boundingpolygon
import lattice_David
import routes
import time
import filterroutes
import compute

def pair_analysis(start,end):
    bounds,startLatLng,endLatLng = boundingpolygon.bounding_polygon(start,end)
    boundsXY,startXY,endXY = lattice_David.project_bounds(bounds,startLatLng,endLatLng)
    lattice_David.set_params(startXY,endXY)
    transformedBounds = lattice_David.transform_bounds(boundsXY,startXY,endXY)
    baseLattice, angles, ySpacing = lattice_David.base_lattice(transformedBounds)
    latticeWithLngLats,xPrimVec,yPrimVec = lattice_David.attach_lnglats(baseLattice)
    latticeWithCost = lattice_David.attach_cost(config.geotiffFilePath,
    	latticeWithLngLats,config.coordinatesList,xPrimVec)
    #routes.
    return [latticeWithCost, angles]

def gen_routes(latticeWithCost, angles, degreeConstaint, numPaths):
    pairs = filterroutes.get_pairs(latticeWithCost, angles)
    routes = filterroutes.treefold(pairs, degreeConstaint, angles, numPaths)
    return routes

start = "Los_Angeles"
end = "San_Francisco"
degreeConstaint = 60
numPaths = 50 #max = 500.
latticeWithCost, angles = pair_analysis(start,end)
routes = gen_routes(latticeWithCost, angles, degreeConstaint, numPaths)
routesPoints = [route.points for route in routes]
routes_Longlat = [[point[2] for point in routePoints] for routePoints in routesPoints]
print "Computing comfort and triptime..."
goodies = []
n = 0
for Longlat in routes_Longlat:
  n += 1
  print "Attaching comfort and triptime to "+ str(n) + "th route."
  goodies += compute.comfort_and_Triptime(Longlat)
route_comforts, route_triptimes = zip([compute.comfort_and_Triptime(Longlat) for Longlat in routes_Longlat])
print "Computing land cost..."
route_costs = [route.cost for route in routes]
print "Formatting results..."
results = zip(route_costs, route_comforts, route_triptimes)
print results
