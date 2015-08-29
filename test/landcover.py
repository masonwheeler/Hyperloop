"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the land acquisition cost associated with
                   building the Hyperloop route along a given edge.
Last Modified: 8/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: fixed function naming
"""

# Standard Modules:
from osgeo import gdal
from osgeo import osr

# Our Modules:
import config
import util
import geotiff


def cost_density_to_local_cost(cost_density):
    """Takes the cost per unit area and outputs the land acquisition cost
    """
    length = config.LAND_POINT_SPACING
    width = 2.0 * config.LAND_PADDING
    area = length * width
    local_cost = cost_density * area * 10
    return local_cost


def get_landcover_cost_densities(landcover_lat_lngs):
    """Fetches the cost per unit area at each input lat lng point
    """
    geotiff_file_path = config.CWD + config.GEOTIFF_FILE_PATH
    file_handle = gdal.Open(geotiff_file_path)
    geo_transform = file_handle.GetGeoTransform()
    raster_band = file_handle.GetRasterBand(1)
    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromWkt(file_handle.GetProjection())
    spatial_reference_lat_lon = spatial_reference.CloneGeogCS()
    coord_trans = osr.CoordinateTransformation(spatial_reference_lat_lon,
                                               spatial_reference)
    landcover_pixel_values = [geotiff.get_pixel_val(coord_trans,
                                                    geo_transform,
                                                    raster_band,
                                                    util.swap_pair(
                                                    landcover_lat_lng))
                              for landcover_lat_lng in landcover_lat_lngs]
    landcover_cost_densities = [config.COST_TABLE[pixel_val] for pixel_val
                                in landcover_pixel_values]
    return landcover_cost_densities


def cost_densities_to_landcost(landcover_cost_densities):
    """Computes the total land acquisition cost from a list of cost densities
    """
    landcover_costs = [cost_density_to_local_cost(cost_density)
                       for cost_density in landcover_cost_densities]
    land_cost = sum(landcover_costs)
    return land_cost


def get_land_cost(landcover_lat_lngs):
    """Computes the total land acquisition cost for a list of lat lng points
    """
    land_cover_cost_densities = get_landcover_cost_densities(landcover_lat_lngs)
    land_cost = cost_densities_to_landcost(land_cover_cost_densities)
    return land_cost
