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

class PotentialPylon(abstract.AbstractPoint):
    def __init__(self, geospatials, latlngs, landElevation, pylonHeight
                                                               pylonId):
        pylonCoordinates = {"geospatials" : geospatials,
                            "latlngs" : latlngs,
                            "landElevation" : landElevation,
                            "pylonHeight" : pylonHeight,
        self.cost = pylonHeight
        abstract.AbstractPoint.__init__(pylonCoordinates, pylonId)

        
class PotentialPylonOptions(abstract.AbstractSlice):   
    def pylons_builder(self, shortestPylonCoords, tallestPylonCoords,
                             shortestPylonId):       
        heightDifference = tallestPylonCoords["pylonHeight"] - \
                           shortestPylonCoords["pylonHeight"]
        geospatials = shortestPylonCoords["geospatials"]
        latlngs = shortestPylonCoords["latlngs"]
        landElevation = shortestPylonCoords["landElevation"]
        shortestPylonHeight = shortestPylonCoords["pylonHeight"]
        pylonHeightOptions = util.build_grid2(heightDifference, #rename gridfunc
          config.pylonHeightOptionSpacing, shortestPylonHeight)     
        pylonIds = map(lambda x: x + shortestPylonId,
                       range(len(pylonHeightOptions)))
        enumeratedPylonHeightOptions = zip(pylonHeightOptions, pylonIds)
        potentialPylonOptions = map(lambda height_id:
            PotentialPylon(geospatials, latlngs, landElevation, height_id[0], 
            height_id[1]), enumeratedPylonHeightOptions)
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
        abstract.AbstractSlice.__init__(shortestPylonCoords,
            tallestPylonCoords, shortestPylonId, self.pylons_builder)
        

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
    
    
