"""
Original Developer: Jonathan Ward
Purpose of Module: To convert graphs into paths.
Last Modified: 7/26/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module.
"""

#Standard Modules
import scipy.interpolate

#Our Modules:
import proj
import elevation
import landcover
import tube

class Path:
    tube = []
    curvature = []
    maxVelocitiesByArcLength = [] #v_max(s)
    pylons = []
    landCost = 0
    pylonCost = 0
    tubeCost = 0   
  
    def __init__(self, graph):
        graphGeospatials = sample_geospatials(graph.geospatials)
        graphSpline = build_geospatials_spline(sampledGeospatials)
        pathGeospatials = evaluate_graphspline(graphSpline)
        pathLatLngs = proj.geospatials_to_latlngs(pathGeospatials, config.proj)
        pathElevations = elevation.usgs_elevation(pathLatLngs)       
        pathPylons, tube = pylons.build_pylons(pathElevations)    
        pylonCost = pylons.pylon_cost(pathPylons)
        landCost = landcover.land_cost(pathLatLngs)
        tubeCost = tube.tubeCost(tube)
        
        
        
        
        



def pchip_interpolate(graphXVals, graphYVals):
    
    
