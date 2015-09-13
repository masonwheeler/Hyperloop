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
import geotiff
import parameters
import util


def cost_density_to_local_cost(cost_density):
    """Takes the cost per unit area and outputs the land acquisition cost
    """
    length = config.LAND_POINT_SPACING
    width = 2.0 * parameters.LAND_PADDING
    area = length * width
    local_cost = cost_density * area * 10
    return local_cost

def get_landcover_pixel_values(landcover_latlngs):
    """Fetches the cost per unit area at each input lat lng point
    """
    geotiff_file_path = config.CWD + config.GEOTIFF_FILE_PATH
    landcover_lnglats = util.swap_pairs(landcover_latlngs)
    landcover_pixel_values = geotiff.get_geotiff_pixel_vals_with_projection(
                                        geotiff_file_path, landcover_lnglats)
    return landcover_pixel_values

def pixel_values_to_cost_densities(landcover_pixel_values):
    """Maps the land cover pixel values to the corresponding costs
    """
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


def get_land_cost(landcover_latlngs):
    """Computes the total land acquisition cost for a list of lat lng points
    """
    landcover_pixel_values = get_landcover_pixel_values(landcover_latlngs)
    landcover_cost_densities = pixel_values_to_cost_densities(
                                                   landcover_pixel_values)
    land_cost = cost_densities_to_landcost(landcover_cost_densities)
    return land_cost
