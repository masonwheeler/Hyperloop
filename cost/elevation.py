#!/usr/bin/env python
import math
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import simplejson
import urllib

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



coordinates = [(36.578581,-118.291994), (36.23998,-116.83171)]

print getElevation(coordinates)
