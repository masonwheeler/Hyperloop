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
  return compute.interpolation_data(route.xyCoords)

def outputRoutes(start,end,degreeConstaint,numPaths):
  latticeWithCost, angles = pair_analysis(start,end)
  routes = gen_routes(latticeWithCost, angles, degreeConstaint, numPaths)
  print "Computing comfort and triptime..."
  n = 0
  for route in routes:
    n += 1
    print "Attaching comfort and triptime to "+ str(n) + "th route..."
    route.comfort, route.triptime, route.plot_times, route.points, route.vel_points, route.accel_points = fetch_Interpolation_Data(route)
    route.waypoints = [point[2] for point in route.waypoints]
  return routes


print "outputRoutes(start,end,degreeConstaint,numPaths)"



