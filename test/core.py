import config
import database
import boundingpolygon
import lattice
import routes
import time

def pair_analysis(start,end):
    bounds,startLatLng,endLatLng = boundingpolygon.bounding_polygon(start,end)
    boundsXY,startXY,endXY = lattice.project_bounds(bounds,startLatLng,endLatLng)
    lattice.set_params(startXY,endXY)
    transformedBounds = lattice.transform_bounds(boundsXY,startXY,endXY)
    baseLattice, angles = lattice.base_lattice(transformedBounds)
    latticeWithLngLats = lattice.attach_lnglats(baseLattice)
    #latticeWithCost = lattice.attach_cost(config.geotiffFilePath,
    #	latticeWithLngLats,config.coordinatesList)
    #routes.
    return 0
