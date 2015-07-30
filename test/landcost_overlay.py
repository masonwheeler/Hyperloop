#Standard Modules:
from osgeo import gdal
from osgeo import osr

#Our Modules:
import config
import util
import geotiff
import landcover
import lattice
import cacher

dense_lattice = lattice.build_dense_lattice()
denselattice_list = [point for Slice in dense_lattice for point in Slice]
land_cost_densities = landcover.landcover_costDensities(denselattice_list)
exportfile = [((denselattice_list[i].latlngCoords)[0],(denselattice_list[i].latlngCoords)[1], \
	             land_cost_densities[i]) for i in range(len(land_cost_densities))]

cacher.save_listlike(exportfile,costDensityOverlay)