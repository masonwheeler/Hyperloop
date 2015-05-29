import config
import database
import genBounds
import genLattice
import genRoutes

def pairAnalysis(start,end):
    bounds,startLatLng,endLatLng = genBounds.genBoundingPolygon(start,end)
    genLattice.projectBounds(bounds,startLatLng,endLatLng)
    return 0
