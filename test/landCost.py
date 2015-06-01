import config
import geotiff
import directionsCoords
import proj
import transform
import util

def get_latLngLandCost(latLng):
    pixelVal = geotiff.latLngToPixel(config.geotiffFilePath)
    landCost = config.costTable[pixelVal]
    return landCost

def get_latLngDistance(latLngA,latLngB):
    lonLatA = util.swapPair(latLngA)
    lonLatB = util.swapPair(latLngB)
    xyA = proj.lonlat_to_xy(lonLatA,config.proj)
    xyB = proj.lonlat_to_xy(lonLatB,config.proj)
    distanceAB = get_distance(xyA,xyB)
    return distanceAB

def is_latLng_in_rightOfWay(latLng,directionsCoords):
    for coord in directionsCoords:
        if get_latLngDistance(latLng,coord) < config.rightOfWayDistance:
            return True
    return False
    
    
