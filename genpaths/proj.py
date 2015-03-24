"""
Jonathan Ward 3/24/2015

This file contains the function definitions for generating and validating
routes on the lattice.

TODO:
Add arguments to get_omerc    
Add conical Albers proj    

Most Recent Change: added lat_to_xy and xy_to_latlon
"""

import mpl_toolkits.basemap.pyproj as pyproj

def omerc_proj(startLatLon, endLatLon):
    startLat, startLon = startLatLon
    endLat, endLon = endLatLon
    centerLat = (startLat + endLat)/2
    centerLon = (startLon + endLon)/2
    omerc=pyproj.Proj('+proj=omerc +lon_0=' + centerLon + ' +lat_0=' + centerLat  + ' +lon_2=' + endLon + ' +lat_2= ' + endLat + ' +lon_1=' + startLon + ' +lat_1=' + startLat)
    return omerc

def mrlc_proj():
    mrlc=pyproj.Proj("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs")
    return mrlc

def latlon_to_xy(latlon,proj):
    lat, lon = latlon
    xy = proj(lat, lon)
    return xy

def xy_to_latlon(xy,proj):
    x, y = xy
    latlon = proj(x, y, inverse=True)
    return latlon
