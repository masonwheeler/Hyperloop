from osgeo import gdal
from osgeo import osr
import struct

import config
import util
import geotiff

def normalize_cost(cost):
    area = config.landPointSpacing * (2.0 * config.landPadding)
    normalizedCost = cost * (area / 100.0)
    return normalizedCost

def land_cost(landPointsLonLatCoords):
    ds = gdal.Open(config.geotiffFilePath)
    gt = ds.GetGeoTransform()
    rb = ds.GetRasterBand(1)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    srsLatLon = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srsLatLon,srs)
    
    landCost = 0
    for lonlatCoord in landPointsLonLatCoords:
        pointPixelVal = geotiff.pixel_val(ct, gt, rb, lonlatCoord)
        pointCost = config.costTable[str(pointPixelVal)]
        landCost += normalize_cost(pointCost)
    return landCost
    
    
        
        
        
                
