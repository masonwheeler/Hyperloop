import math

import elevation
import proj
import util
import config

def get_pyloncoords(cellCenter, primVec, pylonSpacing):
    vecNorm = util.norm(primVec)
    unitVec = util.scale(1.0/vecNorm, primVec)     
    numPylonsInGridHalf = int((vecNorm / 2.0) / pylonSpacing)
    pylonIndices = range(-numPylonsInGridHalf,numPylonsInGridHalf + 1)
    basePylonXYCoords = [util.scale(pylonIndex*pylonSpacing,unitVec)
                         for pylonIndex in pylonIndices]
    pylonXYCoords = [util.add(basePylonXYCoord,cellCenter)
                     for basePylonXYCoord in basePylonXYCoords]
    #print(pylonXYCoords)
    pylonLonLatCoords = proj.xys_to_lonlats(pylonXYCoords, config.proj)
    pylonLatLngCoords = util.swap_pairs(pylonLonLatCoords)
    #print(pylonLonLatCoords)
    return pylonLatLngCoords

def get_pylonheights(cellCenter, primVec, pylonSpacing):
    pylonLatLngCoords = get_pyloncoords(cellCenter, primVec, pylonSpacing)
    print(len(pylonLatLngCoords))
    #print(pylonLatLngCoords)
    pylonHeights = util.operation_on_pieces(elevation.get_elevation,
                   config.getElevationPieceSize, pylonLatLngCoords)
    #print(pylonHeights)
    return pylonHeights

