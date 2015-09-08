"""
Original Developer: David Roberts
Purpose of Module: To generate the velocity profile of a route.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Removed unecessary lines and fixed formatting
"""

#Standard Modules
import math
import numpy as np
from scipy.interpolate import interp1d

#Our Modules
import util
import config

def vMaxPoints(xPoints):
    rPoints = [util.points_to_radius(xPoints[i-1:i+2]) for i in range(1,len(x)-1)]
    sPoints = [0 for i in range(0,len(xPoints))]
    for i in range(0, len(xPoints)-1):
        sPoints[i+1] = sPoints[i] + np.linalg.norm(xPoints[i+1] - xPoints[i])
    maxPoints = [0] + [min(np.sqrt(r*config.lateralAccelTol), config.maxSpeed) for r in rPoints] + [0]
    return [sPoints, maxPoints]

def reversesort_elevationindices(elevations):
    elevationsIndices = range(len(elevations))
    sortedIndices = sorted(elevationsIndices,
                            key = lambda i: elevations[i], reverse=True)
    return sortedIndices


#Note: get_relevant_indices() crashes if either start OR end are the highest points on the route!!!
def get_relevant_indices(elevations, pylonSpacing):
    tallest = reversesort_elevationindices(elevations)    
    relevantIndices = [0, len(elevations)- 1]  #[beginning of route, tallest location, end of route]

    def newLocationisGood(i):
      newLocation = util.placeIndexinList(tallest[i], relevantIndices) # append newcomer to list; try it on for size
      backwardCurvature = curvature(relevantIndices[newLocation-1], relevantIndices[newLocation], elevations)
      forwardCurvature = curvature(relevantIndices[newLocation], relevantIndices[newLocation+1], elevations)
      relevantIndices.pop(newLocation) # return list back to normal
      
      curvatureTolerance = config.gTolerance * config.maxSpeed**2
      if max(backwardCurvature, forwardCurvature) < curvatureTolerance:  # Let's see; how did we do?
        return True
      else:
        return False

    i = 0
    while (newLocationisGood(i) and len(relevantIndices) < len(elevations)):  
    #we will continue to zero-out pylons while it is safe to do so. 
      util.placeIndexinList(tallest[i], relevantIndices)
      i += 1
    
    return relevantIndices



def xPointstovPoints(xPoints):
    sPoints = [0 for i in range(0,len(xPoints))]
    for i in range(0, len(xPoints)-1):
        sPoints[i+1] = sPoints[i] + np.linalg.norm(xPoints[i+1] - xPoints[i])

    vPoints = [0, 200, 300] + \
              [util.list_mean([min(math.sqrt(9.81*.3*util.pointstoRadius(xPoints[j:j+3])),330)
               for j in range(i-2,i+3)]) for i in range(3,len(xPoints)-4)] + \
              [320, 300, 200, 0]
    return [sPoints, vPoints]

def vPointstovFunc(sPoints,vPoints):
  return interp1d(sPoints, vPoints, kind='cubic')


