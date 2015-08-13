"""
Original Developer: Jonathan Ward
Purpose of Module: To provide an interface for experimental Classes
Last Modified: 8/12/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

class AbstractPoint:
    def __init__(self, coordinates, pointId):
        self.pointId = pointId
        self.coordinates = coordinates
        
class AbstractSlice:
    def __init__(self, startCoords, endCoords, startId, points_builder):
        self.points = points_builder(startCoords, endCoords, startId)
        self.endId = startId + len(self.points)
        
class AbstractLattice:
    def __init__(self, slicesStartEndCoords, points_builder):
        self.slices = []
        startId = 0
        for eachSliceStartEndCoords in slicesStartEndCoords:
            startCoords, endCoords = eachSliceStartEndCoords
            newSlice = AbstractSlice(startCoords, endCoords, startId,
                                                      points_builder)
            self.slices.append(newSlice)
            startId = newSlice.endId

class AbstractGraph:
    def __init__(self, startId, endId, startAngle, endAngle, numEdges):
        self.startId = startId
        self.endId = endId
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.numEdges = numEdges

class AbstractGraphsSets:
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

    def __init__(self, graphs, graphs_evaluator, minimizeAVals, minimizeBVals):
        self.unfilteredGraphs = graphs
        graphsNumEdges = graphs[0].numEdges
        self.graphsABVals = graphs_evaluator(graphs, graphsNumEdges)
        self.select_graphs(minimizeAVals, minimizeBVals)
        self.minimizeAVals, self.minimizeBVals = minimizeAVals, minimizeBVals

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

class AbstractPath:
    def __init__(self, graph, get_graphcoords)
        self.graphCoords = get_graphcoords(graph)  

        

