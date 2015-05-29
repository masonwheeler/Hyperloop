import config
import util
import genBaseLattice
import proj
import transform       

def projectBounds(bounds, startLatLng, endLatLng):
    startLonLat = [startLatLng[1],startLatLng[0]]
    endLonLat = [endLatLng[1],endLatLng[0]]
    omercProj = proj.omerc_proj(startLonLat,endLonLat)
    boundsXY = proj.lonlats_to_xys(bounds)
    startXY = proj.lonlat_to_xy(startLonLat)
    endXY = proj.lonlat_to_xy(endLonLat)
    return transformedBounds 
