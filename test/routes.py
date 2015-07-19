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

def pointstoCurvature(threepoints):
    if gen.pointstoRadius(threepoints) == 0:
        return config.gTolerance/(config.maxSpeed**2)
    else:
        A, B, C = threepoints
        BAperp = [-(B-A)[1],(B-A)[0]]
        sign = np.dot(C-A, BAperp)
        return (sign/np.absolute(sign))*(1./gen.pointstoRadius(threepoints))

class Route:
    pylonCost = 0
    routeCost = 0
    startAngle = 0
    endAngle = 0
    startId = 0
    endId = 0
    geospatialCoords = []

    def __init__(self, pylonCost, landCost, startId, endId, startAngle,
                 endAngle, latlngCoords, geospatialCoords):
                   #, curvatures,variation, edges):
        self.pylonCost = pylonCost
        self.landCost = landCost
        self.startId = startId
        self.endId = endId
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.latlngCoords = latlngCoords
        self.geospatialCoords = geospatialCoords

    def to_plottable(self):
        return zip(*self.geospatialCoords)

    def display(self):     
        print("The route cost is: " + str(self.cost) + ".")
        print("The route start angle is: " + str(self.startAngle) + ".")        
        print("The route end angle is: " + str(self.endAngle) + ".")
        print("The route curvatures are: " + str(self.curvatures) + ".")


def is_route_pair_compatible(routeA, routeB):
    if (routeA.endId == routeB.startId):
        if abs(routeA.endAngle - routeB.startAngle) < config.degreeConstraint:
            return True
    return False

def merge_two_routes(routeA,routeB):
    pylonCost = routeA.pylonCost + routeB.pylonCost
    landCost = routeA.landCost + routeB.landCost
    startId = routeA.startId
    #Edges = routeA.edges + routeB.edges
    #curvatures = routeA.curvatures \
    #    + [pointstoCurvature([(routeA.xyCoords)[-2],(routeA.xyCoords)[-1],(routeB.xyCoords)[0]])] \
    #    + routeB.curvatures 
    #variation = sum([np.absolute((curvatures[i+1]-curvatures[i])/curvatures[i]**1.5) for i in range(len(curvatures)-1)])
    startId = routeA.startId
    startAngle = routeA.startAngle
    endId = routeB.endId
    endAngle = routeB.endAngle
    latlngCoords = util.smart_concat(routeA.latlngCoords, routeB.latlngCoords)
    geospatialCoords = util.smart_concat(routeA.geospatialCoords,
                                         routeB.geospatialCoords)
    newRoute = Route(pylonCost, landCost, startId, endId, startAngle, endAngle,
                     latlngCoords, geospatialCoords)
    return newRoute

def edge_to_route(edge):
    pylonCost = edge.pylonCost
    landCost = edge.landCost
    startId = edge.startId
    endId = edge.endId
    startAngle = endAngle = edge.angle
    latlngCoords = edge.latlngCoords
    geospatialCoords = edge.geospatialCoords
    newRoute = Route(pylonCost, landCost, startId, endId, startAngle, endAngle,
                     latlngCoords, geospatialCoords)
    return newRoute

def edgesset_to_routesset(edgesSet):
    return [edge_to_route(edge) for edge in edgesSet]

def edgessets_to_routessets(edgesSets):
    return [edgesset_to_routesset(edgesSet) for edgesSet in edgesSets]

def sample_routes(merged):
    #n = int(np.log2(len(merged[0].xyCoords)))
    merged.sort(key = lambda route: route.landCost)
    # if n < 3: 
    #    selected = merged[:config.numPaths]
    #else:
    #    merged = filter(merged, lambda route: route.cost < config.maxCost*(numSlices/len(merged[0].xyCoords)))
    #    merged.sort(key = lambda route: route.variation)
    selected = merged[:config.numPaths]
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

        
