import clothoid


def curvature(location1, location2, elevations):
    "Computes the curvature of the clothoid"
    x0 = location1 * config.pylonSpacing
    x1 = location2 * config.pylonSpacing
    theta0 = 0
    theta1 = 0
    y0 = inList[location1]
    y1 = inList[location2]
    kappa, kappaPrime, L = clothoid.buildClothoid(x0, y0, theta0,
                                                  x1, y1, theta1)
    if kappa < 0:
        return kappaPrime
    else:
        return kappa + L * kappaPrime

def reversesort_elevationindices(elevations):
    elevationsIndices = range(len(elevations))
    sortedIndices = sorted(elevationsIndices,
                            key = lambda i: elevations[i], reverse=True)
    return sortedIndices


#Note: get_relevant_indices() crashes if either start OR end are the highest points on the route!!!
def get_relevant_indices(elevations, pylonSpacing):
    tallest = reversesort_elevationindices(elevations)    
    relevantIndices = [0, len(elevations)- 1]  #[beginning of route, tallest location, end of route]

    def newLocationisBad(i):
      newLocation = util.placeIndexinList(tallest[i], relevantIndices) # append newcomer to list; try it on for size
      backwardCurvature = curvature(relevantIndices[newLocation-1], relevantIndices[newLocation], elevations)
      forwardCurvature = curvature(relevantIndices[newLocation], relevantIndices[newLocation+1], elevations)
      relevantIndices.pop(newLocation) # return list back to normal
      
      curvatureTolerance = config.gTolerance * config.maxSpeed**2
      if max(backwardCurvature, forwardCurvature) < curvatureTolerance:  # Let's see; how did we do?
        return False
      else:
        return True

    def scan():
      i = 0
      while newLocationisBad(i):
        i+=1
      if i == len(tallest):
        return "Stop"
      else:
        util.placeIndexinList(tallest[i], relevantIndices)
        return "Go"

    while scan() == "Go":  #we will continue to zero-out pylons while it is safe to do so. 
    return relevantIndices


def build_pylons(sVals, xVals):
     xValsLonglats = proj.geospatials_to_latlngs(xVals, config.proj)
     Elevations = elevation.usgs_elevation(pylonLatLngs)
     j = []
     i = 0
     for k in range(int(sVals[-1]/config.pylonSpacing)):
       while sVals[i] < k*config.pylonSpacing:
          i+=1
       j+=[i]
     pylonsVals, pylonElevations = [[sVals[jIndex] for jIndex in j],[Elevations[jIndex] for jIndex in j]]
     curvatureTolerance = config.gTolerance * math.pow(config.maxSpeed, 2)
     relevantIndices = get_relevant_indices(paddedElevations, config.pylonSpacing,
                                            curvatureTolerance)
     relevantsVals, relevantzVals =  [[pylonsVals[relevantIndex] for relevantIndex in relevantIndices],\
                      [pylonElevations[relevantIndex] for relevantIndex in relevantIndices]]
     zFunc = interp1d(relevantsVals, relevantzVals, kind='cubic')
     return [sVals, zFunc(sVals)]
 
 