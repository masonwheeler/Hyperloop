import random

import config
import util

class Route:
    cost = 0
    startYVal = 0
    endYVal = 0
    startAngle = 0
    endAngle = 0
    latlngCoords = []
    xyCoords = []
    """
    tripTime = 0
    plotTimes = []
    points = []
    vel_points = []
    accel_points = []
    pylon_data = ["Data about pylon placement and pylon cost."]
    comfort = "not noticeable" 
    """

    def __init__(self, cost, startYVal, endYVal, startAngle, endAngle,
                 latlngCoords, xyCoords):
        self.cost = cost
        self.startYVal = startYVal
        self.endYVal = endYVal
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.latlngCoords = latlngCoords
        self.xyCoords = xyCoords
    
    def display(self):     
        print("The route cost is: " + str(self.cost) + ".")
        print("The route start y-value is: " + str(self.startYVal) + ".")        
        print("The route end y-value is: " + str(self.endYVal) + ".")
        print("The route start angle is: " + str(self.startAngle) + ".")        
        print("The route end angle is: " + str(self.endAngle) + ".")


def two_routes_compatible(routeA, routeB):
    return ((routeA.endYVal == routeB.startYVal) and
      (abs(routeA.endAngle - routeB.startAngle) < config.degreeConstraint))

def merge_two_routes(routeA,routeB):
    cost = routeA.cost + routeB.cost
    startYVal = routeA.startYVal
    startAngle = routeA.startAngle
    endYVal = routeB.endYVal    
    endAngle = routeB.endAngle
    latlngCoords = util.smart_concat(routeA.latlngCoords, routeB.latlngCoords)
    xyCoords = util.smart_concat(routeA.xyCoords, routeB.xyCoords)
    newRoute = Route(cost, startYVal, endYVal, startAngle, endAngle,
                     latlngCoords, xyCoords)
    return newRoute

def edge_to_route(edge):
    cost = edge.cost
    startYVal = edge.startYVal
    endYVal = edge.endYVal
    startAngle = endAngle = edge.angle
    latlngCoords = edge.latlngCoords
    xyCoords = edge.xyCoords
    newRoute = Route(cost, startYVal, endYVal, startAngle, endAngle,
                     latlngCoords, xyCoords)
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
            if two_routes_compatible(routeA,routeB):            
                merged.append(merge_two_routes(routeA,routeB))
    if (merged == []):
        print(len(routesSetA))
        for routeA in routesSetA:
          print(routeA.endYVal,routeA.endAngle)
        print(len(routesSetB))    
        for routeB in routesSetB:
          print(routeB.startYVal,routeB.startAngle)
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
#    print(len(filteredRoutes))
    filteredRoutes[0].display()
    return filteredRoutes

def build_routes(edgessets):
    routesSets = edgessets_to_routessets(edgessets)
    fiteredRoutes = recursivemerge_routessets(routesSets)
    return filteredRoutes
    
def get_routes(edgessets):
    routes = cacher.get_object("routes", build_routes, [edgessets],
                                cacher.save_routes, config.routesFlag)
    return routes

        
