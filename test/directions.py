import urllib2
import ast

import util
import cacher

def HTTP_to_string(HTTPData):
    byteData = HTTPData.read()
    stringData = byteData.decode("utf-8")
    return stringData

def directions(origin, destination):
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

"""
Decodes a polyline that was encoded using the Google Maps method.

See http://code.google.com/apis/maps/documentation/polylinealgorithm.html

Source: See Wah Chang
(http://seewah.blogspot.com/2009/11/gpolyline-decoding-in-python.html)
"""

def decode_polyline(encoded):

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
            index += 1
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
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
	    if b < 0x20:
	        break

        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng
        array.append((lat * 1e-5, lng * 1e-5))

    return array

def decode_polylines(polylines):
    return [decode_polyline(polyline) for polyline in polylines]

def coordinate_list(start, end):
    stringDirections = directions(start, end)
    util.smart_print("Obtained directions.")
    polylineDirections = string_to_polylines(stringDirections)  
    util.smart_print("Opened directions.")
    rawCoordinateList = decode_polylines(polylineDirections)
    util.smart_print("Decoded directions.")
    coordinateList = util.remove_duplicates(rawCoordinateList)
    util.smart_print("Removed duplicate Coordinates.")
    return util.round_points(coordinateList)

def get_directions(start, end):
    directions = cacher.get_object("directions", coordinate_list, [start, end], 
                                  cacher.save_listlike)
    return directions
    


