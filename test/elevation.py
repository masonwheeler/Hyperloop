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
