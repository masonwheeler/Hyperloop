"""
Original Developer: Jonathan Ward
Purpose Of Module: To determine the land acquisition cost for an edge.
Last Modified: 7/16/16
Last Modified By: Jonathan Ward
Last Modification Purpose: The right of way flag is now stored in each Edge and
                           is thus not needed here.                        
"""

from osgeo import gdal
from osgeo import osr
import struct

import config
import util
import proj
import util


def land_cost(ct, gt, rb, xyCoord, lonlatCoord, directionsCoords):
	  return pixel_val(ct,gt,rb,lonlatCoord)
"""
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
            latlngCoords = eachPoint.latlngCoords
            landCost = land_cost(ct,gt,rb,xyCoords,lonlatCoords,directionsCoords)
            pylonCost = pyloncost.pylon_cost(xyCoords, primVec,
            config.pylonSpacing, config.maxSpeed, config.gTolerance,
            config.costPerPylonLength, config.pylonBaseCost)
            eachPoint.append(landCost)
    return lattice
"""
