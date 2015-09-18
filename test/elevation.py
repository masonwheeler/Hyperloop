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
    
