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

#######################################
#For NLCD (National Landcover Dataset)#
#######################################

LAND_COVER_GEOTIFF_FILE_PATH = "/nlcd/us.tif"

################
#Land Cost Data#
################

LAND_POINT_SPACING = 30.0  # spacing for land cost sampling (in meters)
LAND_PADDING = 30.0 #Meters
RIGHT_OF_WAY_LAND_COST = 0.0 #Dollars

# See (http://www.mrlc.gov/nlcd11_leg.php) for the pixel legend source.
# Note the omission of Alaska only values (please enter values in USD/
# meter^2.)
# Open Water Cost: http://www.dot.state.fl.us/planning/policy/costs/Bridges.pdf
COST_TABLE = {11: 300,  # Open Water
              12: 4,  # Perennial Ice/Snow
              21: 10,  # Developed, Open Space
              22: 20,  # Developed, Low Intensity
              23: 50,  # Developed, Medium Intensity
              24: 120,  # Developed, High Intensity
              31: 4,  # Barren Land
              41: 4,  # Deciduous Forest
              42: 4,  # Evergreen Forest
              43: 4,  # Mixed Forest
              52: 4,  # Shrub/Scrub
              71: 4,  # Grassland/Herbaceous
              81: 2,  # Pasture/Hay
              82: 2,  # Cultivated Crops
              90: 4,  # Woody Wetlands
              95: 4}  # Emergent Herbaceous Wetlands


def cost_density_to_local_cost(cost_density):
    """Takes the cost per unit area and outputs the land acquisition cost
    """
    length = LAND_POINT_SPACING
    width = 2.0 * LAND_PADDING
    area = length * width
    local_cost = cost_density * area * 10
    return local_cost

def get_landcover_pixel_values(landcover_latlngs):
    """Fetches the cost per unit area at each input lat lng point
    """
    geotiff_file_path = config.CWD + LAND_COVER_GEOTIFF_FILE_PATH
    landcover_lnglats = util.swap_pairs(landcover_latlngs)
    landcover_pixel_values = geotiff.get_geotiff_pixel_vals_with_projection(
                                        geotiff_file_path, landcover_lnglats)
    return landcover_pixel_values

def pixel_values_to_cost_densities(landcover_pixel_values):
    """Maps the land cover pixel values to the corresponding costs
    """
    landcover_cost_densities = [COST_TABLE[pixel_val] for pixel_val
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
