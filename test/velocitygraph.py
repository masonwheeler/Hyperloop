"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a naive velocity profile generation method
Last Modified: 8/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

import abstract


class Velocity(abstract.AbstractPoint):
    def __init__(self, speed, distanceAlongPath, velocityId):
        velocityCoords = {"speed" : speed,
                          "distanceAlongPath":  distanceAlongPath}
        abstract.AbstractPoint.__init__(velocityCoords, velocityId)

class VelocitiesSlice(abstract.AbstractSlice):
    speedOptionsSpacing = config.speedOptionsSpacing

    def velocities_builder(self, velocitiesSliceBounds, lowestVelocityId):
        speedDifference = velocitiesSliceBounds["speedDifference"]
        distanceAlongPath = velocitiesSliceBounds["distanceAlongPath"]
        minimumSpeed = speedOptionsSpacing
        speedOptions = util.build_grid2(speedDifference,
                        self.speedOptionsSpacing, minimumSpeed)
        velocityIds = [index + lowestVelocityId for index
                       in range(len(speedOptions))]
        velocityOptions = [Velocity(speedOptions[i], distanceAlongPath,
                           velocityIds[i]) for i in range(len(velocityIds))]
        return velocityOptions

    def __init__(self, velocitiesSliceBounds, lowestVelocityId):
        abstract.AbstractSlice.__init__(velocitiesSliceBounds,
                   lowestVelocityId, self.velocities_builder):

class VelocitiesLattice(abstract.AbstractLattice):
    def __init__(self, velocitiesSlicesBounds):
        abstract.AbstractLattice.__init__(velocitiesSlicesBounds,
                                          VelocitiesSlice)

class VelocityProfileEdge(abstract.AbstractEdge);
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

    def __init__(self, velocitiesLattice)
        abstract.AbstractEdgesSets.__init__(velocitiesLattice,
            self.velocity_profile_edge_builder


class VelocityProfileGraph(abstract.AbstractGraph):
    def reparametrize_velocity(self, velocitiesByArclength):
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










