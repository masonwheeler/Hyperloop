import math

import elevation
import proj
import util
import config

"""
def dxdtheta(phi_theta):
    return math.fabs(config.radiusOfEarth * math.cos(2 * math.pi * phi_tht[0] / 360)) * 2 * math.pi / 360

def dydphi(phi_theta):
    return R * 2 * math.pi / 360

def getHeights(cellCenter, primVec, pylonSpacing):
    normalization=norm([primVec[0] * dydphi(cellCenter), primVec[1] * dxdtht(cellCenter)])
    pylonSpacingInDegrees = pylonSpacing * norm(primVec) / normalization
    numPylons = int(norm(primVec) /pylonSpacingDegree)
    pylonsRange = range(int(-math.floor(numPylons/2)), int(math.floor(numPylons/2))+1)
    pylonLocations = [add(cellCenter, scale(k * pylonSpacingInDegrees /norm(primVec),primVec)) for k in pylonsRange]
    pylonCoordinates = [(location[1], location[0]) for location in pylonLocations]
    result = util.operationOnPieces(getElevation.getElevation,config.getElevationPieceSize,pylonCoordinates)
    return result
"""

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
    #print(pylonLatLngCoords)
    pylonHeights = util.operation_on_pieces(elevation.get_elevation,
                   config.getElevationPieceSize, pylonLatLngCoords)
    print(pylonHeights)
    return pylonHeights

