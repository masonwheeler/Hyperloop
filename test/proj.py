import pyproj

def omerc_proj(startLonLat, endLonLat):
    startLon, startLat = startLonLat
    endLon, endLat = endLonLat
    centerLat = (startLat + endLat)/2.0
    centerLon = (startLon + endLon)/2.0
    return pyproj.Proj('+proj=omerc +lon_0='+str(centerLon)+' +lat_0='+str(centerLat)
                       +' +lon_2='+str(endLon)+' +lat_2='+str(endLat)
                       +' +lon_1='+str(startLon)+' +lat_1='+str(startLat))

def albers_proj():
    albers = pyproj.Proj("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=+y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs")
    return albers
    
def lonlat_to_xy(lonlat,proj):
    return proj(lonlat[0], lonlat[1])

def xy_to_lonlat(xy, proj):
    return proj(xy[0], xy[1], inverse=True)

def lonlats_to_xys(lonlats,proj):
    return [lonlat_to_xy(lonlat,proj) for lonlat in lonlats]

def xys_to_lonlats(xys, proj):
    return [xy_to_lonlat(xy,proj) for xy in xys]
