"""
Original Developer: Jonathan Ward
Purpose of Module: To provide classes for final output
Last Modified: 8/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

import interpolate
import proj
import landcover
import elevation

class Path2d:
    def sample_geospatials(self, graphGeospatials, geospatialSampleDistance):
        sampledGeospatials = interpolate.sample_path(graphGeospatials,
                                             geospatialSampleDistance)
        return sampledGeospatials
        
    def get_interpolating_geospatials(self, sampledGeospatials):
        xArray, yArray = points_2d_to_arrays(sampledGeospatials)
        numPoints = len(sampledGeospatials)
        sValues = interpolate.get_s_values(numPoints)
        xSpline, ySpline = interpolate.interpolating_splines_2d(xArray, yArray,
                                                                       sValues)
        xValues = interpolate.get_spline_values(xSpline, sValues)
        yValues = interpolate.get_spline_values(ySpline, sValues)
        interpolatingGeospatials = [xValues, yValues]
        return interpolatingGeospatials

    def get_interpolating_latlngs(self, interpolatingGeospatials):
        interpolatingLatLngs = proj.geospatials_to_latlngs(
                                           interpolatingGeospatials)
        return interpolatingLatLngs

    def compute_land_cost(self, interpolatingLatLngs):
        landCost = landcover.get_land_cost(interpolatedLatLngs)
        return landCost

    def get_elevation_profile(self, interpolatedLatLngs):
        elevationProfile = elevation.get_elevation_profile(interpolatedLatLngs)
        return elevationProfile

    def get_tube_graphs(self, elevationProfile):
        return tubeGraphs
    
    def __init__(self, spatialGraph):
        graphGeospatials = spatialGraph.geospatials
        sampledGeospatials = self.sample_geospatials(graphGeospatials)
        interpolatingGeospatials = self.get_interpolating_geospatials(
                                                       sampledGeospatials)
        interpolatingLatLngs = self.get_interpolating_lat_lngs(
                                           interpolatingGeospatials)
        elevationProfile = elevation.get_elevation_profile(
                                       interpolatingGeospatials)
        self.landCost = self.compute_land_cost(interpolatingLatLngs)
        self.tubeGraphs = self.get_tube_graphs(self.elevationProfile)


class Path3d:
    def get_velocity_profile_graphs(self, tubeGraph):
        tubeCoords = tubeGraph.tubeCoords
        

    def __init__(self, landCost, tubeGraph):
        self.landCost = landCost
        velocityProfileGraphs = get_velocity_profile_graphs

         
class Route:
    def __init__(self, tube, velocityProfile):

    def as_dict(self):
        routeDict = {
                     "latlngs" : self.latlngs,
                     "landCost" : self.landCost,
                     "tubeElevations" : self.tubeElevations,
                     "pylons" : self.pylons,
                     "tubeCost" : self.tubeCost,
                     "pylonCost" : self.pylonCost,
                     "velocityProfile" : self.velocityProfile,
                     "accelerationProfile" : self.accelerationProfile,
                     "comfortRating" : self.comfortRating,
                     "tripTime" : self.tripTime
                     }




