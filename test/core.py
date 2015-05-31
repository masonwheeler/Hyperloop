import config
import database
import genBounds
import genLattice
import genRoutes

def pairAnalysis(start,end):
    bounds,startLatLng,endLatLng = genBounds.genBoundingPolygon(start,end)
    boundsXY,startXY,endXY = genLattice.projectBounds(bounds,startLatLng,endLatLng)
    genLattice.set_params(startXY,endXY)
    transformedBounds = genLattice.transformBounds(boundsXY,startXY,endXY)
    baseLattice = genLattice.gen_baseLattice(transformedBounds)
    latticeWithLngLats = genLattice.attach_lngLat(baseLattice)
    return 0
