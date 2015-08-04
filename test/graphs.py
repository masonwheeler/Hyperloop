"""
Original Developer: Jonathan Ward
Purpose of Module: To generate routes from the lattice edges and merge them.
Last Modified: 7/30/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Graph merging now uses MergeTree and ParetoFront.
"""

import config
import util
import cacher
import visualize
import mergetree
import paretofront
import interpolate

class Graph:
    numEdges = 0
    pylonCost = 0
    landCost = 0
    startId = 0
    endId = 0
    startAngle = 0
    endAngle = 0
    curvatureMetric = None
    latlngs = []
    geospatials = []

    def compute_curvature(self):        
        if self.numEdges > config.graphCurvatureMinNumEdges:
            self.curvatureMetric = interpolate.graph_curvature(
                            self.geospatials, config.graphSampleSpacing)

    def __init__(self, numEdges, pylonCost, landCost, startId, endId,
                 startAngle, endAngle, latlngs, geospatials):
        self.numEdges = numEdges
        self.pylonCost = pylonCost
        self.landCost = landCost
        self.startId = startId
        self.endId = endId
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.latlngs = latlngs
        self.geospatials = geospatials    
        self.compute_curvature()

    def to_costcurvature_point(self):
        if self.numEdges > config.graphCurvatureMinNumEdges:
            cost = self.pylonCost + self.landCost
            curvature = self.curvatureMetric
            return [cost, curvature]

    def to_plottable(self, style):
        plottableGraph = [zip(*self.geospatials), style]
        return plottableGraph
        
    def display(self):     
        print("This graph's land cost is: " + str(self.landcost) + ".")
        print("This graph's pylon cost is: " + str(self.startAngle) + ".")        
        print("This graph's root mean squared curvature is: " +
              str(rmsCurvature) + ".")

class GraphsSet:
    minimizeCost = True
    minimizeCurvature = True
    graphsNumEdges = None #The number of edges each constituent graph has.
    unfilteredGraphs = None
    costCurvaturePoints = None
    paretoFront = None
    selectedGraphs = None      

    def graphs_to_costcurvaturepoints(self):
        if self.graphsNumEdges > config.graphCurvatureMinNumEdges:
            self.costCurvaturePoints = [graph.to_costcurvature_point()
                                        for graph in self.unfilteredGraphs]

    def select_graphs(self):
        if self.costCurvaturePoints == None:
            self.selectedGraphs = self.unfilteredGraphs
        else:
            try:
                self.paretoFront = paretofront.ParetoFront(
                                  self.costCurvaturePoints,
                                  self.minimizeCost, self.minimizeCurvature)
                selectedGraphIndices = self.paretoFront.frontsIndices[-1]
                print("unfilteredGraphsLen: " + str(len(self.unfilteredGraphs)))
                print("selectedGraphIndices: " + str(selectedGraphIndices))
                self.selectedGraphs = [self.unfilteredGraphs[i] for i in
                                       selectedGraphIndices]
            except ValueError:
                self.selectedGraphs = self.unfilteredGraphs

    def __init__(self, graphs):              
        self.unfilteredGraphs = graphs
        self.graphsNumEdges = self.unfilteredGraphs[0].numEdges
        self.graphs_to_costcurvaturepoints()
        self.select_graphs()

    def update_graphs(self):
        if self.paretoFront == None:
            return False
        else:
            areGraphsUpdated = self.paretoFront.build_nextfront()
            if areGraphsUpdated:
                selectedGraphIndices = self.paretoFront.frontsIndices[-1]
                for i in selectedGraphIndices:
                    self.selectedGraphs.append(self.unfilteredGraphs[i])
                return True
            else:
                return False       

def graphset_updater(graphset):
    isGraphSetUpdated = graphset.update_graphs()
    return isGraphSetUpdated

def edge_to_graph(edge):
    numEdges = 1
    pylonCost = edge.pylonCost
    landCost = edge.landCost
    startId = edge.startId
    endId = edge.endId
    startAngle = endAngle = edge.angle
    latlngs = edge.latlngs
    geospatials = edge.geospatials
    newGraph = Graph(numEdges, pylonCost, landCost, startId, endId,
                   startAngle, endAngle, latlngs, geospatials)
    return newGraph

def edges_set_to_graphs_set(edgesSet):
    graphs = map(edge_to_graph, edgesSet)
    graphsSet = GraphsSet(graphs) 
    return graphsSet

def edgessets_to_basegraphssets(edgessets):
    baseGraphSets = map(edges_set_to_graphs_set, edgessets)
    return baseGraphSets
    
def is_graph_pair_compatible(graphA, graphB):
    if (graphA.endId == graphB.startId):
        angleDifference = abs(graphA.endAngle - graphB.startAngle)
        if angleDifference < config.degreeConstraint:
            return True
    return False

def merge_two_graphs(graphA, graphB):
    numEdges = graphA.numEdges + graphB.numEdges
    pylonCost = graphA.pylonCost + graphB.pylonCost
    landCost = graphA.landCost + graphB.landCost
    startId = graphA.startId
    endId = graphB.endId
    startAngle = graphA.startAngle
    endAngle = graphB.endAngle
    latlngs = util.smart_concat(graphA.latlngs, graphB.latlngs)
    geospatials = util.smart_concat(graphA.geospatials, graphB.geospatials)
    mergedGraph = Graph(numEdges, pylonCost, landCost, startId, endId,
                        startAngle, endAngle, latlngs, geospatials)
    return mergedGraph

def graphs_sets_merger(graphsSetA, graphsSetB):
    mergedGraphs = []
    for graphA in graphsSetA.selectedGraphs:
        for graphB in graphsSetB.selectedGraphs:
            if is_graph_pair_compatible(graphA, graphB):            
                mergedGraphs.append(merge_two_graphs(graphA, graphB))
    if (len(mergedGraphs) == 0):
        print("no graphs were compatible")
        plottableA = [graphA.to_plottable('k-') for graphA in
                      graphsSetA.selectedGraphs]            
        plottableB = [graphB.to_plottable('r-') for graphB in
                      graphsSetB.selectedGraphs]
        failedMergeResults = plottableA + plottableB        
        visualize.plot_objects(failedMergeResults)
        return None
    else:
        mergedGraphsSet = GraphsSet(mergedGraphs)
        return mergedGraphsSet

def merge_basegraphssets(baseGraphSets):
    rootGraphSet = mergetree.merge_allobjects(baseGraphSets, graphs_sets_merger,
                                              graphset_updater)
    return rootGraphSet
    
def build_graphs(edgessets):
    baseGraphsSets = edgessets_to_basegraphssets(edgessets)
    rootGraphSet = merge_basegraphssets(baseGraphsSets)
    completeGraphs = rootGraphSet.data.selectedGraphs
    return completeGraphs
    
def get_graphs(edgessets):
    graphs = cacher.get_object("graphs", build_graphs, [edgessets],
                                cacher.save_graphs, config.graphsFlag)
    return graphs

        

"""
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
"""
