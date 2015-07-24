"""
Original Developer: Jonathan Ward
Purpose of Module: To generate routes from the lattice edges and merge them.
Last Modified: 7/22/16
Last Modified By: Jonathan Ward
Last Modification Purpose: Rolled back edge modifications
"""

import config
import util
import cacher
import sample_graphs as sample

class Graph:
    pylonCost = 0
    landCost = 0
    startId = 0
    endId = 0
    startAngle = 0
    endAngle = 0
    latlngs = []
    geospatials = []

    def __init__(self, pylonCost, landCost, startId, endId, startAngle,
                 endAngle, latlngs, geospatials):
        self.pylonCost = pylonCost
        self.landCost = landCost
        self.startId = startId
        self.endId = endId
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.latlngs = latlngs
        self.geospatials = geospatials

    def to_plottable(self):
        return zip(*self.geospatials)

    def display(self):     
        print("This graph's land cost is: " + str(self.landcost) + ".")
        print("This graph's start angle is: " + str(self.startAngle) + ".")        
        print("This graph's end angle is: " + str(self.endAngle) + ".")


def is_graph_pair_compatible(graphA, graphB):
    if (graphA.endId == graphB.startId):
        if abs(graphA.endAngle - graphB.startAngle) < config.degreeConstraint:
            return True
    return False

def merge_two_graphs(graphA, graphB):
    pylonCost = graphA.pylonCost + graphB.pylonCost
    landCost = graphA.landCost + graphB.landCost
    startId = graphA.startId
    endId = graphA.endId
    startAngle = graphA.startAngle
    endAngle = graphB.endAngle
    latlngs = util.smart_concat(graphA.latlngs, graphB.latlngs)
    geospatials = util.smart_concat(graphA.geospatials, graphB.geospatials)
    mergedGraph = Graph(pylonCost, landCost, startId, endId, startAngle,
                        endAngle, latlngs, geospatials)
    return mergedGraph

def edge_to_graph(edge):
    pylonCost = edge.pylonCost
    landCost = edge.landCost
    startId = edge.startId
    endId = edge.endId
    startAngle = endAngle = edge.angle
    latlngs = edge.latlngs
    geospatials = edge.geospatials
    newGraph = Graph(pylonCost, landCost, startId, endId, startAngle, endAngle,
                     latlngs, geospatials)
    return newGraph

def edgesset_to_graphsset(edgesSet):
    return [edge_to_graph(edge) for edge in edgesSet]

def edgessets_to_graphssets(edgesSets):
    return [edgesset_to_graphsset(edgesSet) for edgesSet in edgesSets]

def merge_two_graphssets(graphsSetA, graphsSetB):
    merged = []
    for graphA in graphsSetA:
        for graphB in graphsSetB:
            if is_graph_pair_compatible(graphA, graphB):            
                merged.append(merge_two_graphs(graphA, graphB))
    if (merged == []):
        print(len(graphsSetA))
        for graphA in graphsSetA:
          print(graphA.endId, graphA.geospatials)
        print(len(graphsSetB))    
        for graphB in graphsSetB:
          print(graphB.startId, graphB.geospatialCoords)
        raise ValueError('No compatible graphs in graphsets pair.')        
    sampledGraphs = sample.sample_graphs(merged)
    return sampledGraphs


def recursivemerge_graphssets(graphsSets):
    layers = [graphsSets]
    layersIndex = 0
    workingLayerIndex = 0

    numLayers = 1
    workingLayerSize = len(graphsSets)
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

def build_graphs(edgessets):
    graphsSets = edgessets_to_graphssets(edgessets)
    completeGraphs = recursivemerge_graphssets(graphsSets)
    return completeGraphs
    
def get_graphs(edgessets):
    graphs = cacher.get_object("graphs", build_graphs, [edgessets],
                                cacher.save_graphs, config.graphsFlag)
    return graphs

        
