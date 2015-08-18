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














