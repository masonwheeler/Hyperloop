"""
Original Developer: Jonathan Ward
Purpose of Module: To provide an interface for experimental Classes
Last Modified: 8/12/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

import paretofront
import mergetree
import math

class AbstractPoint:
    def __init__(self, pointId, latticeXCoord, latticeYCoord,
                                spatialXCoord, spatialYCoord):
        self.pointId = pointId
        self.latticeXCoord = latticeXCoord
        self.latticeYCoord = latticeYCoord
        self.spatialXCoord = spatialXCoord
        self.spatialYcoord = spatialYCoord

        
class AbstractSlice:
    def __init__(self, latticeXCoord, sliceBounds, startId, points_builder):
        self.points = points_builder(latticeXCoord, sliceBounds, startId)
        self.endId = startId + len(self.points)

        
class AbstractLattice:
    def __init__(self, slicesBounds, points_builder):
        self.slices = []
        startId = 0
        latticeXCoord = 0
        for sliceBounds in slicesBounds:
            newSlice = AbstractSlice(latticeXCoord, sliceBounds, startId,
                                                          points_builder)
            self.slices.append(newSlice.points)
            startId = newSlice.endId
            xCoord += 1


class AbstractEdge:
    def __init__(self, startPoint, endPoint):
        self.startId = startPoint.pointId
        self.endId = endPoint.pointId
        self.startLatticeCoords = [startPoint.latticeXCoord,
                                   startPoint.latticeYCoord]
        self.endLatticeCoords = [endPoint.latticeXCoord,
                                 endPoint.latticeYCoord]
        self.startSpatialCoords = [startPoint.spatialXCoord,
                                   startPoint.spatialYCoord]
        self.endSpatialCoords = [endPoint.spatialXCoord,
                                 endPoint.spatialYCoord]
        self.angle = math.degrees(math.atan2(
                       endPoint.spatialYCoord - startPoint.spatialYCoord,
                       endPoint.spatialXCoord - startPoint.spatialXCoord))
        self.isUseful = True


class AbstractEdgesSets:  
    @staticmethod
    def is_edge_pair_compatible(edgeA, edgeB, degreeConstraint):
        edgePairCompatible = (edgeA.endId == edgeB.startId and
             abs(edgeA.angle - edgeB.angle) < degreeConstraint)
        return edgePairCompatible                   

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
        self.determine_useful_edges(unfilteredEdgesSets,
                                    is_edge_pair_compatible)
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

    #def build_local_lattice(self): to be implemented
        

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

    @staticmethod
    def merge_two_graphs_sets(self, graphsSetA, graphsSetB):
        mergedGraphs = []
        selectedA = graphsSetsA.selectedGraphs
        selectedB = graphsSetsB.selectedGraphs
        for graphA in selectedA:
            for graphB in selectedB:
                if self.is_graph_pair_compatible(graphA, graphB):
                    mergedGraphs.append(merge_two_graphs(graphA, graphB))
        return mergedGraphs

def graphs_sets_merger(graphsSetA, graphsSetB):
    mergedGraphs = GraphsSets.merge_two_graphs_sets(graphsSetA, graphsSetB)
    if (len(mergedGraphs) == 0):
        return None
    else:
        mergedGraphsSet = GraphsSets(mergedGraphs)
        return mergedGraphsSet

def graphs_sets_updater(graphsSets):
    graphsSets.update_graphs()
    return graphsSets

