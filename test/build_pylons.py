import clothoid
import quintic as quint


def build_waypoints_bcs_sets(sPoints, zPoints, n):    
    numSIntervals = len(sPoints) - 1
    numSets = int(math.ceil(float(numSIntervals) / float(n)))
    waypointsBCsSets = [0 for i in range(numWaypointsBCsSets)]

    #Each set of waypoints and boundary conditions contains the following:
    # Take N to be the number of waypoints.
    # [list of independent variable values e.g. "t_i",
    #  list of dependent variable values e.g. "x_i = x(t_i)",
    #  initial first derivative of dependent variable e.g. "dx/dt|(t_0)"
    #  initial second derivative of dependent variable e.g. "dx^2/dt^2|(t_0)"     
    #  final first derivative of dependent variable e.g. "dx/dt|(t_N)"
    #  final second derivative of dependent variable e.g. "dx^2/dt^2|(t_N)"]
     
    if numSets == 1:
        waypointsBCsSets = [[sPoints, zPoints, 0, 0, 0, 0]]
    elif numSets == 2:
        waypointsBCsSets[0] = [sPoints[0 : n+1],
                               zPoints[0 : n+1],
                               0,               
                               0,               
                               ((zPoints[n+1] - zPoints[n])/
                                (sPoints[n+1] - sPoints[n])),
                               0]                       

        waypointsBCsSets[1] = [sPoints[n : numSIntervals+1],
                               zPoints[n : numSIntervals+1],
                               ((zPoints[n+1] - zPoints[n])/
                                (sPoints[n+1] - sPoints[n])),
                               0,
                               0,
                               0]
    else:
        waypointsBCsSets[0] = [sPoints[0 : n+1],
                               zPoints[0: n+1],
                               0,
                               0,
                               ((zPoints[n+1]-zPoints[n])/
                                (sPoints[n+1]-sPoints[n])),
                               0]  
        for j in range(1, numSets-1):
            waypointsBCSSets[j] = [sPoints[j*n : (j+1)*n+1],
                                   zPoints[j*n : (j+1)*n+1],
                                   ((zPoints[j*n+1]-zPoints[j*n])/
                                    (sPoints[j*n+1]-sPoints[j*n])),
                                   0,
                                   ((zPoints[(j+1)*n+1] - zPoints[(j+1)*n])/
                                    (sPoints[(j+1)*n+1] - sPoints[(j+1)*n])),
                                   0]

        waypointsBCsSets[-1] = [sPoints[(numSets-1)*n : numSIntervals+1],
                                zPoints[(numSets-1)*n : numSIntervals+1],
        ((zPoints[(numSets-1)*n+1] - zPoints[(numSets-1)*n])/
         (sPoints[(numSets-1)*n+1] - sPoints[(numSets-1)*n])),
                                0,
                                0,
                                0]
    return waypointsBCsSets

def szPointstozVals(sPoints, zPoints, n, sVals):
    waypointsBCSSets = build_waypoints_bcs_sets(sPoints, zPoints, n)
    zCoeffs = [quint.minimum_jerk_interpolation(waypointsBCs) for
               waypointsBCs in waypointsBCsSets]
    sVals = np.array(sVals)
    sPoints = np.array(sPoints)
    zVals = quint.coeffs_to_vals(zCoeffs, sVals, sPoints)
    return [sVals, zVals]

def szPointstoHeights(sPoints, zPoints, n):
    waypointsBCSSets = build_waypoints_bcs_sets(sPoints, zPoints, n)
    zCoeffs = [quint.minimum_jerk_interpolation(waypointsBCs) for
               waypointsBCs in waypointsBCsSets]
    sSample = np.linspace(0,sPoints[-1],config.numHeights)
    sPoints = np.array(sPoints)
    Heights = quint.coeffs_to_vals(zCoeffs, sSample, sPoints)
    return Heights

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
    