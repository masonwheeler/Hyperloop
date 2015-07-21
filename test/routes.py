"""
Original Developer: Jonathan Ward
Purpose of Module: To generate routes from the lattice edges.
Last Modified: 7/16/16
Last Modified By: Jonathan Ward
Last Modification Purpose: To connect the curvature information.
"""

import random
import numpy as np

import genVelocity as gen
import config
import util
import cacher

# xPointstovPoints(): 
# Outputs a discrete velocity profile {v_i} given a discrete route {x_i}.
# The velocity profile v is a rolling average of the maximum speed allowed by a .3g radial acceleration constraint:
#       v_i = (1/2k) * sum_{i-k <j< i+k} sqrt(.3g * r_j).
# where r_j is the radius of the circle through {x_{j-1},x_j, x_{j+1}}.

def xPointstovPoints(x):
    v = [min(np.sqrt(9.81*.3*gen.points_to_radius(x[0:3])),330)] + [min(np.sqrt(9.81*.3*gen.points_to_radius(x[0:3])),330)] + [gen.mean([min(np.sqrt(9.81*.3*gen.points_to_radius(x[j-1:j+2])),330) for j in range(2-1,2+2)])] + [gen.mean([min(np.sqrt(9.81*.3*gen.points_to_radius(x[j-1:j+2])),330) for j in range(i-2,i+3)]) for i in range(3,-4)] + [gen.mean([min(np.sqrt(9.81*.3*gen.points_to_radius(x[j-1:j+2])),330) for j in range(-3-1,-3+2)])] + [min(np.sqrt(9.81*.3*gen.points_to_radius(x[-3:len(x)])),330)] + [min(np.sqrt(9.81*.3*gen.points_to_radius(x[-3:len(x)])),330)]
    return v

# vPointsto_triptime(): 
# Outputs triptime T of a discrete route {x_i} given its discrete velocity profile {v_i}.
# The triptime is computed assuming a piecewise linear interpolation of the {x_i} (into a set of line-segments),
# and assuming that the velocity in the segment connecting x_i to x_{i+1} is v_i:
#      T = sum_i s_i/v_i
# where s_i is the distance between x_i and x_{i+1}.

def vPointsto_triptime(v, x):
    s = [np.linalg.norm(x[i+1]-x[i]) for i in range(-1)]
    return sum([s[i]/v[i] for i in range(len(s))])



def variation(route):
    
    route



class Route:
    pylonCost = 0
    landCost = 0
    startAngle = 0
    endAngle = 0
    startId = 0
    endId = 0
    geospatialCoords = []
    heights = [[]]

    def __init__(self, pylonCost, landCost, startId, endId, startAngle,
                 endAngle, latlngCoords, geospatialCoords, heights):
        self.pylonCost = pylonCost
        self.landCost = landCost
        self.startId = startId
        self.endId = endId
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.latlngCoords = latlngCoords
        self.geospatialCoords = geospatialCoords
        self.heights = heights

    def to_plottable(self):
        return zip(*self.geospatialCoords)

    def display(self):     
        print("The route cost is: " + str(self.cost) + ".")
        print("The route start angle is: " + str(self.startAngle) + ".")        
        print("The route end angle is: " + str(self.endAngle) + ".")


def is_route_pair_compatible(routeA, routeB):
    if (routeA.endId == routeB.startId):
        if abs(routeA.endAngle - routeB.startAngle) < config.degreeConstraint:
            return True
    return False

def merge_two_routes(routeA,routeB):
    pylonCost = routeA.pylonCost + routeB.pylonCost
    landCost = routeA.landCost + routeB.landCost
    startId = routeA.startId
    heights = routeA.heights + routeB.heights
    startId = routeA.startId
    startAngle = routeA.startAngle
    endId = routeB.endId
    endAngle = routeB.endAngle
    latlngCoords = util.smart_concat(routeA.latlngCoords, routeB.latlngCoords)
    geospatialCoords = util.smart_concat(routeA.geospatialCoords,
                                         routeB.geospatialCoords)
    newRoute = Route(pylonCost, landCost, startId, endId, startAngle, endAngle,
                     latlngCoords, geospatialCoords, heights)
    return newRoute

def edge_to_route(edge):
    pylonCost = edge.pylonCost
    landCost = edge.landCost
    startId = edge.startId
    endId = edge.endId
    startAngle = endAngle = edge.angle
    latlngCoords = edge.latlngCoords
    geospatialCoords = edge.geospatialCoords
    heights = [edge.heights]
    newRoute = Route(pylonCost, landCost, startId, endId, startAngle, endAngle,
                     latlngCoords, geospatialCoords, heights)
    return newRoute

def edgesset_to_routesset(edgesSet):
    return [edge_to_route(edge) for edge in edgesSet]

def edgessets_to_routessets(edgesSets):
    return [edgesset_to_routesset(edgesSet) for edgesSet in edgesSets]

# Filters routes 

def sample_routes(merged):
    n = int(np.log2(len(merged[0].geospatialCoords)))
    print len(merged[0].geospatialCoords)
    print n
    if n > 3:
       velocityProfiles = [xPointstovPoints(route.geospatialCoords) for route in merged]
       variations = [sum([np.absolute(v[i+1]-v[i]) for i in range(-1)]) for v in velocityProfiles]
       triptimes = [vPointsto_triptime(velocityProfiles[i], merged[i].geospatialCoords) for i in range(len(merged))]
       costs = [route.landCost+route.pylonCost for route in merged]
       merged = filter(merged, lambda route: variations[merged.index(route)] < 9.81 * .1 * 2**n)
       merged.sort(key = lambda route: (route.landCost+route.pylonCost) * triptimes[merged.index(route)])
       selected = merged[:config.numPaths[n-1]]
    else:
       merged.sort(key = lambda route: route.landCost+route.pylonCost)
       selected = merged[:config.numPaths[n-1]]
    return selected

def merge_two_routessets(routesSetA, routesSetB):
#    print "Merging two adjacent slices of length-"+str(len(routesSetA[0].xyCoords))+"routes"
    merged = []
    for routeA in routesSetA:
        for routeB in routesSetB:
            if is_route_pair_compatible(routeA,routeB):            
                merged.append(merge_two_routes(routeA,routeB))
    if (merged == []):
        print(len(routesSetA))
        for routeA in routesSetA:
          print(routeA.endId,routeA.geospatialCoords)
        print(len(routesSetB))    
        for routeB in routesSetB:
          print(routeB.startId,routeB.geospatialCoords)
        raise ValueError('No compatible routes')        
    return sample_routes(merged)

def recursivemerge_routessets(routesSets):
#    print "Merging "+str(len(routesSets)) + "sets of routes."
#    print "the number of routes in each set is:"
#    for routeSet in routesSets:
#       print len(routeSet)
    layers = [routesSets]
    layersIndex = 0
    workingLayerIndex = 0

    numLayers = 1
    workingLayerSize = len(routesSets)
    breakFlag = False
    
    while (numLayers != 1 or workingLayerSize != 1):
        if (workingLayerSize - workingLayerIndex == 0):
            if (numLayers - layersIndex == 1):
                breakFlag = True;
            else:
                layersIndex += 1
                workingLayerIndex = 0
                workingLayerSize = len(layers[layersIndex])
        elif (workingLayerSize - workingLayerIndex == 1):
            if (numLayers - layersIndex == 1):
                breakFlag = True;
            else:
                layers[layersIndex + 1].append(
                  layers[layersIndex][workingLayerIndex])
                layersIndex += 1
                workingLayerIndex = 0
                workingLayerSize = len(layers[layersIndex])
        else:
            if (numLayers - layersIndex == 1):
                layers.append([])
                numLayers += 1
            routesSetA = layers[layersIndex][workingLayerIndex]
            routesSetB = layers[layersIndex][workingLayerIndex + 1]
            merged = merge_two_routessets(routesSetA,routesSetB)
            layers[layersIndex+1].append(merged)                
            workingLayerIndex += 2
        if breakFlag:
            break

    filteredRoutes = layers[layersIndex][0]  
    return filteredRoutes

def build_routes(edgessets):
    routesSets = edgessets_to_routessets(edgessets)
    filteredRoutes = recursivemerge_routessets(routesSets)
    return filteredRoutes
    
def get_routes(edgessets):
    routes = cacher.get_object("routes", build_routes, [edgessets],
                                cacher.save_routes, config.routesFlag)
    return routes

        
