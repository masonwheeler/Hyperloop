"""
Original Developer: David Roberts
Purpose of Module: To generate a route from a graph.
Last Modified: 8/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add classes providing useful structure.
"""

#Standard Modules:
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import PchipInterpolator

#Our Modules
import advanced_interpolate as interp
import comfort as cmft
import config
import elevation
import landcover
import match_landscape as landscape
import proj
import util
import visualize


class SpatialPath2d:
    def sample_geospatials(self, graphGeospatials, geospatialSampleDistance):
        sampledGeospatials = interpolate.sample_path(graphGeospatials,
                                             geospatialSampleDistance)
        return sampledGeospatials
        
    def get_interpolating_geospatials(self, sampledGeospatials):
        xArray, yArray = points_2d_to_arrays(sampledGeospatials)
        numPoints = len(sampledGeospatials)
        sValues = interpolate.get_s_values(numPoints)
        xSpline, ySpline = interpolate.interpolating_splines_2d(xArray, yArray,
                                                                       sValues)
        xValues = interpolate.get_spline_values(xSpline, sValues)
        yValues = interpolate.get_spline_values(ySpline, sValues)
        interpolatingGeospatials = [xValues, yValues]
        return interpolatingGeospatials

    def get_interpolating_latlngs(self, interpolatingGeospatials):
        interpolatingLatLngs = proj.geospatials_to_latlngs(
                         interpolatingGeospatials, config.proj)
        return interpolatingLatLngs

    def compute_land_cost(self, interpolatingLatLngs):
        landCost = landcover.get_land_cost(interpolatingLatLngs)
        return landCost

    def get_elevation_profile(self, interpolatedLatLngs):
        elevationProfile = elevation.get_elevation_profile(interpolatedLatLngs)
        return elevationProfile
    
    def get_interpolating_geospatials_v2(self, geospatials):
        interpolatingGeospatialsArray = interp.paraSuperQ(geospatials, 25)
        interpolatingGeospatials = interpolatingGeospatialsArray.tolist()
        arcLengths = util.compute_arc_lengths(interpolatingGeospatials)
        return [interpolatingGeospatials, arcLengths]

    def get_tube_graphs_v2(self, elevationProfile):                     
        geospatials = [elevationPoint["geospatial"] for elevationPoint
                                                    in elevationProfile]
        landElevations = [elevationPoint["landElevation"] for elevationPoint
                                                         in elevationProfile]
        arcLengths = [elevationPoint["distanceAlongPath"] for elevationPoint
                                                         in elevationProfile]
        sInterp, zInterp = landscape.matchLandscape(arcLengths,
                                   landElevations, "elevation")
        tubeSpline = PchipInterpolator(sInterp, zInterp)
        tubeElevations = tubeSpline(arcLengths)
        #  plt.plot(arcLengths, tubeElevations, 'b.',
        #            arcLengths, landElevations, 'r.')
        #  plt.show()  
        spatialXValues, spatialYValues = zip(*geospatials)
        tubeGraph = zip(spatialXValues, spatialYValues, tubeElevations)
        tubeGraphs = [tubeGraph]
        return tubeGraphs
    
    def __init__(self, spatialGraph):
        graphGeospatials = spatialGraph.geospatials
        #sampledGeospatials = self.sample_geospatials(graphGeospatials)
        #interpolatingGeospatials = self.get_interpolating_geospatials(
        #                                               sampledGeospatials)
        interpolatingGeospatials, arcLengths = \
          self.get_interpolating_geospatials_v2(graphGeospatials)
        interpolatingLatLngs = self.get_interpolating_latlngs(
                                           interpolatingGeospatials)
        self.elevationProfile = elevation.get_elevation_profile(
                            interpolatingGeospatials, arcLengths)
        self.landCost = self.compute_land_cost(interpolatingLatLngs)
        self.tubeGraphs = self.get_tube_graphs_v2(self.elevationProfile)


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


def graph_to_2Droute(graph):
  x = graph.geospatials
  return interp.paraSuperQ(x, 25)

def _2Droute_to_3Droute(x):
  s, zland = landscape.genLandscape(x, "elevation")
  sInterp, zInterp = landscape.matchLandscape(s, zland, "elevation")
  f = PchipInterpolator(sInterp, zInterp)
  z = f(s)

  #for testing only:
#  plt.plot(s, z, 'b.', s, zland, 'r.')
#  plt.show()

  
  x, y = np.transpose(x)
  return np.transpose([x, y, z])


def _3Droute_to_4Droute(x):
  s, vland = landscape.genLandscape(x, "velocity")
  sInterp, vInterp = landscape.matchLandscape(s, vland, "velocity")
  f = PchipInterpolator(sInterp, vInterp)
  v = f(s)


# for testing only:
#  plt.plot(s, v, 'b.', s, vland, 'r.')
#  plt.show()

  t = [0] * len(v)
  t[1] = (s[1] - s[0]) / util.mean(v[0:2])
  for i in range(2, len(v)):
    t[i] = t[i-1] + (s[i] - s[i-1]) / v[i-1]
  t[-1] = (s[-1] - s[-2]) / util.mean(v[-2:len(v)])

  x, y, z = np.transpose(x)
  return np.transpose([x, y, z, t])


def comfortanalysis_Of_4Droute(x):
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



