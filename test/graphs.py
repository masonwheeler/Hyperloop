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
import sample_graphs
import visualize

class Graph:
    pylonCost = 0
    landCost = 0
    startId = 0
    endId = 0
    startAngle = 0
    endAngle = 0
    latlngs = []
    geospatials = []
    angleDifferences = []

    def __init__(self, pylonCost, landCost, startId, endId, startAngle,
                 endAngle, latlngs, geospatials, angleDifferences):
        self.pylonCost = pylonCost
        self.landCost = landCost
        self.startId = startId
        self.endId = endId
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.latlngs = latlngs
        self.geospatials = geospatials
        self.angleDifferences = angleDifferences

    def to_plottable(self, style):
        plottableGraph = [zip(*self.geospatials), style]
        return plottableGraph
        
    def display(self):     
        print("This graph's land cost is: " + str(self.landcost) + ".")
        print("This graph's pylon cost is: " + str(self.startAngle) + ".")        


def is_graph_pair_compatible(graphA, graphB):
    if (graphA.endId == graphB.startId):
        if abs(graphA.endAngle - graphB.startAngle) < config.degreeConstraint:
            return True
    return False

def merge_two_graphs(graphA, graphB):
    pylonCost = graphA.pylonCost + graphB.pylonCost
    landCost = graphA.landCost + graphB.landCost
    startId = graphA.startId
    endId = graphB.endId
    startAngle = graphA.startAngle
    endAngle = graphB.endAngle
    newAngleDifference = abs(startAngle - endAngle)
    angleDifferences = graphA.angleDifferences + [newAngleDifference] + \
                       graphB.angleDifferences
    latlngs = util.smart_concat(graphA.latlngs, graphB.latlngs)
    geospatials = util.smart_concat(graphA.geospatials, graphB.geospatials)
    mergedGraph = Graph(pylonCost, landCost, startId, endId, startAngle,
                        endAngle, latlngs, geospatials, angleDifferences)
    return mergedGraph

def edge_to_graph(edge):
    pylonCost = edge.pylonCost
    landCost = edge.landCost
    startId = edge.startId
    endId = edge.endId
    startAngle = endAngle = edge.angle
    latlngs = edge.latlngs
    geospatials = edge.geospatials
    angleDifferences = []
    newGraph = Graph(pylonCost, landCost, startId, endId, startAngle, endAngle,
                     latlngs, geospatials, angleDifferences)
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
        print("Graphs Set A Length:" + str(len(graphsSetA)))
        print("Graphs Set B Length:" + str(len(graphsSetB)))
        print("Potential Angle Pairs:")
        for graphA in graphsSetA:
            for graphB in graphsSetB:
                print(graphA.endId, graphB.startId)
        #plottableA = [graphA.to_plottable('k-') for graphA in graphsSetA]            
        #plottableB = [graphB.to_plottable('r-') for graphB in graphsSetB]
        #failedMergeResults = plottableA + plottableB        
        #visualize.plot_objects(failedMergeResults)
        raise ValueError('No compatible graphs in graphsets pair.')        
    sampledGraphs = sample_graphs.variation_constrained(merged)
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
            graphsSetA = layers[layersIndex][workingLayerIndex]
            graphsSetB = layers[layersIndex][workingLayerIndex + 1]
            merged = merge_two_graphssets(graphsSetA, graphsSetB)
            layers[layersIndex+1].append(merged)                
            workingLayerIndex += 2
        if breakFlag:
            break

    completeGraphs = layers[layersIndex][0]  
    return completeGraphs

def build_graphs(edgessets):
    graphsSets = edgessets_to_graphssets(edgessets)
    completeGraphs = recursivemerge_graphssets(graphsSets)
    return completeGraphs
    
def get_graphs(edgessets):
    graphs = cacher.get_object("graphs", build_graphs, [edgessets],
                                cacher.save_graphs, config.graphsFlag)
    return graphs

        
