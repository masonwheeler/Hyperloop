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


config.pointSpacing = 30
config.splineSampleSpacing = 3
config.cwd = os.getcwd()

start = "Los_Angeles"
end = "San_Francisco"

directionsPoints = core.build_directions(start, end)
dense_lattice = core.build_lattice(directionsPoints)
denselattice_list = [point for Slice in dense_lattice for point in Slice]
land_cost_densities = landcover.landcover_costDensities(denselattice_list)
exportfile = [((denselattice_list[i].latlngCoords)[0],(denselattice_list[i].latlngCoords)[1], \
               land_cost_densities[i]) for i in range(len(land_cost_densities))]

cacher.save_listlike(exportfile,"costDensityOverlay")
