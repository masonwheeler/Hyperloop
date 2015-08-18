"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the tube/pylon cost component of an edge
Last Modified: 8/15/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To implement a non naive tube/pylon cost method.
"""

import util
import config
import abstract
import mergeTree
import interpolate


class Pylon(abstract.AbstractPoint):
    def construction_cost(self, pylonHeight):
        cost = config.pylonBaseCost + pylonHeight * config.pylonCostPerMeter
        return cost

    def __init__(self, geospatials, latlngs, landElevation, pylonHeight,
                                                tubeElevation, pylonId):
        tubeElevation = landElevation + pylonHeight
        xValue, yValue = geospatials
        zValue = tubeElevation
        tubeCoords = [xValue, yValue, zValue]
        coords = {"geospatials" : geospatials,
                  "latlngs" : latlngs,
                  "landElevation" : landElevation,
                  "pylonHeight" : pylonHeight,
                  "tubeElevation": tubeElevation,
                  "tubeCoords": tubeCoords}
        self.cost = self.construction_cost(pylonHeight)
        abstract.AbstractPoint.__init__(coords, pylonId)

        
class PylonsSlice(abstract.AbstractSlice):   
    pylonHeightOptionSpacing = config.pylonHeightOptionSpacing

    def pylons_builder(self, pylonSliceBounds, shortestPylonId):       
        heightDifference = pylonSliceBounds["heightDifference"]
        geospatials = pylonSliceBounds["geospatials"]
        latlngs = pylonSliceBounds["latlngs"]
        landElevation = pylonSliceBounds["landElevation"]
        shortestPylonHeight = 0
        pylonHeightOptions = util.build_grid2(heightDifference,
                 self.pylonHeightOptionSpacing, shortestPylonHeight)    
        tubeElevationOptions = [pylonHeightOption + landElevation 
                                for pylonHeightOption in pylonHeightOptions]
        pylonIds = [index + shortestPylonId for index
                    in range(len(pylonHeightOptions))]
        pylonOptions = [Pylon(geospatials, latlng, landElevation,
            pylonHeightOptions[i], tubeElevationOptions[i], pylonIds[i])
            for i in range(len(pylonIds))]
        return pylonOptions        

    def __init__(self, pylonsSliceBounds, shortestPylonId):
        abstract.AbstractSlice.__init__(pylonSliceBounds, shortestPylonId,
                                        self.pylons_builder)


class PylonsLattice(abstract.AbstractLattice):
    def __init__(self, pylonsSlicesBounds):
        abstract.AbstractLattice.__init__(pylonsSlicesBounds, PylonsSlice)


class TubeEdge(abstract.AbstractEdge):    
    def tube_cost(self, startPylon, endPylon):
        startTubeCoords = startPylon.coords["tubeCoords"]
        endTubeCoords = endPylon.coords["tubeCoords"]
        tubeVector = util.edge_to_vector([startTubeCoords, endTubeCoords])
        tubeLength = util.norm(tubeVector)
        tubeCost = tubeLength * config.tubeCostPerMeter
        return tubeCost

    def pylon_cost(self, startPylon, endPylon):   
        totalPylonCost =  startPylon.cost + endPylon.cost
        return totalPylonCost

    def __init__(self, startPylon, endPylon):
        abstract.AbstractEdge.__init__(startPylon, endPylon)
        self.tubeCost = self.tube_cost(startPylon, endPylon)
        self.pylonCost = self.pylon_cost(startPylon, endPylon)        
        

class TubeEdgesSets(abstract.AbstractEdgesSets):
    tubeEdgeDegreeConstraint = config.tubeDegreeConstraint    

    def tube_edge_builder(self, startPylon, endPylon):
        tubeEdge = TubeEdge(startPylon, endPylon)
        return tubeEdge
    
    @staticmethod
    def is_tube_edge_pair_compatible(self, tubeEdgeA, tubeEdgeB):
        return abstract.AbstractEdgesSets.is_edge_pair_compatible(tubeEdgeA,
                                   tubeEdgeB, self.tubeEdgeDegreeConstraint)
                                                                             
    def __init__(self, pylonsLattice)
        abstract.AbstractEdgesSets.__init__(pylonsLattice,
            self.tube_edge_builder, self.is_tube_edge_pair_compatible)
               

class TubeGraph(abstract.AbstractGraph):
    def compute_triptime_excess(self, tubeCoordinates, numEdges):
        if numEdges < config.minNumTubeEdges:
            return None    
        else:             
            interpolate.compute_trip_time_excess            
            triptimeExcess =          
            return triptimeExcess

    def __init__(self, startId, endId, startAngle, endAngle, numEdges
                       tubeCost, pylonCost, tubeCoords, geospatials):
        abstract.AbstractGraph.__init__(startId, endId, startAngle, endAngle,
                                                                    numEdges)
        self.tubeCost = tubeCost
        self.pylonCost = pylonCost
        self.tubeCoords = tubeCoords
        self.geospatials = geospatials
        self.triptimeExcess = self.compute_triptime_excess(tubeCoords, numEdges)

    @classmethod
    def init_from_tube_edge(cls, tubeEdge):
        startId = tubeEdge.startId
        endId = tubeEdge.endId
        startAngle = tubeEdge.startAngle
        endAngle = tubeEdge.endAngle
        numEdges = 1        
        tubeCost = tubeEdge.tubeCost
        pylonCost = tubeEdge.pylonCost        
        tubeCoords = [tubeEdge.startPoint.coords["tubeCoords"],
                      tubeEdge.endPoint.coords["tubeCoords"]]        
        geospatials = [tubeEdge.startPoint.coords["geospatials"],
                       tubeEdge.endPoint.coords["geospatials"]]
        triptimeExcess = self.compute_triptime_excess(tubeCoords, numEdges)
        data = cls(startId, endId, startAngle, endAngle, numEdges, tubeCost,
                   pylonCost, tubeCoords, geospatials, triptimeExcess)
        return data
    
    @classmethod
    def merge_two_tubegraphs(cls, tubeGraphA, tubeGraphB):
        startId = tubeGraphA.startId
        endId = tubeGraphB.endId
        startAngle = tubeGraphA.startAngle
        endAngle = tubeGraphB.endAngle
        numEdges = tubeGraphA.numEdges + tubeGraphB.numEdges
        tubeCost = tubeGraphA.tubeCost + tubeGraphB.tubeCost
        pylonCost = tubeGraphA.pylonCost + tubeGraphB.pylonCost
        tubeCoords = util.smart_concat(tubeGraphA.tubeCoords,
                                       tubeGraphB.tubeCoords)
        geospatials = util.smart_concat(tubeGraphA.geospatials,
                                        tubeGraphB.geospatials)
        triptimeExcess = self.compute_triptime_excess(tubeCoords, numEdges)
        data = cls(startId, endId, startAngle, endAngle, numEdges, tubeCost,
                   pylonCost, tubeCoords, geospatials, triptimeExcess)
        return data


class TubeGraphsSets(abstract.AbstractGraphsSet):
    def tubegraphs_cost_triptime_excess(self, tubeGraphs)
        graphsCostAndtriptimeExcess = [[tubeGraph.tubeCost + tubeGraph.pylonCost,
                                     tubeGraph.triptimeExcess]
                                     for tubeGraph in tubeElevationGraphs]
        return graphsCostAndTriptimeExcess

    def __init__(self, tubeGraphs):
        minimizeCost = True
        minimizeTriptimeExcess = True
        abstract.AbstractGraphsSet.__init__(tubeGraphs,
                           self.tubegraphs_cost_triptime_excess,
                           minimizeCost, minimizeTriptimeExcess)
    
    @classmethod
    def init_from_tube_edges_sets(cls, tubeEdgesSets):
        tubeGraphs = [map(TubeGraph.init_from_tube_edge, tubeEdgesSet) for
                      tubeEdgesSet in tubeEdgesSets]        
        return cls(tubeGraphs)
        
                                      
