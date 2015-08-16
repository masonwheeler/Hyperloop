"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the pylon cost component of an edge
Last Modified: 8/12/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To implement a non naive pylon cost method.
"""

import util
import config
import abstract

class Pylon(abstract.AbstractPoint):

    def construction_cost(self, pylonHeight):
        cost = config.pylonBaseCost + pylonHeight * config.pylonCostPerMeter
        return cost

    def __init__(self, geospatials, latlngs, landElevation, pylonHeight
                                                               pylonId):
        tubeElevation = landElevation + pylonHeight
        pylonCoordinates = {"geospatials" : geospatials,
                            "latlngs" : latlngs,
                            "landElevation" : landElevation,
                            "pylonHeight" : pylonHeight,
                            "tubeElevation": tubeElevation}
        self.cost = self.construction_cost(pylonHeight)
        abstract.AbstractPoint.__init__(pylonCoordinates, pylonId)

        
class PylonsSlice(abstract.AbstractSlice):   
    pylonHeightOptionSpacing = config.pylonHeightOptionSpacing

    def pylons_builder(self, shortestPylonCoords, tallestPylonCoords,
                             shortestPylonId):       
        heightDifference = tallestPylonCoords["pylonHeight"] - \
                           shortestPylonCoords["pylonHeight"]
        geospatials = shortestPylonCoords["geospatials"]
        latlngs = shortestPylonCoords["latlngs"]
        landElevation = shortestPylonCoords["landElevation"]
        shortestPylonHeight = shortestPylonCoords["pylonHeight"]
        pylonHeightOptions = util.build_grid2(heightDifference,
          self.pylonHeightOptionSpacing, shortestPylonHeight)     
        pylonIds = map(lambda x: x + shortestPylonId,
                       range(len(pylonHeightOptions)))
        enumeratedPylonHeightOptions = zip(pylonHeightOptions, pylonIds)
        potentialPylonOptions = map(lambda height_id:
        Pylon(geospatials, latlngs, landElevation, height_id[0], height_id[1]),
        enumeratedPylonHeightOptions)
        return potentialPylonOptions        

    def __init__(self, minElevation, maxElevation, shortestPylonId,
                       geospatials, latlngs):
        shortestPylonHeight = 0
        tallestPylonHeight = maxElevation - minElevation
        shortestPylonCoords = {"geospatials" : geospatials,
                               "latlngs" : latlngs,
                               "landElevation": minElevation,
                               "pylonHeight" : shortestPylonHeight}
        tallestPylonCoords = {"geospatials" : geospatials,
                              "latlngs" : latlngs,
                              "landElevation": maxElevation,
                              "pylonHeight" : tallestPylonHeight}
        abstract.AbstractSlice.__init__(shortestPylonCoords, tallestPylonCoords,
                                        shortestPylonId, self.pylons_builder)


class PylonsLattice(abstract.AbstractLattice):
    def __init__(self, minMaxElevations):
        abstract.AbstractLattice.__init__(minMaxElevations, PylonsSlice)


class TubeEdge(abstract.AbstractEdge):    
    def tube_cost(self, startPylon, endPylon):
        startTubeElevation = startPylon.coordinates["tubeElevation"]
        endTubeElevation = endPylon.coordinates["tubeElevation"]
        elevationDifference = startTubeElevation - endTubeElevation
        
        startPylonGeospatials = startPylon.coordinates["geospatials"]
        endPylonGeospatials = endPylon.coordinates["geospatials"]
        geospatialVector = util.edge_to_vector([startPylonGeospatials,
                                                endPylonGeospatials])
        geospatialDistance = util.norm(geospatialsVector)
    
        tubeLength = util.norm([elevationDifference, geospatialsDistance])
        tubeCost = tubeLength * config.tubeCostPerMeter
        return tubeCost

    def pylon_cost(self, startPylonCoords, endPylonCoords):   
        totalPylonCost =  startPylon.cost + endPylon.cost
        return totalPylonCost

    def __init__(self, startPylon, endPylon, startId, endId):
        abstract.AbstractEdge.__init__(startPylonCoords, endPylonCoords,
                                       startId, endId)
        self.tubeCost = self.tube_cost(startPylon, endPylon)
        self.pylonCost = self.pylon_cost(startPylon, endPylon)        
        

class TubeEdgesSets(abstract.AbstractEdgesSets):
    def tube_edge_builder(self, startPylon, endPylon):
        startId = startPylon.pointId
        endId = endPylon.pointId
        return TubeEdge(startPylon, endPylon, startId, endId)


    def is_tube_edge_pair_compatible(self, tubeEdgeA, tubeEdgeB):
        if edgeA.endId == edgeB.startId:
            if abs(edgeA.angle - edgeB.angle) < config.tubeDegreeConstraint:
                return True
        return False
        
    def __init__(self, lattice)
        abstract.AbstractEdgesSets.__init__(lattice, self.tube_edge_builder,
                                            self.is_tube_edge_pair_compatible)
           

class TubeGraph(abstract.AbstractGraph):

    def compute_triptime_excess(self, tubeElevations, geospatials, numEdges):
        
        return triptimeExcess

    def __init__(self, startId, endId, startAngle, endAngle, numEdges
                       tubeCost, pylonCost, tubeElevations, geospatials,
                                                         triptimeExcess):
        abstract.AbstractGraph.__init__(startId, endId, startAngle, endAngle,
                                                                    numEdges)
        self.tubeCost = tubeCost
        self.pylonCost = pylonCost
        self.tubeElevations = tubeElevations
        self.geospatials = geospatials
        self.triptimeExcess = self.compute_triptime_excess(self.tubeElevations,
                                                     self.geospatials, numEdges)

    def init_from_tube_edge(self, tubeEdge):
        tubeGraph = abstract.AbstractGraph.init_from_edge(tubeEdge)
        tubeGraph.tubeCost = tubeEdge.tubeCost
        tubeGraph.pylonCost = tubeEdge.pylonCost        
        tubeElevations = [tubeEdge.startPoint.coordinates["tubeElevation"],
                      tubeEdge.endPoint.coordinates["tubeElevation"]]        
        tubeGraph.tubeElevations = tubeElevations
        tubeGraph.geospatials = [tubeEdge.startPoint.coordinates["geospatials"],
                                 tubeEdge.endPoint.coordinates["geospatials"]]
        tubeGraph.triptimeExcess = self.compute_triptime_excess(
            tubeGraph.tubeElevations, tubeGraph.geospatials, tubeGraph.numEdges)
        return tubeGraph

    def merge_two_tubegraphs(self, tubeGraphA, tubeGraphB):
        mergedTubeGraph = abstract.AbstactGraph.merge_two_graphs(tubeGraphA,
                                                                 tubeGraphB)
        mergedTubeGraph.tubeCost = tubeGraphA.tubeCost + tubeGraphB.tubeCost
        mergedTubeGraph.pylonCost = tubeGraphA.pylonCost + tubeGraphB.pylonCost
        mergedTubeGraph.tubeElevations = util.smart_concat(
                        tubeGraphA.tubeElevations, tubeGraphB.tubeElevations)
        mergedTubeGraph.geospatials = util.smart_concat(tubeGraphA.geospatials,
                                                        tubeGraphB.geospatials)
        mergedTubeGraph.triptimeExcess = self.compute_triptime_excess(
               mergedTubeGraph.tubeElevations, mergedTubeGraph.geospatials,
               mergedTubeGraph.numEdges)
        return mergedTubeGraph


class TubeGraphsSets(abstract.AbstractGraphSets):
    def tubegraphs_cost_triptime_excess(self, tubeGraphs)
        graphsCostTriptimeExcess = [[tubeGraph.tubeCost + tubeGraph.pylonCost,
                                     tubeGraph.triptimeExcess]
                                     for tubeGraph in tubeElevationGraphs]
        return graphsCostTriptimeExcess

    def __init__(self, tubeGraphs):
        minimizeCost = True
        minimizeTriptimeExcess = True
        abstract.AbstractGraphSets.__init__(tubeGraphs,
                           self.tubegraphs_cost_triptime_excess,
                           minimizeCost, minimizeTriptimeExcess)

    def init_from_tube_edges_sets(self, tubeEdgesSets):
        tubeGraphs = [map(TubeGraph.init_from_tube_edge, tubeEdgesSet) for
                      tubeEdgesSet in tubeEdgesSets]
        tubeGraphsSets = self.__init__(tubeGraphs)
        return tubeGraphsSets    
        
        
    
                       
         
class TubePath:
    
    
