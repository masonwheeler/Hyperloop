"""
Original Developer: David Roberts
Purpose of Module: To generate a route from a graph.
Last Modified: 7/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To make compatible with graph modifications.
"""

import advanced_interpolate as interp
from scipy.interpolate import PchipInterpolator
import match_landscape as landscape
import comfort as cmft
import util
import visualize

class Route:
  #def __init__(self, tube, velocityProfileGraph):
    
  def as_dict(self):
    routeDict = {
                  "latlngs" : self.latlngs,
                  "landCost" : self.landCost,
                  "tubeCoords" : self.tubeElevations,
                  "pylons" : self.pylons,
                  "tubeCost" : self.tubeCost,
                  "pylonCost" : self.pylonCost,
                  "velocityProfile" : self.velocityProfile,
                  "accelerationProfile" : self.accelerationProfile,
                  "comfortRating" : self.comfortRating,
                  "tripTime" : self.tripTime
                }


def graphtotwoDroute(graph):
  x = graph.geospatials
  return interp.paraSuperQ(x, 25)

def twoDroutetothreeDroute(x):
  s, z = landscape.genLandscape(x, "elevation")
  sInterp, zInterp = landscape.matchLandscape(s, z, "elevation")
  f = PchipInterpolator(sInterp, zInterp)
  z = f(s)

  #for testing only:
  visualize.scatter_plot(s, z)
  
  x, y = np.transpose(x)
  return np.transpose([x, y, z])


def threeDroutetofourDroute(x):
  s, v = landscape.genLandscape(x, "velocity")
  sInterp, vInterp = landscape.matchLandscape(s, v, "velocity")
  f = PchipInterpolator(sInterp, vInterp)
  v = f(s)
  t = [0] * len(v)
  t[1] = (s[1] - s[0]) / gen.mean(v[0:2])
  for i in range(2, len(v)):
    t[i] = t[i-1] + (s[i] - s[i-1]) / v[i-1]
  t[-1] = (s[-1] - s[-2]) / util.mean(v[-2:len(v)])

  x, y, z = np.transpose(x)
  return np.transpose([x, y, z, t])


def comfortanalysisOffourDroute(x):
  x, y, z, t = np.transpose(x)
  vx, vy, vz, t = [util.numericalDerivative(x, t), util.numericalDerivative(y, t), util.numericalDerivative(z, t), t]
  ax, ay, az, t = [util.numericalDerivative(vx, t), util.numericalDerivative(vy, t), util.numericalDerivative(vz, t), t]
    
  #breakUp data into chunks for comfort evaluation:
  vxChunks, vyChunks, vzChunks = [util.breakUp(vx, 500), util.breakUp(vy, 500), util.breakUp(vz, 500)]
  axChunks, ayChunks, azChunks = [util.breakUp(ax, 500), util.breakUp(ay, 500), util.breakUp(az, 500)]

  vChunks = np.transpose([vxChunks, vyChunks, vzChunks])
  aChunks = np.transpose([axChunks, ayChunks, azChunks])
  tChunks = util.breakUp(t, 500)
  mu = 1
  comfort = [cmft.comfort(vChunks[i], aChunks[i], tChunks[i][-1]-tChunks[i][0], mu) for i in range(len(tChunks))]
  return [comfort, t, x, y, z, vx, vy, vz, ax, ay, az]



