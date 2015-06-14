import config
import database
import boundingpolygon
import lattice_David
import routes
import time
import filterroutes
import compute
import math

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

def fetch_Interpolation_Data(route):
  routePoints = route.waypoints
  thtiphii = [[(2*math.pi/360)*point[2][0],(2*math.pi/360)*point[2][1]] for point in routePoints]
  return compute.interpolation_data(thtiphii)

start = "Los_Angeles"
end = "San_Francisco"
degreeConstaint = 60
numPaths = 50 #max = 500.
latticeWithCost, angles = pair_analysis(start,end)
routes = gen_routes(latticeWithCost, angles, degreeConstaint, numPaths)
print "Computing comfort and triptime..."
n = 0
for route in routes:
  n += 1
  print "Attaching comfort and triptime to "+ str(n) + "th route..."
  route.comfort, route.triptime, route.plot_times, route.points, route.vel_points, route.accel_points = fetch_Interpolation_Data(route)
print [route.comfort for route in routes]






