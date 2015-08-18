"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the land acquisition cost associated with
                   building the Hyperloop route along a given edge.
Last Modified: 8/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: fixed function naming
"""

#Standard Modules:
from osgeo import gdal
from osgeo import osr

#Our Modules:
import config
import util
import geotiff

def cost_density_to_local_cost(costDensity):
    length = config.landPointSpacing 
    width = 2.0 * config.landPadding
    area = length * width
    localCost = costDensity * area
    return localCost

def landcover_cost_densities(landcoverLatLngs):
    geotiffFilePath = config.cwd + config.geotiffFilePath
    fileHandle = gdal.Open(geotiffFilePath)
    geoTransform = fileHandle.GetGeoTransform()
    rasterBand = fileHandle.GetRasterBand(1)
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromWkt(fileHandle.GetProjection())
    spatialReferenceLatLon = spatialReference.CloneGeogCS()
    coordTrans = osr.CoordinateTransformation(spatialReferenceLatLon,
                                              spatialReference)    
    landcoverPixelValues = [geotiff.pixel_val(coordTrans, geoTransform,
                            rasterBand, util.swap_pair(landcoverLatLng))
                            for landcoverLatLng in landcoverLatLngs]
    landcoverCostDensities = [config.costTable[pixelVal] for pixelVal
                            in landcoverPixelValues]
    return landcoverCostDensities
        
def cost_densities_to_landcost(landcoverCostDensities):
    landcoverCosts = map(cost_density_to_local_cost, landcoverCostDensities)
    landCost = sum(landcoverCosts)
    return landCost

def get_land_cost(landcoverLatLngs):
    landCoverCostDensities = landcover_cost_densities(landcoverLatLngs)
    landCost = cost_densities_to_landcost(landCoverCostDensities)
    return landCost
                
