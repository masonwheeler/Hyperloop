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
VERBOSE_MODE = True
TIMING_MODE = False
USE_DROPBOX = False

"""
Cache Overwriting Switches.
"""
USE_CACHED_DIRECTIONS = True
USE_CACHED_SPATIAL_LATTICE = True
USE_CACHED_SPATIAL_EDGES = True
USE_CACHED_SPATIAL_GRAPHS = False
USE_CACHED_SPATIAL_PATHS_2D = False

"""
Lattice Generation Parameters
"""
DEGREE_CONSTRAINT = 30  # the angular constraint between subsequent edges
NDIGITS = 6  # the number of digits used for rounding

"""
Graph Generation Parameters
"""
GRAPH_FILTER_MIN_NUM_EDGES = 3
GRAPH_SAMPLE_SPACING = 1000.0
NUM_FRONTS = 4

"""
Tube Generation Parameters
"""

TUBE_TRIP_TIME_EXCESS_MIN_NUM_EDGES = 3
PYLON_HEIGHT_STEP_SIZE = 10.0
TUBE_DEGREE_CONSTRAINT = 60.0

"""
Velocity Profile Generation Parameters
"""
VELOCITY_PROFILE_DEGREE_CONSTRAINT = 30.0
VELOCITY_ARC_LENGTH_STEP_SIZE = 100.0

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
Overwriting Bools.
"""
DIRECTIONS_BOOLS = [USE_CACHED_DIRECTIONS]
SPATIAL_LATTICE_BOOLS = DIRECTIONS_BOOLS + [USE_CACHED_SPATIAL_LATTICE]
SPATIAL_EDGES_BOOLS = SPATIAL_LATTICE_BOOLS + [USE_CACHED_SPATIAL_EDGES]
SPATIAL_GRAPHS_BOOLS = SPATIAL_EDGES_BOOLS + [USE_CACHED_SPATIAL_GRAPHS]
SPATIAL_PATHS_2D_BOOLS = SPATIAL_GRAPHS_BOOLS + [USE_CACHED_SPATIAL_PATHS_2D]

"""
Overwriting Flags.
"""
DIRECTIONS_FLAG = all(DIRECTIONS_BOOLS)
SPATIAL_LATTICE_FLAG = all(SPATIAL_LATTICE_BOOLS)
SPATIAL_EDGES_FLAG = all(SPATIAL_EDGES_BOOLS)
SPATIAL_GRAPHS_FLAG = all(SPATIAL_GRAPHS_BOOLS)
SPATIAL_PATHS_2D_FLAG = all(SPATIAL_PATHS_2D_BOOLS)

"""
Uninitialized Directory Paths.
"""
CACHE_DIRECTORY = ""
SAVE_DIRECTORY = ""
WORKING_CACHE_NAME = ""
WORKING_SAVE_DIR_NAME = ""
WORKING_CACHE_DIRECTORY = ""
WORKING_SAVE_DIRECTORY = ""
WORKING_GRAPHS_DIRECTORY = ""

"""
Unitialized Global variables.
"""

HOLDER = 0
PROJ = 0
DIRECTIONS_COORDS = 0
PLOT_QUEUE = []


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

"""
For Google-Elevation
"""

# Constraint on number of simultaneous api calls.
GET_ELEVATION_PIECE_SIZE = 512
ELEVATION_BASE_URL = 'https://maps.googleapis.com/maps/api/elevation/json'
