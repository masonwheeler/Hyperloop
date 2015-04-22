"""
Admin: Jonathan Ward 
Last Mod: 4/22/2015
Description: This file contains the function definitions for creating and using map projections
Most Recent Change: swapped latitude and longitude into correct positions

TODO:
Add arguments to get_omerc    
Add conical Albers proj    


"""

import mpl_toolkits.basemap.pyproj as pyproj

def omerc_proj(startLonLat, endLonLat):
    startLon, startLat = startLonLat
    startLatStr = str(startLat)
    startLonStr = str(startLon)
    endLon, endLat = endLonLat
    endLatStr = str(endLat)
    endLonStr = str(endLon)
    centerLat = (startLat + endLat)/2.0
    centerLatStr = str(centerLat)
    centerLon = (startLon + endLon)/2.0
    centerLonStr = str(centerLon)
    omerc=pyproj.Proj('+proj=omerc +lon_0=' + centerLonStr + ' +lat_0=' + centerLatStr  + ' +lon_2=' + endLonStr + ' +lat_2= ' + endLatStr + ' +lon_1=' + startLonStr + ' +lat_1=' + startLatStr)
    return omerc

def mrlc_proj():
    mrlc=pyproj.Proj("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs")
    return mrlc

def lonlat_to_xy(lonlat,proj):
    lon, lat = lonlat
    xy = proj(lon, lat)
    return xy

def xy_to_lonlat(xy,proj):
    x, y = xy
    lonlat = proj(x, y, inverse=True)
    return lonlat

startLonLat = [-118.25, 34.05]
endLonLat = [-122.4167, 37.7833]
centerLonLat = [(startLonLat[0] + endLonLat[0])/2.0, (startLonLat[1] + endLonLat[1])/2.0]
omerc = omerc_proj(startLonLat,endLonLat)
mrlc = mrlc_proj()
startXY = lonlat_to_xy(startLonLat,omerc)
#print(startXY)
endXY = lonlat_to_xy(endLonLat,omerc)
#print(endXY)
centerXY = lonlat_to_xy(centerLonLat,omerc)
#print(centerXY)