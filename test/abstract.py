"""
Original Developer: Jonathan Ward
Purpose of Module: To provide an interface for experimental Classes
Last Modified: 8/12/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

import paretofront
import mergetree


class AbstractPoint:
    def __init__(self, coordinates, pointId):
        self.pointId = pointId
        self.coordinates = coordinates

        
class AbstractSlice:
    def __init__(self, startCoords, endCoords, startId, points_builder):
        self.points = points_builder(startCoords, endCoords, startId)
        self.endId = startId + len(self.points)

        
class AbstractLattice:
    def __init__(self, slicesStartAndEndCoords, points_builder):
        self.slices = []
        startId = 0
        for eachSliceStartAndEndCoords in slicesStartAndEndCoords:
            startCoords, endCoords = eachSliceStartAndEndCoords
            newSlice = AbstractSlice(startCoords, endCoords, startId,
                                                      points_builder)
            self.slices.append(newSlice)
            startId = newSlice.endId


class AbstractEdge:
    def __init__(self, startCoords, endCoords, startId, endId):
        self.startCoords = startCoords
        self.endCoords = endCoords
        self.startId = startId
        self.endId = endId


class AbstractEdgesSets:  
    def lattice_to_unfiltered_edges_sets(self, lattice, edge_builder):
        unfilteredEdgesSets = []
        for latticeSliceIndex in range(len(lattice) - 1):
            latticeSliceA = lattice[latticeSliceIndex]
            latticeSliceB = lattice[latticeSliceIndex + 1]
            edgesSet = []
            for pointA in sliceA:
                for pointB in sliceB:
                    edgesSet.append(edge_builder(pointA, pointB))
            unfilteredEdgesSets.append(edgesSet)
        return unfilteredEdgesSets    

    def determine_useful_edges(self, edgesSets, is_edge_pair_compatible):
        """Edge is useful if there are compatible adjacent edges"""
        for edgeA in edgesSets[0]:
            compatibles = [is_edge_pair_compatible(edgeA, edgeB)
                           for edgeB in edgesSets[1]]
            edgeA.isUseful = any(compatibles)
        for edgeSetIndex in range(1, len(edgesSets) - 1):
            for edgeB in edgesSets[edgeSetIndex]:
                compatiblesA = [is_edge_pair_compatible(edgeA, edgeB)
                                for edgeA in edgesSets[edgeSetIndex - 1]]
                compatiblesC = [is_edge_pair_compatible(edgeB, edgeC)
                                for edgeC in edgesSets[edgeSetIndex + 1]]
                edgeB.isUseful = any(compatiblesA) and any(compatiblesC)
        for edgeB in edgeSets[-1]:
            compatibles = [is_edge_pair_compatible(edgeA, edgeB)
                           for edgeA in edgesSets[-2]]
            edgeB.isUseful = any(compatibles)

    def filter_edges(self, edgesSets):
        filteredEdgesSets = []
        for edgesSet in edgesSets:
            filteredEdgesSet = filter(lambda edge : edge.isUseful, edgesSets)
            filteredEdgesSets.append(filteredEdgesSet)
        return filteredEdgesSets

    def check_empty(self, edgesSets):
        for edgesSet in edgesSets:
            if len(edgesSet) == 0:
                return True
        return False
        
    def iterative_filter(self, unfilteredEdgesSets, is_edge_pair_compatible):
        prefilterNumEdges = util.list_of_lists_len(unfilteredEdgesSets)
        util.smart_print("The original number of edges: " +
                         str(prefilteredNumEdges))
        filteredEdgesSetsList = []
        while True:
            self.determine_useful_edges(unfilteredEdgesSets,
                                        is_edge_pair_compatible)
            filteredEdgesSets = self.filter_edges(unfilteredEdgesSets)
            if self.check_empty(filteredEdgesSets):
                raise ValueError("Encountered Empty EdgesSet")
            postfilterNumEdges = util.list_of_lists_len(filteredEdgesSets)
            if postfilterNumEdges == prefilterNumEdges:
                break            
            prefilterNumEdges = postfilterNumEdges
            filteredEdgesSetsList.append(filteredEdgesSets)            
        return filteredEdgesSetsList
        
    def __init__(self, lattice, edge_builder, is_edge_pair_compatible):
        self.unfilteredEdgesSets = self.lattice_to_unfiltered_edges_sets(
                                                    lattice, edge_builder)
        self.filteredEdgesSetsList = self.iterative_filter(
                             self.unfilteredEdgesSets, is_edge_pair_compatible)
        self.finalEdgesSets = self.filteredEdgesSetsList[-1]
         

class AbstractGraph:
    def __init__(self, startId, endId, startAngle, endAngle, numEdges):
        self.startId = startId
        self.endId = endId
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.numEdges = numEdges
    
    def init_from_edge(self, edge):
        numEdges = 1
        graph = self.__init__(edge.startId, edge.endId,
                              edge.startAngle, edge.endAngle, numEdges)  
        return graph

    def merge_two_graphs(self, graphA, graphB):
        mergedGraph = self.__init__(graphA.startId, graphB.endId
                                    graphA.startAngle, graphB.endAngle,
                                    graphA.numEdges + graphB.numEdges)
        return mergedGraph

    def build_local_lattice(self):
        

class AbstractGraphsSet:
    def select_graphs(self, minimizeAVals, minimizeBVals):
        if self.graphsABVals == None:
            self.selectedGraphs = self.unfilteredGraphs
        else:
            try:
                self.front = paretofront.ParetoFront(self.graphsABVals,
                                          minimizeAVals, minimizeBVals)
                selectedGraphsIndices = self.front.frontsIndices[-1]
                numFronts = 1
                while (self.front.build_nextfront() and 
                       numFronts <= config.numFronts):
                    numFronts += 1
                    selectedGraphsIndices += self.front.frontsIndices[-1]
                self.selectedGraphs = [self.unfilteredGraphs[i] for i in
                                       selectedGraphsIndices]
                return True
            except ValueError:
                self.selectedGraphs = self.unfilteredGraphs
                return False

    def __init__(self, graphs, graphs_evaluator, is_graph_pair_compatible,
                       minimizeAVals, minimizeBVals):
        self.unfilteredGraphs = graphs
        graphsNumEdges = graphs[0].numEdges
        self.graphsABVals = graphs_evaluator(graphs, graphsNumEdges)
        self.select_graphs(minimizeAVals, minimizeBVals)
        self.minimizeAVals, self.minimizeBVals = minimizeAVals, minimizeBVals
        self.is_graph_pair_compatible = is_graph_pair_compatible

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

    def merge_two_graphssets(self, graphsSetA, graphsSetB)
        mergedGraphs = []
        selectedA = graphsSetsA.selectedGraphs
        selectedB = graphsSetsB.selectedGraphs
        for graphA in selectedA:
            for graphB in selectedB:
                if self.is_graph_pair_compatible(graphA, graphB):
                    mergedGraphs.append(merge_two_graphs(graphA, graphB))
        if (len(mergedGraphs) == 0):
            return None
        else:
            mergedGraphsSet = self.__init__(mergedGraphs)
            return mergedGraphsSet


class AbstractPath:
    def __init__(self, graph, get_graphcoords)
        self.graphCoords = get_graphcoords(graph)          

