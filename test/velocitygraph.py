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
    def 

