"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a naive velocity profile generation method
Last Modified: 8/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

import abstract


class Velocity(abstract.AbstractPoint):
    def __init__(self, velocity, distanceAlongPath velocityId):
        velocityCoordinates = {"speed" : velocity,
                               "distanceAlongPath":  distanceAlongPath}
        abstract.AbstractPoint.__init__(velocityCoordinates, velocityId)

class VelocitiesSlice(abstract.AbstractSlice):
    velocityOptionsSpacing = config.velocityOptionSpacing

    def velocities_builder(self, minimumSpeed, maximumSpeed, 
                                                minimumVelocityId)
        speedDifference = maximumVelocityVal - minimumVelocityVal
        velocityOptions = util.build_grid2(velocityDifference,
                        velocityOptionsSpacing, minimumVelocity)
        velocityIds = map(lambda x: x + minimumVelocityId,
                              range(len(velocityOptions)))
        enumeratedVelocityOptions = zip(velocityOptions, velocityIds)
        velocityOption

    def __init__(

