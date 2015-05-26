#!/usr/bin/env python
import math as m
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.integrate import quad
import simplejson
import urllib
import time
import buildClothoid
import random

R = 6.371*(10**6)
ELEVATION_BASE_URL = 'https://maps.googleapis.com/maps/api/elevation/json'
CHART_BASE_URL = 'http://chart.apis.google.com/chart'

def dxdtht(phi_tht):
    return m.fabs(R * m.cos(2 * m.pi * phi_tht[0] / 360)) * 2 * m.pi / 360

def dydphi(phi_tht):
    return R * 2 * m.pi / 360

def add(vector_1, vector_2):
    return [vector_1[i] + vector_2[i] for i in range(len(vector_1))]

def subtract(vector_1, vector_2):
    return [vector_1[i] - vector_2[i] for i in range(len(vector_1))]

def scale(scalar, vector):
    return [scalar * vector[i] for i in range(len(vector))]

def norm(vector): 
    return m.sqrt(sum([m.pow(vector[i],2) for i in range(len(vector))]))

def entry_multiply(vector_1, vector_2):
    return [vector_1[i] * vector_2[i] for i in range(len(vector_1))]


def catenate(list_of_lists):
    result = []
    for i in range(len(list_of_lists)):
        result = result + list_of_lists[i]
    return result

#_____________BEGINNING OF ELEVATION FUNCTIONS______________

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

def getHeights(cell_center, primitiveVector, pylon_spacing):
    pylon_spacing_deg = pylon_spacing * norm(primitiveVector) / norm([primitiveVector[0] * dydphi(cell_center), primitiveVector[1] * dxdtht(cell_center)])
    N = int(norm(primitiveVector) / pylon_spacing_deg)
    print "N is:"
    print N
    pylon_locations = [add(cell_center, scale(k * pylon_spacing_deg / norm(primitiveVector), primitiveVector)) for k in range(int(-m.floor(N / 2)), int(m.floor(N / 2))+1)]
    coordinates = [(location[1], location[0]) for location in pylon_locations]
    result = []
    for i in range(len(coordinates)/80):
        result += getElevation(coordinates[80*i:80*(i+1)-1])
    k = len(coordinates)/80 - 1
    return result + getElevation(coordinates[80*k:-1])


#returns indices of the sorted list.
def getIndices(List): 
    Indices_backwards = sorted(range(len(List)), key = lambda k: List[k])
    return [Indices_backwards[-i] for i in range(1, len(Indices_backwards))] + [Indices_backwards[0]]

def curvature(location1, location2, List, pylon_spacing):
    data = buildClothoid.buildClothoid(location1 * pylon_spacing, List[location1], 0, location2 * pylon_spacing, List[location2], 0)
    if data[0] < 0:
        return data[1]
    else:
        return data[0] + data[2] * data[1]

def length(location1, location2, List, pylon_spacing):
    return buildClothoid.buildClothoid(location1 * pylon_spacing, List[location1], 0, location2 * pylon_spacing, List[location2], 0)[2]

#def produceInterp_indices(List, sortIndices):
#    N = len(List)
#    truncated_List = [List[i] for i in range(1, N - 1)]
#    truncated_sortIndices = getIndices(truncated_List)
#    j= [0, truncated_sortIndices[0] + 1, N - 1]
#    i = 1
#    while length(j[i - 1], j[i], List) < (j[i] - j[i - 1]) * pylon_spacing + m.fabs(List[j[i]] - List[j[i - 1]]) and length(j[i], j[i + 1], List) < (j[i + 1] - j[i]) * pylon_spacing + m.fabs(List[j[i + 1]] - List[j[i]]) and j != range(len(List)):
#        print "trying a new point, because the lengths for the previous choice are:"
#        print length(j[i - 1], j[i], List)
#        print length(j[i], j[i + 1], List)
#        k = 0
#        print "This is the index of the new point:"
#        print truncated_sortIndices[1] + 1
#        print "we're trying to fit it in j:"
#        print j
#        while truncated_sortIndices[1] + 1 > j[k]:
#            k += 1
#        i = k
#        j.insert(k, truncated_sortIndices[1] + 1)
#        print "Did we insert the index in the right place?:"
#        print j        
#        print "okay, done! - just one more thing: is sInd missing its first element?:"
#        print truncated_sortIndices
#        del truncated_sortIndices[0]
#        print truncated_sortIndices
#    print "we did not continue, because the lengths for the previous choice are:"
#    print length(j[i - 1], j[i], List)
#    print length(j[i], j[i + 1], List)
#    print "or it could just be because we got 'em all:"
#    return j

def produceInterp_indices(List, sortIndices, pylon_spacing, k_tol):
    N = len(List)
    truncated_List = [List[i] for i in range(1, N - 1)]
    truncated_sortIndices = getIndices(truncated_List)
    j= [0, truncated_sortIndices[0] + 1, N - 1]
    i = 1
    while curvature(j[i - 1], j[i], List, pylon_spacing) < k_tol and curvature(j[i], j[i + 1], List, pylon_spacing) < k_tol and j != range(len(List)):
 #       print "trying a new point, because the lengths for the previous choice are:"
 #       print curvature(j[i - 1], j[i], List)
 #       print curvature(j[i], j[i + 1], List)
        k = 0
 #       print "This is the index of the new point:"
 #       print truncated_sortIndices[1] + 1
 #       print "we're trying to fit it in j:"
 #       print j
        while truncated_sortIndices[1] + 1 > j[k]:
            k += 1
        i = k
        j.insert(k, truncated_sortIndices[1] + 1)
 #       print "Did we insert the index in the right place?:"
 #       print j        
 #       print "okay, done! - just one more thing: is sInd missing its first element?:"
 #       print truncated_sortIndices
        del truncated_sortIndices[0]
 #       print truncated_sortIndices
 #   print "we did not continue, because the lengths for the previous choice are:"
 #   print curvature(j[i - 1], j[i], List)
 #   print curvature(j[i], j[i + 1], List)
 #   print "or it could just be because we got 'em all:"
    return j


def visualize(j, List, pylon_spacing):
    N = len(j)
    data = [buildClothoid.buildClothoid(j[i] * pylon_spacing, List[j[i]], 0, j[i+1] * pylon_spacing, List[j[i+1]], 0) for i in range(N-1)]
    kappas = [elt[0] for elt in data]
    kappaps = [elt[1] for elt in data]
    Ls = [elt[2] for elt in data]
    x0s = [n * pylon_spacing for n in range(len(List))]
    xvals = catenate([[x0s[j[i]] + s * buildClothoid.evalXY(kappaps[i] * m.pow(s,2), kappas[i] * s, 0, 1)[0][0] for s in np.linspace(0, Ls[i] , 100)] for i in range(len(j)-1)])
    yvals = catenate([[List[j[i]] + s * buildClothoid.evalXY(kappaps[i] * m.pow(s,2), kappas[i] * s, 0, 1)[1][0] for s in np.linspace(0, Ls[i] , 100)] for i in range(len(j)-1)])
    yvals_plot = [0] * len(List)
    for l in range(len(j)-1):
        for n in range(j[l], j[l + 1]):
            yvals_plot[n] = yvals[100 * l + int((n - j[l]) * 100 / (j[l + 1] - j[l]))]
    fig = plt.figure()
    plt.plot(xvals, yvals, label = "elevation of tube")
    plt.plot(np.arange(0, pylon_spacing * len(List), pylon_spacing), List, label = "elevation of terrain")
    plt.vlines(np.arange(0, pylon_spacing * len(List), pylon_spacing), List, yvals_plot)
    plt.legend(bbox_to_anchor=(.85, 1.), loc=2, borderaxespad=-3.)
    fig.suptitle('Result of Pylon Placement')
    plt.xlabel('distance (m)')
    plt.ylabel('elevation (m above sealevel)')
    print("--- %s seconds ---" % (time.time() - start_time))
    return plt.show()

def pylon_cost(cell_center, primitiveVector, pylon_spacing, max_speed, g_tol, cost_perlength, base_cost):
    k_tol = g_tol/ m.pow(max_speed, 2)
    Listp = getHeights(cell_center,primitiveVector, pylon_spacing)
    List = [max(Listp)-30]+Listp+[max(Listp)-30]
    sortIndices = getIndices(List)
    j = produceInterp_indices(List, sortIndices, pylon_spacing, k_tol)
    N = len(j)
    data = [buildClothoid.buildClothoid(j[i] * pylon_spacing, List[j[i]], 0, j[i+1] * pylon_spacing, List[j[i+1]], 0) for i in range(N-1)]
    kappas = [elt[0] for elt in data]
    kappaps = [elt[1] for elt in data]
    Ls = [elt[2] for elt in data]
    x0s = [n * pylon_spacing for n in range(len(List))]
    xvals = catenate([[x0s[j[i]] + s * buildClothoid.evalXY(kappaps[i] * m.pow(s,2), kappas[i] * s, 0, 1)[0][0] for s in np.linspace(0, Ls[i] , 100)] for i in range(len(j)-1)])
    yvals = catenate([[List[j[i]] + s * buildClothoid.evalXY(kappaps[i] * m.pow(s,2), kappas[i] * s, 0, 1)[1][0] for s in np.linspace(0, Ls[i] , 100)] for i in range(len(j)-1)])
    yvals_plot = [0] * len(List)
    for l in range(len(j)-1):
        for n in range(j[l], j[l + 1]):
            yvals_plot[n] = yvals[100 * l + int((n - j[l]) * 100 / (j[l + 1] - j[l]))]
    pylon_heights = [m.fabs(pylon_height) for pylon_height in subtract(yvals_plot, List)]
    total_length = sum(pylon_heights)
    print "total # of pylons:"
    print len(List)
    print "total length of pylon:"
    print total_length
    pylon_cost_total = base_cost * len(List) + cost_perlength * total_length
    fig = plt.figure()
    plt.plot(xvals, yvals, label = "elevation of tube")
    plt.plot(np.arange(0, pylon_spacing * len(List), pylon_spacing), List, label = "elevation of terrain")
    plt.vlines(np.arange(0, pylon_spacing * len(List), pylon_spacing), List, yvals_plot)
    plt.legend(bbox_to_anchor=(.85, 1.), loc=2, borderaxespad=-3.)
    fig.suptitle('Result of Pylon Placement')
    plt.xlabel('distance (m)')
    plt.ylabel('elevation (m above sealevel)')
    print "total pylon cost:"
    print pylon_cost_total
    print("--- %s seconds ---" % (time.time() - start_time))
    plt.show()
    return pylon_cost_total

cell_center = [-80.0,40.0]
primitiveVector = [0.05,0.0]
pylon_spacing = 100.
max_speed = 80.
g_tol = .2 * 9.8
cost_perlength = 10000
base_cost = 2000


start_time = time.time()
pylon_cost(cell_center, primitiveVector, pylon_spacing, max_speed, g_tol, cost_perlength, base_cost)

