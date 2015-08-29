# Standard Modules:
from osgeo import gdal
from osgeo import osr
import os

# Our Modules:
import config
import util
import geotiff
import landcover
import lattice
import cacher
import core

config.use_cached_lattice = False
config.point_spacing = 30
config.spline_sample_spacing = 3
config.cwd = os.getcwd()
config.lattice_flag = False

start = "Los_Angeles"
end = "San_Francisco"
#start = "Dallas"
#end = "Austin"
#start = "Portland"
#end = "San_Francisco"
#start = "New_York"
#end = "Boston"

directions_points = core.build_directions(start, end)
dense_lattice = core.build_lattice(directions_points)
denselattice_list = [point["latlng_coords"]
                     for Slice in dense_lattice for point in Slice]
land_cost_densities = landcover.landcover_cost_densities(denselattice_list)
exportfile = [(denselattice_list[i][0], denselattice_list[i][1],
               land_cost_densities[i]) for i in range(len(land_cost_densities))]
save_name = "_".join([start, end, "cost_density"])
cacher.save_listlike(exportfile, save_name)
