import mpl_toolkits.basemap.pyproj as pyproj

def omerc_proj(startLonLat, endLonLat):
    startLon, startLat = startLonLat
    endLon, endLat = endLonLat
    centerLat = (startLat + endLat)/2.0
    centerLon = (startLon + endLon)/2.0
    return pyproj.Proj('+proj=omerc +lon_0='+str(centerLon)+' +lat_0='+str(centerLat)
                       +' +lon_2='+str(endLon)+' +lat_2='+str(endLat)
                       +' +lon_1='+str(startLon)+' +lat_1='+str(startLat))
    
def lonlat_to_xy(lonlat,proj):
    return proj(lonlat[0], lonlat[1])

def xy_to_lonlat(xy, proj):
    return proj(xy[0], xy[1], inverse=True)


