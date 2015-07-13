import math 
import numpy as np
import random
import time

import config
import clothoid
import util

import math
import numpy as np
import quintic as quint
import interpolation

def szPointstozVals(sPoints, zPoints, n, sVals):
  N = n-1
  M = int(math.ceil((len(sPoints)-1.)/ N))
  G = [0 for i in range(M)]
  if M == 1:
    G = [[sPoints, zPoints, 0, 0, 0, 0]]
  elif M == 2:
    G[0] = [sPoints[0:N+1],zPoints[0:N+1], 0, 0, (zPoints[N+1]-zPoints[N-1])/(sPoints[N+1]-sPoints[N-1]),0]
    G[M-1] = [sPoints[0:N+1],zPoints[0:N+1], (zPoints[N+1]-zPoints[N-1])/(sPoints[N+1]-sPoints[N-1]),0,0,0]
  else:
    G[0] = [sPoints[0:N+1],zPoints[0:N+1],0,0, (zPoints[N+1]-zPoints[N-1])/(sPoints[N+1]-sPoints[N-1]),0]  
    for k in range(2,M):
      G[k-1] = [sPoints[(k-1)*N:k*N+1],zPoints[(k-1)*N:k*N+1], (zPoints[(k-1)*N+1]-zPoints[(k-1)*N-1])/(sPoints[(k-1)*N+1]-sPoints[(k-1)*N-1]),0,(zPoints[k*N+1]-zPoints[k*N-1])/(sPoints[k*N+1]-sPoints[k*N-1]),0]
    G[M-1] = [sPoints[(M-1)*N:len(sPoints)], zPoints[(M-1)*N:len(zPoints)],(zPoints[(M-1)*N+1]-zPoints[(M-1)*N-1])/(sPoints[(M-1)*N+1]-sPoints[(M-1)*N-1]) ,0,0,0]
  zCoeffs = sum([quint.interp(g) for g in G],[])
  sVals = np.array(sVals)
  sPoints = np.array(sPoints)
  zVals = interpolation.Coeffs_to_Vals(zCoeffs, sVals, sPoints)
  return [sVals, zVals]

def szPointstoHeights(sPoints, zPoints, n):
  N = n-1
  M = int(math.ceil((len(sPoints)-1.)/ N))
  G = [0 for i in range(M)]
  if M == 1:
    G = [[sPoints, zPoints, 0, 0, 0, 0]]
  elif M == 2:
    G[0] = [sPoints[0:N+1],zPoints[0:N+1], 0, 0, (zPoints[N+1]-zPoints[N-1])/(sPoints[N+1]-sPoints[N-1]),0]
    G[M-1] = [sPoints[0:N+1],zPoints[0:N+1], (zPoints[N+1]-zPoints[N-1])/(sPoints[N+1]-sPoints[N-1]),0,0,0]
  else:
    G[0] = [sPoints[0:N+1],zPoints[0:N+1],0,0, (zPoints[N+1]-zPoints[N-1])/(sPoints[N+1]-sPoints[N-1]),0]  
    for k in range(2,M):
      G[k-1] = [sPoints[(k-1)*N:k*N+1],zPoints[(k-1)*N:k*N+1], (zPoints[(k-1)*N+1]-zPoints[(k-1)*N-1])/(sPoints[(k-1)*N+1]-sPoints[(k-1)*N-1]),0,(zPoints[k*N+1]-zPoints[k*N-1])/(sPoints[k*N+1]-sPoints[k*N-1]),0]
    G[M-1] = [sPoints[(M-1)*N:len(sPoints)], zPoints[(M-1)*N:len(zPoints)],(zPoints[(M-1)*N+1]-zPoints[(M-1)*N-1])/(sPoints[(M-1)*N+1]-sPoints[(M-1)*N-1]) ,0,0,0]
  zCoeffs = sum([quint.interp(g) for g in G],[])
  sSample = np.linspace(0,sPoints[-1],config.numHeights)
  sPoints = np.array(sPoints)
  Heights = interpolation.Coeffs_to_Vals(zCoeffs, sSample, sPoints)
  return Heights

def curvature(location1, location2, inList, pylonSpacing):
    #print("Called curvature with variables:")
    #print(location1, location2, inList, pylonSpacing)
    data = clothoid.buildClothoid(location1 * pylonSpacing, 
      inList[location1], 0, location2 * pylonSpacing, inList[location2], 0)
    if data[0] < 0:
        return data[1]
    else:
        return data[0] + data[2] * data[1]


def interpolating_indices(inList, pylonSpacing, kTolerance):
    truncatedList = inList[1 : len(inList) - 1]
    truncatedSortedIndices = util.get_indices(truncatedList)
    indices = [0, truncatedSortedIndices[0] + 1, len(inList) - 1]
    i = 1
    while (curvature(indices[i-1],indices[i],inList,pylonSpacing) < kTolerance
      and curvature(indices[i],indices[i+1],inList,pylonSpacing) < kTolerance
      and indices != range(len(inList))):
        k = 0
        #print("b")
        while (truncatedSortedIndices[1] + 1 > indices[k]):
            #print("entered loop")
            k += 1
        #print(i)
        i = k
        indices.insert(k, truncatedSortedIndices[1] + 1)
        del truncatedSortedIndices[0]
    return indices

def pylon_cost(rawHeights, pylonSpacing, maxSpeed, gTolerance,
               costPerPylonLength, pylonBaseCost):
    t0 = time.time()
    kTolerance = gTolerance / math.pow(maxSpeed, 2)
    fixedHeights = [max(rawHeights)] + rawHeights + [max(rawHeights)]
    indices = interpolating_indices(fixedHeights,pylonSpacing,kTolerance)
    indicesNum = len(indices)
    data = [clothoid.buildClothoid(indices[i] * pylonSpacing, 
        fixedHeights[indices[i]], 0, indices[i+1] * pylonSpacing, 
        fixedHeights[indices[i+1]], 0)
        for i in range(indicesNum - 1)]
    kappas, kappaPs, Ls = zip(*data)
    sVals = [n * pylonSpacing for n in range(len(fixedHeights))]
    sPoints = [sVals[index] for index in indices]
    zPoints = [fixedHeights[index] for index in indices]
    sVals, zVals = szPointstozVals(sPoints, zPoints, 5, sVals)
    Heights = szPointstoHeights(sPoints, zPoints, 5)
    pylonHeights = [math.fabs(pylonHeight) for pylonHeight in util.subtract(zVals,fixedHeights)]
    totalLength = sum(pylonHeights)
    numberOfPylons = len(fixedHeights)
    
#    print("The total number of pylons used is: " + str(numberOfPylons) + ".")
#    print("The sum of the lengths of the pylons is: " + str(totalLength) + ".")
    pylonCostTotal = pylonBaseCost * numberOfPylons + costPerPylonLength * totalLength
    t1 = time.time()
    print ("completed pylon cost calculation. process took "+str(t1-t0)+" seconds.")
    return [pylonCostTotal, Heights]

    
        
