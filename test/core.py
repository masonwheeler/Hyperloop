import config
import database
import genBounds
import genLattice
import genRoutes

def pairAnalysis(start,end):
    bounds = genBounds.genBoundingPolygon(start,end)
    startLatLng,endLatLng = genBounds.get_startEndLatLng()
    return 0
