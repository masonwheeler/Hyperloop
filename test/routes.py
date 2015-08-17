"""
Original Developer: Jonathan Ward
Purpose of Module: To provide classes for final output
Last Modified: 8/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

class Path:
    def sample_geospatials(self, graphGeospatials, geospatial_sample_distance):
        return sampledGeospatials
        
    def interpolate_geospatials(self, sampledGeospatials)
        return interpolatedGeospatials

    def interpolate_latlngs(self, interpolatedGeospatials):
        return interpolatedLatLngs

    def compute_land_cost(self, interpolatedLatLngs):
        return landCost

    def get_land_elevations(self, interpolatedLatLngs):
        return landElevations

    def build_pylons(self, landElevations):
        return pylons

    def build_tube(self, pylons):
        return tubeCoordinates

    def compute_pylon_cost(self, pylons):
        return pylonCost
    
    def compute_tube_cost(self, tubeCoordinates):
        return tubeCost
    
    def compute_tube_curvature(self, tubeCoordinates):
        return tubeCurvature

    def compute_max_speeds(self, tubeCurvature, maxLateralAccel,
                                                maxVerticalAccel):
        return maxSpeeds
    
    def __init__(self, graphGeospatials):
         

class VelocityProfile:    
    def __init__(self,):


class VelocityProfilesSet:
    def __init__(self, path)


class Route:
    def __init__(self, path, velocityProfile):

    def as_dict(self):
        routeDict = {
                     "latlngs" : self.latlngs,
                     "landCost" : self.landCost,
                     "tubeElevations" : self.tubeElevations,
                     "pylons" : self.pylons,
                     "tubeCost" : self.tubeCost,
                     "pylonCost" : self.pylonCost,
                     "velocityProfile" : self.velocityProfile,
                     "comfortRating" : self.comfortRating,
                     "tripTime" : self.tripTime
                     }




