"""
Original Developer: Jonathan Ward
iesPurpose of Module: To provide a naive velocity profile generation method
Last Modified: 8/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

#Standard Modules
import numpy as np

#Our Modules
import abstract
import comfort
import interpolate

def velocities_to_velocity_pairs(velocities):
    velocityPairs = util.to_pairs(velocities)
    return velocityPairs

def time_elapsed_to_velocity(velocityPair, timeElapsed):
    startVelocity, endVelocity = velocityPair
    startVelocityTime, startVelocityVal = startVelocity
    endVelocityTime, endVelocityVal = endVelocity 
    velocityDifference = endVelocityVal - startVelocityVal
    timeDifference = endVelocityTime - startVelocityTime
    relativeVelocityVal = timeElapsed * velocityDifference/timeDifference
    velocityVal = startVelocityVal + relativeVelocityVal
    velocityTime = startVelocityTime + timeElapsed
    velocity = [velocityTime, velocityVal]
    return velocity    

def sample_velocity_pair(velocityPair, timeStepSize, timeElapsed):
    sampledVelocities = []    
    startVelocity, endVelocity = velocityPair
    startVelocityTime, startVelocityVal = startVelocity
    endVelocityTime, endVelocityVal = endVelocity 
    velocityPairtimeDifference = endVelocityTime - startVelocityTime
    while timeElapsed <= velocityPairTimeDifference:
        velocity = time_elapsed_to_velocity(velocityPair, timeElapsed)
        sampledVelocities.append(velocity)
        timeElapsed += timeStepSize
    timeElapsed -= velocityPairTimeDifference
    return [sampledVelocities, timeElapsed]    

def sample_velocities(velocitiesByTime, timeStepSize):
    timeElapsed = 0
    velocities = []
    for velocityPair in velocityPairs:
        sampledVelocities, timeElapsed = sample_velocity_pair(velocity_pair,
                                                                timeElapsed)
        velocities += sampledVelocities 
    return velocities
                   
def velocities_by_arclength_to_time_checkpoints_array(velocitiesByArcLength, 
                                              velocityArcLengthStepSize):
    numVelocities = velocitiesByArcLength.length
    velocityArcLengthStepSizeArray = np.empty(numVelocities)
    velocityArcLengthStepSizeArray = np.fill(velocityArcLengthStepSize)
    paddedVelocities = np.append(velocitiesByArcLength, 0)
    shiftedVelocities = np.insert(velocitiesByArcLength, 0, 0)    
    paddedVelocitiesSums = np.add(paddedVelocities, shiftedVelocities)
    velocitiesSums = paddedVelocitiesSums[1:-1]
    meanVelocitiesByArcLength = np.divide(velocitiesSums, 2)
    times = np.divide(velocityArcLengthStepSizeArray,
                     meanVelocitiesByArcLength)
    timeCheckpointsArray = np.insert(times, 0, 0)    
    return timeCheckPointsArray
    
def compute_trip_time(velocitiesByArcLength, velocityArcLengthStepSize):
    timeCheckpointsArray = velocities_by_arclength_to_time_checkpoints_array(
                            velocitiesByArcLength, velocityArclengthStepSize)
    tripTime = np.sum(timeCheckpointsArray)
    return tripTime    

def reparametrize_velocities(velocitiesByArcLength, velocityArclengthStepSize,
                                                                timeStepSize):    
    timeCheckpointsArray = velocities_by_arclength_to_time_checkpoints_array(
                            velocitiesByArcLength, velocityArclengthStepSize)
    timesElapsed = np.cumsum(timeCheckpointsArray)
    velocitiesByTime = np.array([timesElapsed, velocitiesByArcLength]).T
    sampledVelocitiesByTime = sample_velocities(velocitiesByTime)
    return sampledVelocitiesByTime
    
def compute_local_trip_time_excess(maxAllowedVelocities,
                                     arclengthStepSize):
    numVelocities = maxAllowedVelocities.length
    maxPossibleVelocities.empty(numVelocities)
    maxPossibleVelocities.fill(config.maxPossibleVelocity)
    minimumPossibleTripTime = compute_trip_time(maxPossibleVelocities,
                                                velocityArclengthStepSize)
    minimumAllowedTripTime = compute_trip_time(maxAllowedVelocities,
                                              velocityArclengthStepSize)
    localTripTimeExcess = minimumAllowedTripTime - minimumPossibleTripTime
    return localTripTimeExcess

def compute_max_endpoint_velocities(maxLinearAccel, maxPossibleVelocity,
                                             velocityArclengthStepSize):
    velocity = 0    
    maxEndPointVelocities = []
    while velocity < maxPossibleVelocity:
        maxEndPointVelocites.append(velocity)
        velocity = np.sqrt(2 * velocityArcLengthStepSize * maxLinearAccel \
                           + np.square(currentVelocity))
    return maxEndPointVelocities    

def global_max_allowed_velocities(localMaxAllowedVelocities,
                                     maxEndPointVelocities):
    endpointVelocitiesLength = maxEndPointVelocities.length
    maxStartVelocities = maxEndPointVelocities
    maxEndVelocities = maxEndPointVelocities[::-1]
    localMaxStartVelocities = localMaxAllowedVelocities[
                                :endpointVelocitiesLength]
    localMaxEndVelocities = localMaxAllowedVelocities[
                                -endpointVelocitiesLength:]
    effectiveMaxStartVelocities = np.minimum(maxStartVelocities,
                                             localMaxStartVelocities)
    effectiveMaxEndVelocities = np.minimum(maxEndVelocities,
                                           localMaxEndVelocities)
    globalMaxAllowedVelocities = localMaxAllowedVelocities
    globalMaxAllowedVelocities[:endpointVelocitiesLength] = \
        effectiveMaxStartVelocities
    globalMaxAllowedVelocities[-endpointVelocitiesLength:] = \
         effectiveMaxEndVelocities
    return globalMaxAllowedVelocities       


class Velocity(abstract.AbstractPoint):
    def __init__(self, speed, distanceAlongPath, velocityId):
        velocityCoords = {"speed" : speed,
                          "distanceAlongPath":  distanceAlongPath}
        abstract.AbstractPoint.__init__(velocityCoords, velocityId)


class VelocitiesSlice(abstract.AbstractSlice):

    def velocities_builder(self, velocitiesSliceBounds, lowestVelocityId):
        maxSpeed = velocitiesSliceBounds["maxSpeed"]
        minSpeed = velocitiesSliceBounds["minSpeed"]
        speedStepSize = velocitiesSliceBounds["speedStepSize"]
        distanceAlongPath = velocitiesSliceBounds["distanceAlongPath"]
        speedDifference = maxSpeed - minSpeed
        speedOptions = util.build_grid2(speedDifference,
                           speedsStepSize, minimumSpeed)
        velocityIds = [index + lowestVelocityId for index
                       in range(len(speedOptions))]
        velocityOptions = [Velocity(speedOptions[i], distanceAlongPath,
                           velocityIds[i]) for i in range(len(velocityIds))]
        return velocityOptions

    def __init__(self, velocitiesSliceBounds, lowestVelocityId):
        abstract.AbstractSlice.__init__(velocitiesSliceBounds,
                   lowestVelocityId, self.velocities_builder)


class VelocitiesLattice(abstract.AbstractLattice):

    def max_allowed_velocities_to_velocity_slice_bounds(maxAllowedVelocities):
        numArcLengthSteps = maxAllowedVelocities.length - 1
        arcLengthStepsArray = np.empty(numArcLengthPoints)
        arcLengthStepsArray = np.fill(config.arclengthStepSize)
        partialArcLengthArray = np.cumsum(arcLengthStepsArray)
        arcLengthArray = np.insert(partialArcLengthArray, 0, 0)
        velocitySlicesBounds = []
        for i in range(len(maxAllowedVelocities.length)):
            maxSpeed = maxAllowedVelocities[i]
            minSpeed = config.speedStepSize
            speedStepSize = config.speedStepSize
            distanceAlongPath = arcLengthArray[i]
            velocitySliceBounds = {"maxSpeed" : maxSpeed,
                                   "minSpeed" : minSpeed,
                                   "speedStepSize" : speedStepSize,
                                   "distanceAlongPath" : distanceAlongPath}
            velocitySlicesBounds.append(velocitySliceBounds)
        return velocitySlicesBounds

    def __init__(self, maxAllowedVelocities):
        velocitySlicesBounds = max_allowed_velocities_to_velocity_slice_bounds(
                                                          maxAllowedVelocities)
        abstract.AbstractLattice.__init__(velocitiesSlicesBounds,
                                                 VelocitiesSlice)


class VelocityProfileEdge(abstract.AbstractEdge):
    def __init__(self, startVelocity, endVelocity):
        abstract.AbstractEdge.__init__(startVelocity, endVelocity) 


class VelocityProfileEdgesSets(abstract.AbstractEdgesSets):
    velocityProfileEdgeDegreeConstraint = config.velocityProfileDegreeConstraint

    def velocity_profile_edge_builder(self, startVelocity, endVelocity):
        velocityProfileEdge = VelocityProfileEdge(startVelocity, endVelocity)
        return velocityProfileEdge

    @staticmethod
    def is_velocity_profile_edge_pair_compatible(self, velocityProfileEdgeA,
                                               velocityProfileEdgeB):
        return abstract.AbstractEdgesSets.is_edge_pair_compatible(
                        velocityProfileEdgeA, velocityProfileEdgeB,     
                          self.velocityProfileEdgeDegreeConstraint)

    def __init__(self, velocitiesLattice):
        abstract.AbstractEdgesSets.__init__(velocitiesLattice,
                           self.velocity_profile_edge_builder,
               self.is_velocity_profile_edge_pair_compataible)


class VelocityProfileGraph(abstract.AbstractGraph):
    velocityArcLengthStepSize = config.velocityArcLengthStepSize
    def reparametrize_velocities(self, velocitiesByArclength):
        velocitiesByTime = reparametrize_velocities(velocitiesByArcLength,
                                                velocityArcLengthStepSize)
        return velocitiesByTime

    def compute_comfort(self, velocitiesByTime):        
        return comfort

    def compute_trip_time(self, velocitiesByTime):
        return tripTime

    def __init__(self, startId, endId, startAngle, endAngle, numEdges,
                                               velocitiesByArclength):
        abstract.AbstractGraph.__init__(startId, endId, startAngle, endAngle,
                                                                    numEdges)
        self.velocitiesByArcLength = velocitiesByArcLength
        velocitiesByTime = self.reparametrize_velocity(velocitiesByInArcLength)
        self.velocitiesByTime = velocitiesByTime
        self.comfort = self.compute_comfort(velocitiesByTime)
        self.triptime = self.compute_trip_time(velocitiesByTime)

    @classmethod
    def init_from_velocity_profile_edge(cls, velocityProfileEdge):
        startId = velocityProfileEdge.startId
        endId = velocityProfileEdge.endId
        startAngle = velocityProfileEdge.startId
        endAngle = velocityProfileEdge.endId
        numEdges = 1
        velocitiesByArcLength = [
        
    @classmethod
    def merge_two_velocity_profile_graphs(cls, velocityProfileGraphA,
                                               velocityProfileGraphB):
        startId = velocityProfileGraphA.startId
        endId = velocityProfileGraphB.endId
        startAngle = velocityProfileGraphA.startAngle
        endAngle = velocityProfileGraphB.endAngle
        numEdges = velocityProfileGraphA.numEdges + \
                   velocityProfileGraphB.numEdges
        velocitiesByArcLength = velocityProfileGraphA.velocitiesByArcLength + \
                                velocityProfileGraphB.velocitiesByArcLength
        data = cls(startId, endId, startAngle, endAngle, numEdges,
                   velocitiesByArcLength)
        return data


class VelocityProfileGraphsSet(abstract.AbstractGraphsSet):
    def velocity_profile_graphs_comfort_triptime(self, velocityProfileGraphs):
        graphsComfortAndTripTime = [[graph.comfort, graph.triptime] for graph
                                    in velocityProfileGraphs]
        return graphsComfortAndTripTime

    def __init__(self, velocityProfileGraphs):
        minimizeComfort = False
        minimizeTripTime = True
        abstract.AbstractGraphSets.__init__(velocityProfileGraphs,
                    self.velocity_profile_graphs_comfort_triptime,
                                minimizeComfort, minimizeTripTime)

    @classmethod
    def init_from_velocity_profile_edges_sets(cls, velocityProfileEdgesSets):
        velocityProfileGraphs = [
            map(VelocityProfileGraph.init_from_velocity_profile_edge,
                velocityProfileEdgesSet)
            for velocityProfileEdgesSet in velocityProfileEdgesSets]
        return cls(velocityProfileGraphs)


def max_allowed_velocities_to_velocity_profile_graphs(maxAllowedVelocities):
    velocitiesLattice = VelocitiesLattice(maxAllowedVelocities)
    velocityProfileEdgesSets = VelocityProfileEdgesSets(velocitiesLattice)
    velocityProfileGraphsSet = \
         VelocityProfileGraphsSet.init_from_velocity_profile_edges_sets(
            velocityProfileEdgesSets)
    velocityProfileGraphsSetsTree = mergeTree.MasterTree(
         velocityProfileGraphsSet, abstract.graphs_sets_merger,
                                  abstract.graphs_sets_updater)
    rootVelocityProfileGraphsSet = velocityProfileGraphsSetsTree.root
    selectedVelocityProfileGraphs = rootVelocityProfileGraphsSet.selectedGraphs
    return selectedVelocityProfileGraphs
    
