import config
import database
import boundingpolygon
import lattice
import routes
import time

def pair_analysis(start,end):
    t0 = time.time()
    bounds,startLatLng,endLatLng = boundingpolygon.bounding_polygon(start,end)
    boundsXY,startXY,endXY = lattice.project_bounds(bounds,startLatLng,endLatLng)
    lattice.set_params(startXY,endXY)
    transformedBounds = lattice.transform_bounds(boundsXY,startXY,endXY)
    baseLattice, angles, config.latticeYSpacing = lattice.base_lattice(
                                                    transformedBounds)
    latticeWithLngLats,xPrimVec,yPrimVec = lattice.attach_lnglats(baseLattice)
    latticeWithCost = lattice.attach_cost(config.geotiffFilePath,
    	latticeWithLngLats,config.coordinatesList,xPrimVec)
    t1 = time.time()
    print("Analysis of a single pair took " + str(t1-t0) + " seconds.")
    return 0
