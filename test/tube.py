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
import mergetree
import interpolate
import velocity

class Pylon(abstract.AbstractPoint):
    def pylon_construction_cost(self, pylonHeight):
        pylonCost = config.pylonBaseCost + \
                    pylonHeight * config.pylonCostPerMeter
        return pylonCost

    def __init__(self, pylonId, latticeXCoord, latticeYCoord, distanceAlongPath,
                       geospatial, latlng, landElevation, pylonHeight):    
        self.pylonHeight = pylonHeight
        self.landElevation = landElevation
        self.latlng = latlng
        tubeElevation = landElevation + pylonHeight
        xValue, yValue = geospatial
        zValue = tubeElevation
        self.tubeCoords = [xValue, yValue, zValue]
        self.pylonCost = self.pylon_construction_cost(pylonHeight)
        self.spatialXCoord = distanceAlongPath
        self.spatialYCoord = tubeElevation
        abstract.AbstractPoint.__init__(self, pylonId, latticeXCoord,
                   latticeYCoord, self.spatialXCoord, self.spatialYCoord)

        
class PylonsSlice(abstract.AbstractSlice):   
    @staticmethod
    def pylons_builder(latticeXCoord, pylonSliceBounds, shortestPylonId):       
        pylonHeightStepSize = pylonSliceBounds["pylonHeightStepSize"]        
        tallestPylonHeight = pylonSliceBounds["tallestPylonHeight"]
        shortestPylonHeight = pylonSliceBounds["shortestPylonHeight"]
        pylonHeightDifference = tallestPylonHeight - shortestPylonHeight
        distanceAlongPath = pylonSliceBounds["distanceAlongPath"] 
        geospatial = pylonSliceBounds["geospatial"]
        latlng = pylonSliceBounds["latlng"]
        landElevation = pylonSliceBounds["landElevation"]
        shortestPylonHeight = 0         
        pylonHeightOptions = util.build_grid_1d(pylonHeightDifference,
                             pylonHeightStepSize, shortestPylonHeight)    
        pylonIds = [index + shortestPylonId for index
                    in range(len(pylonHeightOptions))]
        pylons = []
        for i in range(len(pylonIds)):
            pylonId = pylonIds[i]
            pylonLatticeXCoord = latticeXCoord
            pylonLatticeYCoord = i
            pylonDistanceAlongPath = distanceAlongPath
            pylonGeospatial = geospatial
            pylonLatLng = latlng
            pylonLandElevation = landElevation
            pylonHeight = pylonHeightOptions[i]
            newPylon = Pylon(pylonId, pylonLatticeXCoord, pylonLatticeYCoord,
                        pylonDistanceAlongPath, pylonGeospatial, pylonLatLng,
                                             pylonLandElevation, pylonHeight)
            pylons.append(newPylon)    
        return pylons

    def __init__(self, latticeXCoord, pylonsSliceBounds, shortestPylonId):
        abstract.AbstractSlice.__init__(self, latticeXCoord, pylonsSliceBounds,
                                          shortestPylon)


class PylonsLattice(abstract.AbstractLattice):
    def elevation_point_to_pylons_slice_bounds(self, elevationPoint,
                                                  maxLandElevation):
        distanceAlongPath = elevationPoint["distanceAlongPath"]
        latlng = elevationPoint["latlng"]
        geospatial = elevationPoint["geospatial"]
        landElevation = elevationPoint["landElevation"]
        pylonHeightStepSize = config.pylonHeightStepSize
        tallestPylonHeight = maxLandElevation - landElevation
        shortestPylonHeight = 0        
        pylonsSliceBounds = {"tallestPylonHeight" : tallestPylonHeight,
                             "shortestPylonHeight" : shortestPylonHeight,
                             "distanceAlongPath" : distanceAlongPath,
                             "geospatial" : geospatial,
                             "latlng" : latlng,
                             "landElevation" : landElevation,
                             "pylonHeightStepSize" : pylonHeightStepSize}
        return pylonsSliceBounds

    def elevation_profile_to_pylons_slices_bounds(self, elevationProfile):
        landElevations = [elevationPoint["landElevation"] for elevationPoint
                                                        in elevationProfile]
        maxLandElevation = max(landElevations)
        pylonsSlicesBounds = [self.elevation_point_to_pylons_slice_bounds(
                      elevationPoint, maxLandElevation) for elevationPoint
                                                       in elevationProfile]
        return pylonsSlicesBounds   

    def __init__(self, elevationProfile):    
        pylonsSlicesBounds = self.elevation_profile_to_pylons_slices_bounds(
                                                           elevationProfile)
        abstract.AbstractLattice.__init__(self, pylonsSlicesBounds,
                                            PylonsSlice.pylons_builder)


class TubeEdge(abstract.AbstractEdge):    
    def tube_cost(self, startPylon, endPylon):
        startTubeCoords = startPylon.tubeCoords
        endTubeCoords = endPylon.tubeCoords
        tubeVector = util.edge_to_vector([startTubeCoords, endTubeCoords])
        tubeLength = util.norm(tubeVector)
        tubeCost = tubeLength * config.tubeCostPerMeter
        return tubeCost

    def pylon_cost(self, startPylon, endPylon):   
        totalPylonCost =  startPylon.pylonCost + endPylon.pylonCost
        return totalPylonCost

    def __init__(self, startPylon, endPylon):
        abstract.AbstractEdge.__init__(self, startPylon, endPylon)
        self.tubeCoords = [startPylon.tubeCoords, endPylon.tubeCoords]
        self.tubeCost = self.tube_cost(startPylon, endPylon)
        self.pylonCost = self.pylon_cost(startPylon, endPylon)        
        

class TubeEdgesSets(abstract.AbstractEdgesSets):
    def tube_edge_builder(self, startPylon, endPylon):
        tubeEdge = TubeEdge(startPylon, endPylon)
        return tubeEdge
    
    @staticmethod
    def is_tube_edge_pair_compatible(tubeEdgeA, tubeEdgeB):
        edgePairCompatible = abstract.AbstractEdgesSets.is_edge_pair_compatible(
                              tubeEdgeA, tubeEdgeB, config.tubeDegreeConstraint)
        return edgePairCompatible
                                                                             
    def __init__(self, pylonsLattice):
        abstract.AbstractEdgesSets.__init__(self, pylonsLattice,
          self.tube_edge_builder, self.is_tube_edge_pair_compatible)
               

class TubeGraph(abstract.AbstractGraph):
    
    velocityArcLengthStepSize = config.velocityArcLengthStepSize
    
    def compute_triptime_excess(self, tubeCoords, numEdges):
        if numEdges < config.tubeTripTimeExcessMinNumEdges:
            return None    
        else:             
            maxAllowedVels = interpolate.points_3d_max_allowed_vels(tubeCoords)
            triptimeExcess = velocity.compute_local_trip_time_excess(
                      maxAllowedVels, self.velocityArcLengthStepSize)
            return triptimeExcess

    def __init__(self, startId, endId, startAngle, endAngle, numEdges,
                       tubeCost, pylonCost, tubeCoords):
        abstract.AbstractGraph.__init__(self, startId, endId,
                                   startAngle, endAngle, numEdges)
        self.tubeCost = tubeCost
        self.pylonCost = pylonCost
        self.tubeCoords = tubeCoords
        self.triptimeExcess = self.compute_triptime_excess(tubeCoords, numEdges)

    def tube_cost_trip_time_excess(self):
        costTripTimeExcess = [self.tubeCost + self.pylonCost,
                                         self.triptimeExcess]
        return costTripTimeExcess

    @classmethod
    def init_from_tube_edge(cls, tubeEdge):
        startId = tubeEdge.startId
        endId = tubeEdge.endId
        startAngle = tubeEdge.angle
        endAngle = tubeEdge.angle  
        numEdges = 1        
        tubeCost = tubeEdge.tubeCost
        pylonCost = tubeEdge.pylonCost        
        tubeCoords = tubeEdge.tubeCoords
        data = cls(startId, endId, startAngle, endAngle, numEdges, tubeCost,
                   pylonCost, tubeCoords)
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
        data = cls(startId, endId, startAngle, endAngle, numEdges, tubeCost,
                   pylonCost, tubeCoords)
        return data


class TubeGraphsSet(abstract.AbstractGraphsSet):

    @staticmethod
    def is_graph_pair_compatible(graphA, graphB):
        graphsCompatible = abstract.AbstractGraphsSet.is_graph_pair_compatible(
                                   graphA, graphB, config.tubeDegreeConstraint)
        return graphsCompatible

    @staticmethod 
    def tubegraphs_cost_triptime_excess(tubeGraphs, graphsNumEdges):
        if graphsNumEdges < config.tubeTripTimeExcessMinNumEdges:
            return None    
        else: 
            graphsCostTriptimeExcess = [tubeGraph.tube_cost_trip_time_excess()
                                         for tubeGraph in tubeElevationGraphs]
            return graphsCostTriptimeExcess

    def __init__(self, tubeGraphs, graphsNumEdges):
        minimizeCost = True
        minimizeTriptimeExcess = True
        abstract.AbstractGraphsSet.__init__(self, tubeGraphs,
          self.tubegraphs_cost_triptime_excess, self.is_graph_pair_compatible,
                         minimizeCost, minimizeTriptimeExcess, graphsNumEdges)
    
    @classmethod
    def init_from_tube_edges_set(cls, tubeEdgesSet):
        tubeGraphs = map(TubeGraph.init_from_tube_edge, tubeEdgesSet)        
        graphsNumEdges = 1
        return cls(tubeGraphs, graphsNumEdges)

def tube_graphs_set_pair_merger(tubeGraphsSetA, tubeGraphsSetB):
    mergedTubeGraphs = abstract.graphs_set_pair_merger(tubeGraphsSetA,
                                        tubeGraphsSetB, TubeGraphsSet)
    return mergedTubeGraphs

        
def elevation_profile_to_tube_graphs(elevationProfile):
    pylonsLattice = PylonsLattice(elevationProfile)
    tubeEdgesSets = TubeEdgesSets(pylonsLattice)
    tubeGraphsSets = map(TubeGraphsSet.init_from_tube_edges_set,
                                   tubeEdgesSets.finalEdgesSets)
    tubeGraphsSetsTree = mergetree.MasterTree(tubeGraphsSets,
        tube_graphs_set_pair_merger, abstract.graphs_set_updater)
    rootTubeGraphsSet = graphsTree.root
    selectedTubeGraphs = rootGraphsSet.selectedGraphs
    return selectedTubeGraphs
    
    
                                      
