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


def google_elevation(coords):
    """Fetches elevations from google's dataset for a list of lat lng pairs
    """
    args = {
        'locations': '|'.join([str(coord[0]) + ',' + str(coord[1])
                               for coord in coords])
    }

    url = config.ELEVATION_BASE_URL + '?' + urllib.urlencode(args)
    response = simplejson.load(urllib.urlopen(url))

    elevation_array = []
    if response['status'] == 'OK':
        # Create a dictionary for each results[] object
        for result_set in response['results']:
            elevation_array.append(result_set['elevation'])
    else:
        print response['status']

    return elevation_array


def usgs_elevation(latlngs):
    """Fetches elevations from usgs dataset for a list of lat lng pairs
    """   
    elevations = [usgs.get_elevation(latlng) for latlng in latlngs]
    #elevations = usgs.get_elevations(latlngs)
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
