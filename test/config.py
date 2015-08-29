"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a namespace for global configuration variables.
Last Modified: 7/23/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Changed from routes to graphs
"""


########## Parameters And Switches ##########

"""
Modes and settings.
"""
testing_mode = True
visual_mode = True
verbose_mode = True
timing_mode = False
use_dropbox = False

"""
Cache Overwriting Switches.
"""
use_cached_directions = False
use_cached_spline = False
use_cached_lattice = False
use_cached_edges = True
use_cached_graphs = True
use_cached_spatial_paths2d = False

"""
Lattice Generation Parameters
"""
point_spacing = 2000.0  # (in meters) spacing between points in the same slice
directions_sample_spacing = 10  # (in meters)
degree_constraint = 30  # the angular constraint between subsequent edges
# (in units of directions_sample_spacing) i.e.
spatial_slice_s_value_step_size = 1000
# spacing between spline points in meters is given
# by directions_sample_spacing * spline_sample_spacing
ndigits = 6  # the number of digits used for rounding

"""
Graph Generation Parameters
"""
graph_curvature_min_num_edges = 3
graph_sample_spacing = 1000.0
num_fronts = 4

"""
Tube Generation Parameters
"""

tube_trip_time_excess_min_num_edges = 3
pylon_height_step_size = 10.0
tube_degree_constraint = 60.0

"""
Velocity Profile Generation Parameters
"""
velocity_profile_degree_constraint = 30.0
velocity_arc_length_step_size = 100.0

"""
Engineering constraints.
"""
pylon_spacing = 100.0  # maximum distance between subsequent pylons (in meters)
max_speed = 330.0  # maximum speed of the capsule (in m/s)


"""
Land Cost parameters
"""
land_point_spacing = 30.0  # spacing between points for land cost sampling in meters

"""
Comfort parameters.
"""
linear_accel_constraint = 0.5 * 9.81
lateral_accel_constraint = 0.3 * 9.81
vertical_accel_constraint = 0.3 * 9.81

linear_accel_tol = 0.5 * 9.81
lateral_accel_tol = 0.3 * 9.81
jerk_tol = 2
curvature_threshhold = (lateral_accel_tol / max_speed**2)

"""
Legal Parameters
"""

land_padding = 30

"""
Financial Parameters, all costs in dollars.
"""

right_of_way_land_cost = 0.0
pylon_cost_per_meter = 10000.0
tunneling_cost_per_meter = 10000.0  # USD/m
pylon_base_cost = 2000.0
tube_cost_per_meter = 1000.0
padding = 20  # padding (in meters)


# See (http://www.mrlc.gov/nlcd11_leg.php) for the pixel legend source.
# Note the omission of Alaska only values (please enter values in USD/
# meter^2.)
cost_table = {11: 300,  # Open Water (Source: http://www.dot.state.fl.us/planning/policy/costs/Bridges.pdf)
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
directions_bools = [use_cached_directions]
spline_bools = directions_bools + [use_cached_spline]
lattice_bools = spline_bools + [use_cached_lattice]
edges_bools = lattice_bools + [use_cached_edges]
graphs_bools = edges_bools + [use_cached_graphs]
spatial_paths2d_bools = graphs_bools + [use_cached_spatial_paths2d]

"""
Overwriting Flags.
"""
directions_flag = all(directions_bools)
spline_flag = all(spline_bools)
lattice_flag = all(lattice_bools)
edges_flag = all(edges_bools)
graphs_flag = all(graphs_bools)
spatial_paths2d_flag = all(spatial_paths2d_bools)

"""
Uninitialized Directory Paths.
"""
cache_directory = ""
save_directory = ""
working_cache_name = ""
working_save_dir_name = ""
working_cache_directory = ""
working_save_directory = ""
working_graphs_directory = ""

"""
Unitialized Global variables.
"""

holder = 0
proj = 0
directions_coords = 0
plot_queue = []


########## API-Specific and System-Specific Settings ##########

"""
For File Saving.
"""
cwd = ""
dropbox_directory = "/home/ubuntu/Dropbox/save"

"""
For USGS-Elevation.
"""

usgs_ftp_path = "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Elevation/13/IMG/"
usgs_folder = "/usgs/"

"""
For NLCD (National Landcover Dataset).
"""

geotiff_file_path = "/nlcd/us.tif"

"""
For Google-Elevation
"""

# Constraint on number of simultaneous api calls.
get_elevation_piece_size = 512
elevation_base_url = 'https://maps.googleapis.com/maps/api/elevation/json'
