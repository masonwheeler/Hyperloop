"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the land acquisition cost associated with
                   building the Hyperloop route along a given edge.
Last Modified: 7/17/15
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

def edge_land_cost(landcostGrid):
    geotiffFilePath = config.cwd + config.geotiffFilePath
    fileHandle = gdal.Open(geotiffFilePath)
    geoTransform = fileHandle.GetGeoTransform()
    rasterBand = fileHandle.GetRasterBand(1)
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromWkt(fileHandle.GetProjection())
    spatialReferenceLatLon = spatialReference.CloneGeogCS()
    coordTrans = osr.CoordinateTransformation(spatialReferenceLatLon,
                                              spatialReference)    
    edgeLandCost = 0
    for landcostLatLng in landcostGrid:
        latlngPixelVal = geotiff.pixel_val(coordTrans, geoTransform,
                         rasterBand, util.swap_pair(landcostLatLng))
        latlngLandCost = config.costTable[latlngPixelVal]
        edgeLandCost += latlngLandCost #normalize_cost(pointCost)
    return edgeLandCost
    
    
        
        
        
                
