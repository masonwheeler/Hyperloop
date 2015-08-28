"""
Original Developer: Jonathan Ward
Purpose of Module: To generate routes from the lattice edges and merge them.
Last Modified: 8/10/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Changed Class attributes to Instance attributes.
"""

import matplotlib.pyplot as plt
import time

import config
import util
import cacher
import visualize
import mergetree
import paretofront
import interpolate

class Graph:
    """Stores list of spatial points, their edge costs and curvature"""

    def compute_curvature(self):       
        """Compute the curvature of an interpolation of the graph""" 
        if self.numEdges > config.graphCurvatureMinNumEdges:
            self.curvatureMetric = interpolate.graph_curvature(
                            self.geospatials, config.graphSampleSpacing)

    def __init__(self, numEdges, pylonCost, landCost, startId, endId,
                 startAngle, endAngle, latlngs, geospatials):
        self.numEdges = numEdges #The number of edges in a graph
        self.pylonCost = pylonCost #The total cost of the pylons
        self.landCost = landCost #The total cost of the land acquired
        self.startId = startId #The id of the start point in the graph
        self.endId = endId #The id of the end point in the graph
        self.startAngle = startAngle #The angle of the start edge in the graph
        self.endAngle = endAngle #The angle of the end edge in the graph
        self.latlngs = latlngs #The latitude longitude coordinates
        self.geospatials = geospatials #The geospatial coordinates
        self.compute_curvature()

    def to_costcurvature_point(self):
        """Return the cost and curvature of the graph"""
        if self.numEdges > config.graphCurvatureMinNumEdges:
            cost = self.pylonCost + self.landCost
            curvature = self.curvatureMetric
            return [cost, curvature]

    def to_plottable(self, style):
        """Return the geospatial coords of the graph in plottable format"""
        plottableGraph = [zip(*self.geospatials), style]
        return plottableGraph
        
    def display(self):     
        """display the cost and curvature of the graph"""
        print("This graph's land cost is: " + str(self.landcost) + ".")
        print("This graph's pylon cost is: " + str(self.startAngle) + ".")        
        print("This graph's curvature is: " + str(self.curvatureMetric) + ".")


class GraphsSet:
    """Stores all selected graphs between two given lattice slices"""
    minimizeCost = True
    minimizeCurvature = True

    def graphs_to_costcurvaturepoints(self):
        """Compute cost and curvature of each graph with min number of edges"""
        if self.graphsNumEdges > config.graphCurvatureMinNumEdges:
            self.costCurvaturePoints = [graph.to_costcurvature_point()
                                        for graph in self.unfilteredGraphs]
        else:
            self.costCurvaturePoints = None

    def select_graphs(self):
        """
        Select the Pareto optimal graphs, minimizing cost and curvature

        If the cost and curvature of the graphs have not been computed,
        then return all of the graphs.
        """
        #print("num unfiltered graphs: " + str(len(self.unfilteredGraphs)))
        if self.costCurvaturePoints == None:
            self.selectedGraphs = self.unfilteredGraphs
            landCosts = [graph.landCost for graph in self.unfilteredGraphs]
            #print("min land cost: " + str(min(landCosts)))
        else:
            landCosts = [graph.landCost for graph in self.unfilteredGraphs]
            #print("min land cost: " + str(min(landCosts)))
            evaluationMetrics = [(graph.landCost) *
                                  graph.curvatureMetric for graph
                                  in self.unfilteredGraphs]
            self.sortedGraphs = [graph for (metric, graph) in
                    sorted(zip(evaluationMetrics, self.unfilteredGraphs),
                           key = lambda pair: pair[0])]            
            self.selectedGraphs = self.sortedGraphs[:100]
            allCosts = [graph.pylonCost + graph.landCost for graph
                        in self.unfilteredGraphs]
            allCurvatures = [graph.curvatureMetric for graph 
                             in self.unfilteredGraphs]
            selectedCosts = [ graph.landCost for graph
                             in self.selectedGraphs]
            selectedCurvatures = [graph.curvatureMetric for graph
                                  in self.selectedGraphs]
            #plt.scatter(allCosts, allCurvatures)
            #plt.show()
            #plt.scatter(selectedCosts, selectedCurvatures)
            #plt.show()
        """
            print("before selection")
            originalCosts, originalCurvatures = zip(*self.costCurvaturePoints)
            plt.scatter(originalCosts, originalCurvatures)
            plt.show()
            try:
                self.front = paretofront.ParetoFront(
                                  self.costCurvaturePoints,
                                  self.minimizeCost, self.minimizeCurvature)
                selectedGraphsIndices = self.front.frontsIndices[-1]
                numFronts = 1
                while (self.front.build_nextfront() and
                       numFronts <= config.numFronts):
                    numFronts += 1
                    selectedGraphsIndices += self.front.frontsIndices[-1]
                self.selectedGraphs = [self.unfilteredGraphs[i] for i in
                                       selectedGraphsIndices] 
                print("after selection")
                costs = [graph.pylonCost + graph.landCost for graph
                                             in self.selectedGraphs]
                curvatures = [graph.curvatureMetric for graph
                                             in self.selectedGraphs]
                plt.scatter(originalCosts, originalCurvatures, 'b',
                                       costs, curvatures, 'r')
                plt.show()
            except ValueError:
                print("encountered ValueError")
                self.selectedGraphs = self.unfilteredGraphs
                return 0
            """
    
    def update_graphs(self):
        """
        Update the selected graphs

        If the graphs are successfully updated return True, else return False.
        Update the graphs by adding the next front from the Pareto Frontier
        """
        if self.front == None:
            return False
        else:
            try:
                areGraphsUpdated = self.front.build_nextfront()
            except ValueError:
                return False
            if areGraphsUpdated:
                selectedGraphIndices = self.front.frontsIndices[-1]
                for i in selectedGraphIndices:
                    self.selectedGraphs.append(self.unfilteredGraphs[i])                
                return True                
            else:
                return False       

    def __init__(self, graphs):              
        self.unfilteredGraphs = graphs
        self.graphsNumEdges = self.unfilteredGraphs[0].numEdges
        self.graphs_to_costcurvaturepoints()
        self.select_graphs()       

def graphs_set_updater(graphsSet):
    """Wrapper function to update a graphset"""
    isGraphSetUpdated = graphsSet.update_graphs()
    return isGraphSetUpdated

def edge_to_graph(edge):
    """Initializes a graph from an edge"""
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
    """Creates a GraphsSet from a set of edges"""
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
    selectedA = graphsSetA.selectedGraphs
    selectedB = graphsSetB.selectedGraphs
    for graphA in selectedA:
        for graphB in selectedB:
            if is_graph_pair_compatible(graphA, graphB):           
                mergedGraph = merge_two_graphs(graphA, graphB)
                #print("graph A geospatials: " + str(graphA.geospatials))
                #print("graph B geospatials: " + str(graphB.geospatials))
                #print("merged graph geospatials: " + str(mergedGraph.geospatials))
                #time.sleep(3) 
                mergedGraphs.append(mergedGraph)
    if (len(mergedGraphs) == 0):
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
    graphsSetsTree = mergetree.MasterTree(baseGraphsSets, graphs_sets_merger,
                                                          graphs_set_updater)
    rootGraphsSet = graphsSetsTree.root
    selectedGraphs = rootGraphsSet.selectedGraphs
    return selectedGraphs
    
def get_graphs(edgessets):
    graphs = cacher.get_object("graphs", build_graphs, [edgessets],
                                cacher.save_graphs, config.graphsFlag)
    return graphs

