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
routes = gen_routes(latticeWithCost, angles, degreeConstaint, numPaths)[0:3]
routesPoints = [route.points for route in routes]
routes_Longlat = [[point[2] for point in routePoints] for routePoints in routesPoints]
print "Computing comfort and triptime..."
goodies = [[] for index in range(3)]
n = 0
for i in range(len(routes_Longlat)):
  n += 1
  print "Attaching comfort and triptime to "+ str(n) + "th route..."
  goodies[i] = [compute.comfort_and_Triptime(routes_Longlat[i])]
goodies = [good[0] for good in goodies]
print goodies
route_comforts, route_triptimes = zip(*goodies)
print "Computing land cost..."
route_costs = [route.cost for route in routes]
print "Formatting results..."
results = zip(route_costs, route_comforts, route_triptimes)
def comfortToActual(comfort_rating):
   if comfort_rating < 1:
     return "not noticeable"
   elif comfort_rating < 2:
     return "just noticeable"
   elif comfort_rating < 2.5:
     return "clearly noticeable"
   elif comfort_rating < 3:
     return "more pronounced but not unpleasant"
   elif comfort_rating < 3.25:
     return "strong, irregular, but still tolerable"
   elif comfort_rating < 3.5:
     return "very irregular"
   elif comfort_rating < 4:
     return "extremely irregular, unpleasant, annoying; prolonged exposure intolerable"
   else:
     return "extremely unpleasant; prolonged exposure harmful"
results = [["Route #"+str(i),str(results[i][0])+" billion USD",comfortToActual(results[i][1]),str(results[i][2]/60)+" minutes"] for i in range(len(results))]
print results
