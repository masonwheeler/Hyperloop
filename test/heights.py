import getElevation
import util

import math

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

def get_heights(cellCenter, xPrimVec, yPrimVec,
