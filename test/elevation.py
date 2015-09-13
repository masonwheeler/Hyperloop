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
import proj

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

def get_elevation_profile(geospatials, distances):
    """Build elevation profile for a list of geospatials
    """
    latlngs = proj.geospatials_to_latlngs(geospatials, config.PROJ)
    elevations = usgs_elevation(latlngs)
    elevation_profile = []
    for i in range(len(geospatials)):
        elevation_point = {"latlng": latlngs[i],
                           "geospatial": geospatials[i],
                           "land_elevation": elevations[i],
                           "distance_along_path": distances[i]}
        elevation_profile.append(elevation_point)
    return elevation_profile

def get_elevation_profile_v2(geospatials, distances):
    """Build elevation profile for a list of geospatials
    """
    latlngs = proj.geospatials_to_latlngs(geospatials, config.PROJ)
    elevations = usgs_windowed_elevation(latlngs)
    elevation_profile = []
    for i in range(len(geospatials)):
        elevation_point = {"latlng": latlngs[i],
                           "geospatial": geospatials[i],
                           "land_elevation": elevations[i],
                           "distance_along_path": distances[i]}
        elevation_profile.append(elevation_point)
    return elevation_profile
