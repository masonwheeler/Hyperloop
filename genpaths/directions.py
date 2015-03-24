"""
Jonathan Ward 3/18/2015

This file contains the function definitions for getting the coordinates
from the google driving directions for a pair of cities, as well as the 
function definition for creating the tuples corresponding to the polygons
which will comprise the bounding polygonal region.
"""

import json, urllib2, ast, itertools
from collections import OrderedDict

def HTTP_to_string(HTTPData):
    byteData = HTTPData.read()
    stringData = byteData.decode("utf-8")
    return stringData

def get_directions(origin, destination):    
    rawDirections = urllib2.urlopen('https://maps.googleapis.com/maps/api/directions/json?origin=' + origin + '&destination=' + destination + '&key=AIzaSyDNlWzlyeHuRVbWrMSM2ojZm-LzINVcoX4')
    stringDirections = HTTP_to_string(rawDirections) 
    return stringDirections

def string_to_polylines( stringData ):
	dictResponse = ast.literal_eval(stringData) # converts string to dict
	steps = dictResponse['routes'][0]['legs'][0]['steps']
	polylines = []	
	for step in steps : 
		polylines.append(step["polyline"]["points"])
	return polylines  

def decode_line(encoded):

    """
    Decodes a polyline that was encoded using the Google Maps method.

    See http://code.google.com/apis/maps/documentation/polylinealgorithm.html

    Source: See Wah Chang
    (http://seewah.blogspot.com/2009/11/gpolyline-decoding-in-python.html)
    """

    encoded_len = len(encoded)
    index = 0
    array = []
    lat = 0
    lng = 0

    while index < encoded_len:

        b = 0
        shift = 0
        result = 0

        while True:
            b = ord(encoded[index]) - 63
            index = index + 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break

        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat

        shift = 0
        result = 0

        while True:
            b = ord(encoded[index]) - 63
            index = index + 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break

        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng

        array.append((lat * 1e-5, lng * 1e-5))

    return array

def decode_polylines( polylines ):
	decoded = []
	for polyline in polylines:
		decoded.append(decode_line(polyline))
	return decoded

def removeDuplicates(inputList):
    outputList = list(OrderedDict.fromkeys(list(itertools.chain(*inputList))))
    return outputList

def get_coordinateList(origin, destination):
    stringDirections = get_directions(origin, destination)
    polylineDirections = string_to_polylines(stringDirections)
    rawCoordinateList = decode_polylines(polylineDirections)
    coordinateList = removeDuplicates(rawCoordinateList)
    return coordinateList     

def list_to_tuples( inputList, repeatFirst, numPts ):
    CoordTuples = []
    numTuples = len(inputList) - numPts
    """Creates each of the N+1 tuples which define each N-gon"""
    for x in range(0, numTuples):
        currentSlice = inputList[x:x + numPts] 
        if repeatFirst:
            currentSlice.append(inputList[x])
        CoordTuples.append(currentSlice)        
    return CoordTuples