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

def cost(costDensity):
    length = config.landPointSpacing 
    width = 2.0 * config.landPadding
    area = length * width
    return costDensity * area

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
        latlng_costDensity = config.costTable[latlngPixelVal]
        edgeLandCost += cost(latlng_costDensity)
    return edgeLandCost
    
    
        
        
        
                
