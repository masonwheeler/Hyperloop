import pyproj

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

def lonLats_to_xys(lonlats,proj):
    return [lonlat_to_xy(lonlat,proj) for lonlat in lonlats]

def xys_to_lonlats(xys, proj):
    return [xy_to_lonlat(xy,proj) for xy in xys]
