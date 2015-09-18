"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a namespace for global configuration variables.
Last Modified: 7/23/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Changed from routes to graphs
"""

#pylint: disable=W0105

########## Parameters And Switches ##########

"""
Modes and settings.
"""
TESTING_MODE = True
VISUAL_MODE = False
CACHE_MODE = True
VERBOSE_MODE = True
TIMING_MODE = False
USE_DROPBOX = False

"""
Lattice Generation Parameters
"""
NDIGITS = 6  # the number of digits used for rounding

"""
Land Cost parameters
"""
LAND_POINT_SPACING = 30.0  # spacing for land cost sampling (in meters)

"""
Comfort parameters.
"""
JERK_TOL = 2

"""
Financial Parameters.
"""

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


########## For Internal Use ##########

"""
Unitialized Global variables.
"""

PROJ = 0

########## API-Specific and System-Specific Settings ##########

"""
For File Saving.
"""
CWD = ""
DROPBOX_DIRECTORY = "/home/ubuntu/Dropbox/save"

"""
For USGS-Elevation.
"""

USGS_FTP_PATH = "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Elevation/13/IMG/"
USGS_FOLDER = "/usgs/"

"""
For NLCD (National Landcover Dataset).
"""

GEOTIFF_FILE_PATH = "/nlcd/us.tif"

