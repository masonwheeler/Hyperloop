"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the land acquisition cost associated with
                   building the Hyperloop route along a given edge.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify module usage
"""

#Standard Modules:
from osgeo import gdal
from osgeo import osr

#Our Modules:
import config
import util
import geotiff

def normalize_cost(cost):
    area = config.landPointSpacing * (2.0 * config.landPadding)
    normalizedCost = cost * (area / 100.0)
    return normalizedCost

def land_cost(landPointsLonLatCoords):
    geotiffFilePath = config.cwd + config.geotiffPath
    fileHandle = gdal.Open()
    geoTransform = fileHandle.GetGeoTransform()
    rasterBand = fileHandle.GetRasterBand(1)
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromWkt(fileHandle.GetProjection())
    spatialReferenceLatLon = spatialReference.CloneGeogCS()
    coordTrans = osr.CoordinateTransformation(spatialReferenceLatLon,
                                              spatialReference)    
    landCost = 0
    for lonlatCoord in landPointsLonLatCoords:
        pointPixelVal = geotiff.pixel_val(ct, gt, rb, lonlatCoord)
        pointCost = config.costTable[str(pointPixelVal)]
        landCost += normalize_cost(pointCost)
    return landCost
    
    
        
        
        
                
