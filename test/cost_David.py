from osgeo import gdal
from osgeo import osr
import struct

import config
import util
import directions
import proj
import transform
import util
import pyloncost

def xy_distance(xyA,xyB):        
    distanceAB = util.norm(util.subtract(xyA,xyB))
    return distanceAB

def xyCoord_in_rightofway(xyCoord,projectedDirections):
    for directionCoord in projectedDirections:
        if xy_distance(xyCoord,directionCoord) < config.rightOfWayDistance:
            return True
    return False

def pixel_val(ct, gt, rb, lonlatCoord):
    xVal, yVal, zVal = ct.TransformPoint(*lonlatCoord)
    x = int((xVal - gt[0])/gt[1])
    y = int((yVal - gt[3])/gt[5])
    structval = rb.ReadRaster(x,y,1,1,buf_type=gdal.GDT_Float32)
    intval = struct.unpack('f', structval)
    pixelVal = intval[0]
    return pixelVal

def land_cost(ct, gt, rb, xyCoord, lonlatCoord, directionsCoords):
    if xyCoord_in_rightofway(xyCoord, directionsCoords):
	return 0
    else:
	return pixel_val(ct,gt,rb,lonlatCoord)

def attach_cost(geotiff,lattice,directionsCoords,primVec):
    ds = gdal.Open(geotiff)
    gt = ds.GetGeoTransform()
    rb = ds.GetRasterBand(1)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    srsLatLon = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srsLatLon,srs)

    for eachSlice in lattice:
        for eachPoint in eachSlice:
	    latticeCoords, xyCoords, lonlatCoords = eachPoint
            landCost=land_cost(ct,gt,rb,xyCoords,lonlatCoords,directionsCoords)
#            pylonCost = pyloncost.pylon_cost(xyCoords, primVec,
#            config.pylonSpacing, config.maxSpeed, config.gTolerance,
#            config.costPerPylonLength, config.pylonBaseCost)
            eachPoint.append(landCost)
    return lattice

