"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the tube/pylon cost component of an edge
Last Modified: 8/15/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To implement a non naive tube/pylon cost method.
"""
#Standard Modules
import numpy as np

#Our Modules
import abstract
import clothoid
import config
import interpolate
import mergetree
import velocity
import util

#Experimental Modules
from scipy.interpolate import PchipInterpolator
import routes
import match_landscape as landscape

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

    def circle_function(self, x, r):
        if x > r:
            return -float("Inf")
        else:
            y = np.sqrt(np.square(r) - np.square(x)) - r
            return y

    def build_window(self, leftBound, rightBound, radius):
        relativeIndices = range(-leftBound, rightBound + 1)
        window = [{"relativeIndex" : relativeIndex,
                   "relativeElevation" : self.circle_function(
                   abs(relativeIndex * config.pylonSpacing), radius)}
                   for relativeIndex in relativeIndices]
        return window                    

    def add_current_window(self, envelope, currentWindow):
        for point in currentWindow:
            currentIndex = point["index"]
            envelope[currentIndex].append(point["elevation"])

    def build_envelope(self, elevations, radius):
        windowSize = int(radius / config.pylonSpacing)
        envelopeLists = [[] for i in xrange(len(elevations))]
        for currentIndex in range(0, len(elevations)):
            if currentIndex < windowSize:
                leftBound = currentIndex
            else:
                leftBound = windowSize
            if currentIndex > (len(elevations) - 1) - windowSize:
                rightBound = (len(elevations) - 1) - currentIndex
            else:
                rightBound = windowSize
            relativeWindow = self.build_window(leftBound, rightBound, radius)
            currentElevation = elevations[currentIndex]
            currentWindow = [{
                "index" : point["relativeIndex"] + currentIndex,
                "elevation" : point["relativeElevation"] + currentElevation}
                for point in relativeWindow]
            self.add_current_window(envelopeLists, currentWindow)
        envelope = map(max, envelopeLists)
        return envelope

    def build_pylons_envelopes(self, elevationProfile):
        distances = []
        elevations = []
        for elevationPoint in elevationProfile:
            distances.append(elevationPoint["distanceAlongPath"])
            elevations.append(elevationPoint["landElevation"])
        upperSpeed = config.maxSpeed
        curvatureThresholdUpper = interpolate.compute_curvature_threshold(
                        upperSpeed, config.verticalAccelConstraint)
        radiusUpper = 1.0 / curvatureThresholdUpper
        envelopeUpper = self.build_envelope(elevations, radiusUpper)
        lowerSpeed = config.maxSpeed/1.2
        curvatureThresholdLower = interpolate.compute_curvature_threshold(
                        lowerSpeed, config.verticalAccelConstraint)
        radiusLower = 1.0 / curvatureThresholdLower
        envelopeLower = self.build_envelope(elevations, radiusLower)
        return [envelopeUpper, envelopeLower]
    
    def envelope_point_to_bounds(self, dataPoint):
        elevationPoint, envelopePointUpper, envelopePointLower = dataPoint
        landElevation = elevationPoint["landElevation"]
        pylonsSliceBounds = {
            "tallestPylonHeight" : envelopePointUpper - landElevation,
            "shortestPylonHeight" : envelopePointLower - landElevation,
            "distanceAlongPath" : elevationPoint["distanceAlongPath"],
            "geospatial" : elevationPoint["geospatial"],
            "latlng" : elevationPoint["latlng"],
            "landElevation" : landElevation,
            "pylonHeightStepSize" : config.pylonHeightStepSize
            }
        return pylonsSliceBounds

    def build_pylons_slices_bounds(self, elevationProfile, pylonsEnvelopeUpper,
                                                           pylonsEnvelopeLower):
        pylonsData = zip(elevationProfile, pylonsEnvelopeUpper,
                                           pylonsEnvelopeLower)
        pylonsSlicesBounds = [self.envelope_point_to_bounds(dataPoint)
                                      for dataPoint in pylonsData]
        return pylonsSlicesBounds   

    def __init__(self, elevationProfile):    
        pylonsEnvelopeUpper, pylonsEnvelopeLower = \
             self.build_pylons_envelopes(elevationProfile)
        pylonsSlicesBounds = self.build_pylons_slices_bounds(elevationProfile,
                                     pylonsEnvelopeUpper, pylonsEnvelopeLower)
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
            zValues = [tubeCoord[2] for tubeCoord in tubeCoords]
            localMaxAllowedVels = interpolate.points_1d_local_max_allowed_vels(
                                                                       zValues)
            triptimeExcess = velocity.compute_local_trip_time_excess(
                      localMaxAllowedVels, self.velocityArcLengthStepSize)
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
        #print("tube cost: " + str(self.tubeCost))
        #print("pylon cost: " + str(self.pylonCost))
        #print("trip time excess: " + str(self.triptimeExcess))
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
    def merge_two_tube_graphs(cls, tubeGraphA, tubeGraphB):
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
                                                  for tubeGraph in tubeGraphs]
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
        tubeGraphsSetB, TubeGraphsSet, TubeGraphsSet.is_graph_pair_compatible,
                                              TubeGraph.merge_two_tube_graphs)
    return mergedTubeGraphs

        
def build_tube_graphs(elevationProfile):
    pylonsLattice = PylonsLattice(elevationProfile)
    tubeEdgesSets = TubeEdgesSets(pylonsLattice)
    tubeGraphsSets = map(TubeGraphsSet.init_from_tube_edges_set,
                                   tubeEdgesSets.finalEdgesSets)
    tubeGraphsSetsTree = mergetree.MasterTree(tubeGraphsSets,
        tube_graphs_set_pair_merger, abstract.graphs_set_updater)
    rootTubeGraphsSet = tubeGraphsSetsTree.root
    selectedTubeGraphs = rootTubeGraphsSet.selectedGraphs
    return selectedTubeGraphs
  


 
def compute_pylon_cost(pylonHeight):    
    if pylonHeight >= 0:
        heightCost = pylonHeight * config.pylonCostPerMeter
    else:
        heightCost = -pylonHeight * 5 * config.pylonCostPerMeter
    pylonCost = config.pylonBaseCost + heightCost
    return pylonCost

def compute_tube_cost(tubeLength):
    tubeCost = config.tubeCostPerMeter * tubeLength
    return tubeCost

def build_tube_profile_v2(elevationProfile):
    geospatials = [elevationPoint["geospatial"] for elevationPoint
                                                in elevationProfile]
    landElevations = [elevationPoint["landElevation"] for elevationPoint
                                                     in elevationProfile]
    arcLengths = [elevationPoint["distanceAlongPath"] for elevationPoint
                                                     in elevationProfile]
    sInterp, zInterp = landscape.matchLandscape_v1(arcLengths,
                               landElevations, "elevation")
    tubeSpline = PchipInterpolator(sInterp, zInterp)
    tubeElevations = tubeSpline(arcLengths)
    spatialXValues, spatialYValues = zip(*geospatials)
    pylonHeights = util.subtract(tubeElevations, landElevations)    
    tubeCoords = zip(spatialXValues, spatialYValues, tubeElevations)
    tubeLength = util.compute_total_arc_length(tubeCoords)
    totalPylonCost = sum(map(compute_pylon_cost, pylonHeights))    
    totalTubeCost = compute_tube_cost(tubeLength)
    return [totalTubeCost, totalPylonCost, tubeElevations]

"""
def curvature(i, j, arcLengths, elevations):
    x0, x1 = [arcLengths[i], arcLengths[j]]
    y0, y1 = [elevations[i], elevations[j]]
    tht0, tht1  = [0, 0]
    k, K, L = clothoid.buildClothoid(x0, y0, tht0, x1, y1, tht1)
    extremalCurvatures = [k + L*K, k]
    return max(np.absolute(extremalCurvatures))

def test(i, j, arcLengths, elevations, cached):
    if cached[i][j]:
        return True
    else:
        cached[i][j] = cached[j][i] = True
        curvatureTol = config.linearAccelConstraint/config.maxSpeed**2
        return curvature(i, j, arcLengths, elevations) > curvatureTol

def bad(index, tubeProfile, arcLengths, elevations, cached):       
    indexInsertedAt = util.sorted_insert(index, tubeProfile)
    backwardValid = test(tubeProfile[indexInsertedAt-1],
                          tubeProfile[indexInsertedAt],
                          arcLengths, elevations, cached) 
    forwardValid = test(tubeProfile[indexInsertedAt],
                        tubeProfile[indexInsertedAt+1],
                        arcLengths, elevations, cached)
    indexValid = backwardValid or forwardValid
    tubeProfile.pop(indexInsertedAt)
    return indexValid

def match_point(elevationIndices, tubeProfileIndices,
                     arcLengths, elevations, cached):
    i = 0
    while (bad(elevationIndices[i], tubeProfileIndices,
                        arcLengths, elevations, cached) and
                        i < len(elevationIndices) - 1):
        i += 1
    if i == len(elevationIndices) - 1:
        print "Exhausted the landscape. Could not find a point to match."
        return False
    else:
        util.sorted_insert(elevationIndices.pop(i), tubeProfileIndices)
        return True

def reverse_sort_indices(aList):
    listIndices = range(len(aList))
    sortedIndices = sorted(listIndices, key = lambda i: aList[i], reverse=True)
    return sortedIndices

def get_selected_tube_points(elevationProfile):
    #Add the endpoint indices to the tube profile
    tubeProfileIndices = [0, len(elevationProfile)-1]
    elevations = [elevationPoint["landElevation"] for elevationPoint
                                                 in elevationProfile]
    arcLengths = [elevationPoint["distanceAlongPath"] for elevationPoint
                                                     in elevationProfile]
    #we now sort the remaining landscape.
    truncatedElevations = elevations[1 : len(elevations)]
    sortedElevationIndices = reverse_sort_indices(truncatedElevations)
    elevationIndices = [index + 1 for index in sortedElevationIndices]
    cached = [[0 for i in range(len(elevations))]
                 for i in range(len(elevations))]
    #l = 0
    while match_point(elevationIndices, tubeProfileIndices,
                      arcLengths, elevations, cached):
        pass
        #l += 1
        #print "matched the "+ str(l)+ "th point."
    selectedElevations = [elevations[index] for index in tubeProfile]
    selectedArcLengths = [arcLengths[index] for index in tubeProfile]
    return [selectedArcLengths, selectedElevations]

def build_tube_profile(elevationProfile):    
    arcLengths = [elevationPoint["distanceAlongPath"] for elevationPoint
                                                     in elevationProfile]
    selectedArcLengths, selectedElevations = get_selected_tube_points(
                                                         elevationProfile)
    tubeSpline = PchipInterpolator(selectedArcLengths, selectedElevations)
    tubeElevations = tubeSpline(arcLengths)
    return tubeElevations
"""   
