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
  rPoints = [util.points_to_radius(xPoints[i-1:i+2]) for i in range(1,len(xPoints)-1)]
  sPoints = [0 for i in range(0,len(xPoints))]
  for i in range(0, len(xPoints)-1):
    sPoints[i+1] = sPoints[i] + np.linalg.norm(xPoints[i+1] - xPoints[i])
  maxPoints = [0] + [min(np.sqrt(r*config.lateralAccelTol), config.maxSpeed) for r in rPoints] + [0]
  return [sPoints, maxPoints]


def sort_vMaxindices(vMaxPoints):
  vMaxindices = range(len(vMaxPoints))
  sortedIndices = sorted(vMaxindices, key = lambda i: vMaxPoints[i],)
  return sortedIndices


#Note: get_relevant_indices() crashes if either start OR end are the highest points on the route!!!
def get_relevant_indices(vMaxPoints, sPoints):
  lowest = sort_vMaxindices(vMaxPoints)    
  relevantIndices = [0, len(vMaxPoints)- 1]  #[beginning of route, lowest location, end of route]
  print 
  def newLocationisBad(i):
    if i < len(lowest)-1:
      newLocation = util.placeIndexinList(lowest[i], relevantIndices) # append newcomer to list; try it on for size
      actualForwardChange = np.absolute(vMaxPoints[relevantIndices[newLocation+1]]-vMaxPoints[relevantIndices[newLocation]])
      if (np.absolute(sPoints[relevantIndices[newLocation+1]] - sPoints[relevantIndices[newLocation]]) < 2*config.linearAccelTol/config.jerkTol):
        maxForwardChange = np.absolute((sPoints[relevantIndices[newLocation+1]] - sPoints[relevantIndices[newLocation+1]])/2)**2*config.jerkTol
      else: 
        maxForwardChange = np.absolute(sPoints[relevantIndices[newLocation+1]] - sPoints[relevantIndices[newLocation]]-config.linearAccelTol/config.jerkTol)*config.linearAccelTol
      actualBackwardChange = np.absolute(vMaxPoints[relevantIndices[newLocation]]-vMaxPoints[relevantIndices[newLocation-1]])
      if (np.absolute(sPoints[relevantIndices[newLocation]] - sPoints[relevantIndices[newLocation-1]]) < 2*config.linearAccelTol/config.jerkTol):
        maxBackwardChange = np.absolute((sPoints[relevantIndices[newLocation]] - sPoints[relevantIndices[newLocation-1]])/2)**2*config.jerkTol
      else: 
        maxBackwardChange = np.absolute(sPoints[relevantIndices[newLocation]] - sPoints[relevantIndices[newLocation-1]]-config.linearAccelTol/config.jerkTol)*config.linearAccelTol
      relevantIndices.pop(newLocation) # return list back to normal
      if (actualForwardChange > maxForwardChange or actualBackwardChange > maxBackwardChange):  # Let's see; how did we do?
        return True
      else:
        return False
    else:
      return False

  def scan():
    i = 0
    while newLocationisBad(i):
      i+=1
    if (i >= len(lowest)-1 or len(lowest)<2):
      return "Stop"
    else:
      util.placeIndexinList(lowest[i], relevantIndices)
      lowest.pop(i)
      return "Go"

  while scan() == "Go":  #we will continue to zero-out pylons while it is safe to do so. 
    pass
  return list(set(relevantIndices))


def vPoints(xPoints):
  sPoints, vmaxpoints = vMaxPoints(xPoints)
  relevantIndices = get_relevant_indices(vmaxpoints, sPoints)
  relevantsPoints, relevantvMaxPoints = [[sPoints[i] for i in relevantIndices], [vmaxpoints[i] for i in relevantIndices]]
  vFunc = interp1d(relevantsPoints, relevantvMaxPoints, kind='cubic')
  return [sPoints, vFunc(sPoints), vmaxpoints]


