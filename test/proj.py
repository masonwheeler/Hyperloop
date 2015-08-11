"""
Original Developer: David Roberts
Purpose of Module: To provide projection functionality
Last Modified: 8/10/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add docstrings
"""

#Standard Modules:
import pyproj

#Our Modules:
import util
import config

def omerc_proj(startLonLat, endLonLat):
    """Provides the Oblique Mercator Projection"""
    startLon, startLat = startLonLat
    endLon, endLat = endLonLat
    centerLat = (startLat + endLat)/2.0
    centerLon = (startLon + endLon)/2.0
    parameterString = '+proj=omerc' \
    + ' +lon_0=' + str(centerLon) + ' +lat_0=' + str(centerLat) \
    + ' +lon_2=' + str(endLon) + ' +lat_2=' + str(endLat) \
    + ' +lon_1=' + str(startLon) + ' +lat_1=' + str(startLat) 
    if config.verboseMode:
        print("The Parameters of the projection are:")
        print(parameterString)
    omercProj =  pyproj.Proj(parameterString)
    return omercProj

def albers_proj():
    """Provides the Albers Conical Projection"""
    albersProj = pyproj.Proj("+proj=aea \
                              +lat_1=29.5 \
                              +lat_2=45.5 \
                              +lat_0=23 \
                              +lon_0=-96 \
                              +x_0=+y_0=0 \
                              +ellps=GRS80 \
                              +datum=NAD83 \
                              +units=m \
                              +no_defs")
    return albersProj

def usgs_proj():
    """Provides the standard USGS projection"""
    usgsProj = pyproj.Proj(init='epsg:3857')
    return usgsProj
    
def latlng_to_geospatial(latlng, proj):    
    """Converts latitude longitude coordinates to geospatial coordinates"""
    return proj(latlng[1], latlng[0])

def geospatial_to_latlng(geospatial, proj):
    """Converts geospatial coordinates to latitude longitude coordinates"""
    lonlat = proj(geospatial[0], geospatial[1], inverse=True)
    return util.swap_pair(lonlat)

def latlngs_to_geospatials(latlngs, proj):
    """Converts list of lat-lng coords to list of geospatial coords"""
    return [latlng_to_geospatial(latlng, proj) for latlng in latlngs]

def geospatials_to_latlngs(geospatials, proj):
    """Converts list of geospatial coords to list of lat-lng coords"""
    latlngs = [geospatial_to_latlng(geospatial, proj)
               for geospatial in geospatials]
    return latlngs

def set_projection(startLatLng, endLatLng):
    """Sets the projection used for converting lat-lngs to geospatials"""
    startLonLat, endLonLat = util.swap_pairs([startLatLng, endLatLng])
    #config.proj = omerc_proj(startLonLat, endLonLat)
    config.proj = albers_proj()

