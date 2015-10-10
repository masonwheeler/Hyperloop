"""
Original Developer: David Roberts
Purpose of Module: To provide projection functionality
Last Modified: 8/10/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add docstrings
"""

# Standard Modules:
import numpy as np
import pyproj

# Our Modules:
import util
import config

def get_omerc_proj(start_lon_lat, end_lon_lat):
    """Provides the Oblique Mercator Projection"""
    start_lon, start_lat = start_lon_lat
    end_lon, end_lat = end_lon_lat
    center_lat = (start_lat + end_lat) / 2.0
    center_lon = (start_lon + end_lon) / 2.0
    parameter_string = '+proj=omerc' \
        + ' +lon_0=' + str(center_lon) + ' +lat_0=' + str(center_lat) \
        + ' +lon_2=' + str(end_lon) + ' +lat_2=' + str(end_lat) \
        + ' +lon_1=' + str(start_lon) + ' +lat_1=' + str(start_lat)
    if config.VERBOSE_MODE:
        print "The parameters of the projection are:"
        print parameter_string
    omerc_proj = pyproj.Proj(parameter_string)
    return omerc_proj

def get_albers_proj():
    """Provides the Albers Conical Projection"""
    albers_proj = pyproj.Proj("+proj=aea \
                              +lat_1=29.5 \
                              +lat_2=45.5 \
                              +lat_0=23 \
                              +lon_0=-96 \
                              +x_0=+y_0=0 \
                              +ellps=GRS80 \
                              +datum=NAD83 \
                              +units=m \
                              +no_defs")
    return albers_proj

def get_usgs_proj():
    """Provides the standard USGS projection"""
    usgs_proj = pyproj.Proj(init='epsg:3857')
    return usgs_proj

def latlng_to_geospatial(latlng, proj):
    """Converts latitude longitude coordinates to geospatial coordinates"""
    return proj(latlng[1], latlng[0])

def geospatial_to_latlng(geospatial, proj):
    """Converts geospatial coordinates to latitude longitude coordinates"""
    lonlat = proj(geospatial[0], geospatial[1], inverse=True)
    return util.swap_pair(lonlat)

def latlngs_to_geospatials(latlngs, proj):
    """Converts list of lat-lng coords to list of geospatial coords"""
    geospatials = np.array([latlng_to_geospatial(latlng, proj)
                            for latlng in latlngs.tolist()])
    return geospatials 

def geospatials_to_latlngs(geospatials, proj):
    """Converts list of geospatial coords to list of lat-lng coords"""
    latlngs = np.array([geospatial_to_latlng(geospatial, proj)
                        for geospatial in geospatials.tolist()])
    return latlngs

def set_projection(start_lat_lng, end_lat_lng):
    """Sets the projection used for converting lat-lngs to geospatials"""
    #start_lon_lat, end_lon_lat = util.swap_pairs([start_lat_lng, end_lat_lng])
    projection = get_albers_proj()
    return projection
