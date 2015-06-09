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

def attach_cost(geotiff,lattice,directionsCoords):
    ds = gdal.Open(geotiff)
    gt = ds.GetGeoTransform()
    rb = ds.GetRasterBand(1)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    srsLatLon = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srsLatLon,srs)
    for eachSlice in lattice:
        for eachPoint in eachSlice:
	    xyCoord = eachPoint[1]
            latlng = util.swap_pair(eachPoint[2])
	    if xyCoord_in_rightofway(xyCoord,directionsCoords):
		eachPoint.append(0)
	    else:
                xVal, yVal, zVal = ct.TransformPoint(latlng[1],latlng[0])
                x = int((xVal - gt[0])/gt[1])
                y = int((yVal - gt[3])/gt[5])
                structval = rb.ReadRaster(x,y,1,1,buf_type=gdal.GDT_Float32)
                intval = struct.unpack('f', structval)
                pixelVal = intval[0]
                eachPoint.append(pixelVal)
    return lattice

