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
        pylonCoordinates = {"geospatials" : geospatials,
                            "latlngs" : latlngs,
                            "landElevation" : landElevation,
                            "pylonHeight" : pylonHeight,
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
    def __init__(self, minMaxElevations, pylons_builder):
        abstract.AbstractLattice.__init__(minMaxElevations, pylonsBuilder)


class TubeEdge(abstract.AbstractEdge):

    def tube_cost(self, startPylon, endPylon):
        startPylon.coord

    def pylon_cost(self, startPylonCoords, endPylonCoords):   
        return startPylon.cost + endPylon.cost

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
        

    def __init__(self, lattice)
        abstract.AbstractEdgesSets.__init__(lattice, self.tube_edge_builder,
                                            self.is_tube_edge_pair_compatible)
           

class TubeElevationGraph(abstract.AbstractGraph):
    def __init__(self, startId, endId, startAngle, endAngle, numEdges
                       cost, triptimeExcess):
        abstract.AbstractGraph.__init__(startId, endId, startAngle, endAngle,
                                                                    numEdges)
        self.cost = cost
        self.triptimeExcess

    def cost_triptime_excess(self):
        return [self.cost, self.triptimeExcess]

class TubeElevationGraphsSets(abstract.AbstractGraphSets):
    def graphs_cost_triptime_excess(self, tubeElevationGraphs)
        graphsCostTriptimeExcess = [graph.cost_triptime_excess() for graph
                                    in tubeElevationGraphs]
        return graphsCostTriptimeExcess

    def __init__(self, tubeElevationGraphs, graphs_cost_triptime_excess):
        minimizeCost = True
        minimizeTriptimeExcess = True
        abstract.AbstractGraphSets.__init__(tubeElevationGraphs,
            graphs_cost_triptime_excess, minimizeCost, minimizeTriptimeExcess)
                       
         
class TubePath:
    
    
