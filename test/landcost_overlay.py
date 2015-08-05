#Standard Modules:
from osgeo import gdal
from osgeo import osr
import os

#Our Modules:
import config
import util
import geotiff
import landcover
import lattice
import cacher
import core

config.useCachedLattice = False
config.pointSpacing = 30
config.splineSampleSpacing = 3
config.cwd = os.getcwd()
config.latticeFlag = False

start = "Los_Angeles"
end = "San_Francisco"
#start = "Dallas"
#end = "Austin"
#start = "Portland"
#end = "San_Francisco"
#start = "New_York"
#end = "Boston"

directionsPoints = core.build_directions(start, end)
dense_lattice = core.build_lattice(directionsPoints)
denselattice_list = [point["latlngCoords"] for Slice in dense_lattice for point in Slice]
land_cost_densities = landcover.landcover_costDensities(denselattice_list)
exportfile = [(denselattice_list[i][0],denselattice_list[i][1], \
               land_cost_densities[i]) for i in range(len(land_cost_densities))]
saveName = "_".join([start, end, "costDensity"])
cacher.save_listlike(exportfile, saveName)
