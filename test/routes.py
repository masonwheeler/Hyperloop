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
import cacher
import comfort as cmft
import config
import elevation
import landcover
import match_landscape as landscape
import proj
import util
import visualize
import time


# The Route Class.
class Route:

  def __init__(self, comfort, t, x, y, z, vx, vy, vz, ax, ay, az):

        self.latlngs = self.compute_latlngs(x, y)
        self.landCost = landcover.get_land_cost(self.latlngs)
        self.tubeElevations = z
        self.pylons = self.compute_pylons(x, y, z)
        self.tubeCost = self.compute_tubeCost(x, y, z)
        self.pylonCost = sum([pylon["pylonCost"] for pylon in self.pylons])
        self.velocityProfile = self.compute_velocityProfile(vx, vy, vz)
        self.accelerationProfile = self.compute_accelerationProfile(ax, ay, az)
        self.tripTime = t[-1]
        tChunks = util.breakUp(t, 500)
        tComfort = [tChunks[i][-1] for i in range(len(tChunks))]
        self.comfortRating = util.LpNorm(tComfort, comfort, 2)


  def compute_latlngs(self, x, y):
    geospatials = np.transpose([x, y])
    return proj.geospatials_to_latlngs(geospatials, config.proj)
    
  def compute_pylons(self, x, y, z):
    geospatials = np.transpose([x, y])
    s, zland = landscape.genLandscape(geospatials, "elevation")
 
    def pylonCost(pylonHeight):
      if pylonHeight > 0:
        return config.pylonBaseCost + pylonHeight * config.pylonCostPerMeter
      else: 
        return - pylonHeight * config.tunnelingCostPerMeter
    geospatials = [geospatial.tolist() for geospatial in geospatials]
    Pylons = [{"geospatial" : geospatials[i],
                "latlng" : proj.geospatial_to_latlng(geospatials[i], config.proj),
                "landElevation" : zland[i],
                "pylonHeight" : (z[i]-zland[i]),
                "pylonCost" : pylonCost(z[i]-zland[i])}
                for i in range(len(z))]     
    return Pylons

  def compute_tubeCost(self, x, y, z):
    geospatials = np.transpose([x, y, z])
    tubeLength = sum([np.linalg.norm(geospatials[i + 1]-geospatials[i]) for i in range(len(geospatials)-1)])
    return tubeLength * config.tubeCostPerMeter

  def compute_velocityProfile(self, vx, vy, vz):
    velocityVectors = np.transpose([vx, vy, vz])
    return [np.linalg.norm(velocityVector) for velocityVector in velocityVectors]

  def compute_accelerationProfile(self, ax, ay, az):
    accelerationVectors = np.transpose([ax, ay, az])
    return [np.linalg.norm(accelerationVector) for accelerationVector in accelerationVectors]

  def as_dict(self):    
    routeDict = {
                  "latlngs" : self.latlngs,
                  "landCost" : self.landCost,
                  "tubeCoords" : self.tubeElevations.tolist(),
                  "pylons" : self.pylons,
                  "tubeCost" : self.tubeCost,
                  "pylonCost" : self.pylonCost,
                  "velocityProfile" : self.velocityProfile,
                  "accelerationProfile" : self.accelerationProfile,
                  "comfortRating" : self.comfortRating,
                  "tripTime" : self.tripTime
                }
    return routeDict





#Ancillary Functions:

def graph_to_2Droute(graph, M):
  x = graph.geospatials
  return interp.paraSuperQ(x, M)

def graph_to_2Droutev2(graph, M):
  x = graph.geospatials
  return interp.scipyQ(x, M)

def _2Droute_to_3Droute(x):
  s, zland = landscape.genLandscape(x, "elevation")
  sInterp, zInterp = landscape.matchLandscape(s, zland, "elevation")
  f = PchipInterpolator(sInterp, zInterp)
  z = f(s)

  sPylons = np.arange(s[0], s[-1], 100)
  zPylons = f(sPylons)

  x, y = np.transpose(x)
  return np.transpose([x, y, z])


def _3Droute_to_4Droute(x):
  s, vland = landscape.genLandscape(x, "velocity")
  sInterp, vInterp = landscape.matchLandscape(s, vland, "velocity")
  f = PchipInterpolator(sInterp, vInterp)
  v = [max(10 ,f(sVal)) for sVal in s]

  t = [0] * len(v)
  t[1] = (s[1] - s[0]) / util.mean(v[0:2])
  for i in range(2, len(v)):
    t[i] = t[i-1] + (s[i] - s[i-1]) / v[i-1]
  t[-1] = t[-2] + (s[-1] - s[-2]) / util.mean(v[-2:len(v)])

  x, y, z = np.transpose(x)
  return np.transpose([x, y, z, t])


def comfortanalysis_Of_4Droute(x):
  x, y, z, t = np.transpose(x)
  vx, vy, vz, t = [util.numericalDerivative(x, t), util.numericalDerivative(y, t), util.numericalDerivative(z, t), t]
  ax, ay, az, t = [util.numericalDerivative(vx, t), util.numericalDerivative(vy, t), util.numericalDerivative(vz, t), t]
    
  #breakUp data into chunks for comfort evaluation:
  v = np.transpose([vx, vy, vz])
  a = np.transpose([ax, ay, az])
  vChunks = util.breakUp(v, 500)
  aChunks = util.breakUp(a, 500)
  tChunks = util.breakUp(t, 500)
  
  mu = 1
  comfort = [cmft.sperling_comfort_index(vChunks[i], aChunks[i], tChunks[i][-1]-tChunks[i][0], mu) for i in range(len(tChunks))]
  return [comfort, t, x, y, z, vx, vy, vz, ax, ay, az]


def graph_to_route(graph):
  start = time.time()
  print  "computing data for a new route..."
  x = graph.geospatials
  graphSpacing = np.linalg.norm([x[2][0]-x[1][0], x[2][1]-x[1][1]])
  M = int(graphSpacing/config.pylonSpacing)
  print M
  routeData = comfortanalysis_Of_4Droute(_3Droute_to_4Droute(_2Droute_to_3Droute(graph_to_2Droutev2(graph, 25))))
  print "attaching data to new route..."
  print "done: process took " +str(time.time()-start)+" seconds."
  return Route(*routeData)



# class SpatialPath2d:
#     def sample_geospatials(self, graphGeospatials, geospatialSampleDistance):
#         sampledGeospatials = interpolate.sample_path(graphGeospatials,
#                                              geospatialSampleDistance)
#         return sampledGeospatials
        
#     def get_interpolating_geospatials(self, sampledGeospatials):
#         xArray, yArray = points_2d_to_arrays(sampledGeospatials)
#         numPoints = len(sampledGeospatials)
#         sValues = interpolate.get_s_values(numPoints)
#         xSpline, ySpline = interpolate.interpolating_splines_2d(xArray, yArray,
#                                                                        sValues)
#         xValues = interpolate.get_spline_values(xSpline, sValues)
#         yValues = interpolate.get_spline_values(ySpline, sValues)
#         interpolatingGeospatials = [xValues, yValues]
#         return interpolatingGeospatials

#     def get_interpolating_geospatials_v2(self, geospatials):
#         interpolatingGeospatialsArray = interp.paraSuperQ(geospatials, 25)
#         interpolatingGeospatials = interpolatingGeospatialsArray.tolist()
#         arcLengths = util.compute_arc_lengths(interpolatingGeospatials)
#         return [interpolatingGeospatials, arcLengths]

#     def get_interpolating_latlngs(self, interpolatingGeospatials):
#         interpolatingLatLngs = proj.geospatials_to_latlngs(
#                          interpolatingGeospatials, config.proj)
#         return interpolatingLatLngs

#     #def get_tube_graphs(self, elevationProfile):
    
#     def get_tube_graphs_v2(self, elevationProfile):                     
#         geospatials = [elevationPoint["geospatial"] for elevationPoint
#                                                     in elevationProfile]
#         landElevations = [elevationPoint["landElevation"] for elevationPoint
#                                                          in elevationProfile]
#         arcLengths = [elevationPoint["distanceAlongPath"] for elevationPoint
#                                                          in elevationProfile]
#         sInterp, zInterp = landscape.matchLandscape(arcLengths,
#                                    landElevations, "elevation")
#         tubeSpline = PchipInterpolator(sInterp, zInterp)
#         tubeElevations = tubeSpline(arcLengths)
#         #  plt.plot(arcLengths, tubeElevations, 'b.',
#         #            arcLengths, landElevations, 'r.')
#         #  plt.show()  
#         spatialXValues, spatialYValues = zip(*geospatials)
#         tubeGraph = zip(spatialXValues, spatialYValues, tubeElevations)
#         tubeGraphs = [tubeGraph]
#         return tubeGraphs
    
#     def __init__(self, spatialGraph):
#         graphGeospatials = spatialGraph.geospatials
#         #sampledGeospatials = self.sample_geospatials(graphGeospatials)
#         #interpolatingGeospatials = self.get_interpolating_geospatials(
#         #                                               sampledGeospatials)
#         interpolatingGeospatials, arcLengths = \
#           self.get_interpolating_geospatials_v2(graphGeospatials)
#         interpolatingLatLngs = self.get_interpolating_latlngs(
#                                            interpolatingGeospatials)
#         self.elevationProfile = elevation.get_elevation_profile(
#                             interpolatingGeospatials, arcLengths)
#         self.landCost = landcover.get_land_cost(interpolatingLatLngs)
#         #self.tubeGraphs = self.get_tube_graphs_v2(self.elevationProfile)

# def build_spatial_paths_2d(completeSpatialGraphs):
#     spatialPaths2d = map(SpatialPath2d, completeSpatialGraphs)
#     return spatialPaths2d

# def get_spatial_paths_2d(completeSpatialGraphs):
#     spatialPaths2d = cacher.get_object("spatialpaths2d", build_spatial_paths_2d,
#                           [completeSpatialGraphs], cacher.save_spatial_paths_2d,
#                                                       config.spatialPaths2dFlag)
#     return spatialPaths2d




