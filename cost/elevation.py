#!/usr/bin/env python
import math
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import simplejson
import urllib
import time

ELEVATION_BASE_URL = 'https://maps.googleapis.com/maps/api/elevation/json'
CHART_BASE_URL = 'http://chart.apis.google.com/chart'


def getElevation(coordinates):
    args = {
        'locations': '|'.join([str(coordinate[0]) + ',' + str(coordinate[1]) for coordinate in coordinates])
    }

    url = ELEVATION_BASE_URL + '?' + urllib.urlencode(args)
    response = simplejson.load(urllib.urlopen(url))

    # Create a dictionary for each results[] object
    elevationArray = []

    for resultset in response['results']:
        elevationArray.append(resultset['elevation'])

    return elevationArray

def getHeights(cell_center, primitiveVector):
    N = int(np.norm(primitiveVector) / pylon_spacing)
    pylon_locations = [np.add(cell_center, k * pylon_spacing * primitiveVector / np.norm(primitiveVector)) for k in range(-N / 2, N / 2)]
    return getElevation(pylon_locations)


#returns indices of the sorted list.
def getIndices(List): 
    return sorted(range(len(List)), key = lambda k: List[k])

def curvature(n, m, List):
    radii = buildClothoid(n * pylon_spacing, List[n], 0, m * pylon_spacing, List[m], 0)[0:1]
    return max(radii)

def produceInterp_indices(sortedList, sortIndices, g_tol):
    sInd = sortIndices
    Interp_indices = [0, sInd[0], -1]
    i = 1
    while curvature(Interp_indices[i - 1],Interp_indices[i]) < g_tol and curvature(Interp_indices[i],Interp_indices[i + 1]) < g_tol:
        k = 0
        while sInd[1] > Interp_indices[k]:
            k += 1
        i = k
        insert(k - 1, k, Interp_indices, sInd[1])
        remove(sInd, 1)
    return Interp_indices

def elevationCost(cell_center, primitiveVector, pylon_spacing, base_cost, cost_per_length):
    z = getHeights(cell_center, primitiveVector)
    n = getIndices(z)
    Interp_indices = produceInterp_indices(z, n)
    pylon_length = sum(np.subtract(h, z))
    h = [0]*len(z)
    for k in range(len(Interp_indices)):
        for j in range(Interp_indices[k], Interp_indices[k + 1]):
            h[j] = z[Interp_indices[k]] + (j - Interp_indices[k]) * (z[Interp_indices[k + 1]] - z[Interp_indices[k]])
    cost = cost_per_length * pylon_height + len(z) * base_cost
    return cost 



pylon_spacing = 7
cost_per_length = 100
base_cost = 10
cell_center = [0,0]
primitiveVector = [1,0]
#print elevationCost(cell_center, primitiveVector, pylon_spacing, base_cost, cost_per_length)
coordinates = [
[-118.542569121974,34.39180314594903],
[-118.5726782085907,34.42573843377703],
[-118.588806279766,34.43246046885258],
[-118.6127804458115,34.45237513675877],
[-118.6144358771204,34.47380623839012],
[-118.6212564796037,34.49095944887284],
[-118.6331899475494,34.51309927611657],
[-118.6774002503572,34.55924454709691],
[-118.7096804992186,34.58604135082059],
[-118.7426694608903,34.63241424132433],
[-118.7530926999706,34.65317552437557], 
[-118.7800247763688,34.68104965486667],
[-118.7955193340742,34.7028802312189],
[-118.8134599623722,34.72396607524714],
[-118.8344722241956,34.7551438114581],
[-118.8668964617316,34.79224217738597]]

coordinates_array = [(coordinate[1], coordinate[0]) for coordinate in coordinates]

start_time = time.time()
print getElevation(coordinates_array)
print("--- %s seconds ---" % (time.time() - start_time))




















