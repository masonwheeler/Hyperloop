import random

import config
import util
import cacher

class Route:
    cost = 0
    startAngle = 0
    endAngle = 0
    startId = 0
    endId = 0
    latlngCoords = []
    geospatialCoords = []

    def __init__(self, cost, startId, endId, startAngle, endAngle,
                 latlngCoords, geospatialCoords):
        self.cost = cost
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


def is_route_pair_compatible(routeA, routeB):
    #print(routeA.endId, routeB.startId)
    if (routeA.endId == routeB.startId):
#        return True
        if abs(routeA.endAngle - routeB.startAngle) < config.degreeConstraint:
            return True
    return False

def merge_two_routes(routeA,routeB):
    cost = routeA.cost + routeB.cost
    startId = routeA.startId
    startAngle = routeA.startAngle
    endId = routeB.endId
    endAngle = routeB.endAngle
    latlngCoords = util.smart_concat(routeA.latlngCoords, routeB.latlngCoords)
    geospatialCoords = util.smart_concat(routeA.geospatialCoords,
                                         routeB.geospatialCoords)
    newRoute = Route(cost, startId, endId, startAngle, endAngle,
                     latlngCoords, geospatialCoords)
    return newRoute

def edge_to_route(edge):
    cost = edge.cost
    startId = edge.startId
    endId = edge.endId
    startAngle = endAngle = edge.angle
    latlngCoords = edge.latlngCoords
    geospatialCoords = edge.geospatialCoords
    newRoute = Route(cost, startId, endId, startAngle, endAngle,
                     latlngCoords, geospatialCoords)
    return newRoute

def edgesset_to_routesset(edgesSet):
    return [edge_to_route(edge) for edge in edgesSet]

def edgessets_to_routessets(edgesSets):
    return [edgesset_to_routesset(edgesSet) for edgesSet in edgesSets]

def sample_routes(merged):
    #merged.sort(key = lambda route: route.cost)    
    #selected = merged[:config.numPaths]
    selected = random.sample(merged,min(config.numPaths,len(merged)))
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

        
