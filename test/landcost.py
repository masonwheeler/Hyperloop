import config
import geotiff
import directions
import proj
import transform
import util

def latlng_distance(latLngA,latLngB):
    lonLatA = util.swapPair(latLngA)
    lonLatB = util.swapPair(latLngB)
    xyA = proj.LonLatToXY(lonLatA,config.proj)
    xyB = proj.LonLatToXY(lonLatB,config.proj)
    distanceAB = util.norm(util.subtract(xyA,xyB))
    return distanceAB

def is_latlng_in_rightofway(latLng,directionsCoords):
    for coord in directionsCoords:
        if latlng_distance(latLng,coord) < config.rightOfWayDistance:
            return True
    return False
    
def latlng_landCost(latLng,directionsCoords):
    if is_latlng_in_rightofway(latLng,directionsCoords):
        landCost = 0
    else:
        pixelVal = geotiff.latlng_to_pixel(config.geotiffFilePath,latLng)
        landCost = config.costTable[pixelVal]
    return landCost
