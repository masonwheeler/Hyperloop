"""
Original Developer: Jonathan Ward
Purpose of Module: To obtain the elevation of each coordinate in
                   a list of latitude longitude coords.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify module usage.
"""

# Standard Modules
import urllib
import simplejson

# Our Modules
import config
import usgs
import util

import time

def usgs_elevation(latlngs):
    """Fetches elevations from usgs dataset for a list of lat lng pairs
    """   
    elevations = [usgs.get_elevation(latlng) for latlng in latlngs]
    return elevations

def usgs_windowed_elevation(latlngs):
    """Fetches elevations from usgs dataset for a list of lat lng pairs
    """   
    elevations = usgs.get_elevations(latlngs)
    return elevations

def get_elevation_profile(geospatials, latlngs, arc_lengths):
    """Build elevation profile for a list of geospatials
    """
    elevations = usgs_elevation(latlngs)
    elevation_profile = []
    for i in range(len(geospatials)):
        elevation_point = {"latlng": latlngs[i],
                           "geospatial": geospatials[i],
                           "landElevation": elevations[i],
                           "arcLength": arc_lengths[i]}
        elevation_profile.append(elevation_point)
    return elevation_profile

def get_elevation_profile_v2(geospatials, latlngs, arc_lengths):
    """Build elevation profile for a list of geospatials
    """
    elevations = usgs_windowed_elevation(latlngs)
    elevation_profile = []
    for i in range(len(geospatials)):
        elevation_point = {"latlng": latlngs[i],
                           "geospatial": geospatials[i],
                           "landElevation": elevations[i],
                           "arcLength": arc_lengths[i]}
        elevation_profile.append(elevation_point)
    return elevation_profile

def merge_elevation_profiles(elevation_profile_a, elevation_profile_b):
    boundary_point = elevation_profile_a[-1]
    arc_length_offset = boundary_point["arcLength"]
    shifted_elevation_profile_b = []
    for elevation_point in elevation_profile_b:
        shifted_elevation_point = {
            "latlng": elevation_point["latlng"],
            "geospatial": elevation_point["geospatial"],
            "landElevation": elevation_point["landElevation"],
            "arcLength": elevation_point["arcLength"] + arc_length_offset}
        shifted_elevation_profile_b.append(shifted_elevation_point)
    shifted_arc_lengths_b = [ep["arcLength"] for ep in elevation_profile_b]
    merged_elevation_profile = util.smart_concat(elevation_profile_a,
                                         shifted_elevation_profile_b)
    return merged_elevation_profile

class ElevationProfile(object):
    
    def get_land_elevations(self):
        land_elevations = [usgs.get_elevation(latlng)
                           for latlng in self.latlngs]
        return land_elevations
    
    def get_land_elevations_v2(self):
        land_elevations = usgs.get_elevations(self.latlngs)
        return land_elevations

    def __init__(self, geospatials, latlngs, arc_lengths, land_elevations=None):
        self.geospatials = geospatials
        self.latlngs = latlngs
        self.arc_lengths = arc_lengths
        if land_elevations = None:
            self.land_elevations = self.get_land_elevations
        else:
            self.land_elevations = land_elevations

    @classmethod
    def merge_two_elevation_profiles(elevation_profile_a, elevation_profile_b):
        merged_geospatials = util.smart_concat(elevation_profile_a.geospatials,
                                               elevation_profile_b.geospatials)
        merged_latlngs = util.smart_concat(elevation_profile_a.latlngs,
                                           elevation_profile_b.latlngs)
        merged_land_elevations = util.smart_concat(
                                    elevation_profile_a.land_elevations,
                                    elevation_profile_b.land_elevations)
        arc_length_offset = elevation_profile_a.arc_lengths[-1]
        shifted_arc_lengths_b = [arc_length + arc_length_offset for arc_length
                                 in elevation_profile_b.arc_lengths]
        merged_arc_lengths = util.smart_concat(elevation_profile_a.arc_lengths,
                                                         shifted_arc_lengths_b)
        data = cls(merged_geospatials, merged_latlngs, merged_arc_lengths,   
                                                   merged_land_elevations)
        return data
        
