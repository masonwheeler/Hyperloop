"""
Original Developer: Jonathan Ward
Purpose of Module: To pull directions data from the Google Maps API.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify naming and add citations.
Citations:
  (http://seewah.blogspot.com/2009/11/gpolyline-decoding-in-python.html)
    - See Wah Chang
"""

# Standard Modules:
import urllib2
import json

# Our Modules:
import util
import config
import cacher


def http_to_string(http_data):
    """Reads HTTP bytecode response and converts it to a string"""
    byte_data = http_data.read()
    string_data = byte_data.decode("utf-8")
    return string_data


def build_directions(origin, destination):
    """Pulls directions from Google API"""
    url = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + \
        origin + '&destination=' + destination + \
        '&key=AIzaSyDNlWzlyeHuRVbWrMSM2ojZm-LzINVcoX4'
    util.smart_print("url: " + url)
    raw_directions = urllib2.urlopen(url)
    string_directions = http_to_string(raw_directions)
    return string_directions


def string_to_polylines(string_data):
    """Converts Directions string to JSON and extracts the polylines."""
    dict_response = json.loads(string_data)
    steps = dict_response['routes'][0]['legs'][0]['steps']
    polylines = []
    for step in steps:
        polylines.append(step["polyline"]["points"])
    return polylines


def decode_polyline(encoded):
    """
    See (http://code.google.com/apis/maps/documentation/polylinealgorithm.html)
    and (See Wah Chang) for exposition of polyline decoding method.
    """
    encoded_len = len(encoded)
    index = 0
    array = []
    lat = 0
    lng = 0

    while index < encoded_len:

        binary = 0
        shift = 0
        result = 0

        while True:
            binary = ord(encoded[index]) - 63
            index += 1
            result |= (binary & 0x1f) << shift
            shift += 5
            if binary < 0x20:
                break

        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat
        shift = 0
        result = 0

        while True:
            binary = ord(encoded[index]) - 63
            index += 1
            result |= (binary & 0x1f) << shift
            shift += 5
            if binary < 0x20:
                break

        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng
        array.append((lat * 1e-5, lng * 1e-5))

    return array


def decode_polylines(polylines):
    """decodes a list of polylines
    """
    return [decode_polyline(polyline) for polyline in polylines]


def build_coordinate_list(start, end):
    """Applies decoding functions to Google API response"""
    string_directions = build_directions(start, end)
    util.smart_print("Obtained directions.")
    polyline_directions = string_to_polylines(string_directions)
    util.smart_print("Opened directions.")
    raw_coordinate_list = decode_polylines(polyline_directions)
    util.smart_print("Decoded directions.")
    coordinate_list = util.remove_duplicates(raw_coordinate_list)
    util.smart_print("Removed duplicate Coordinates.")
    return util.round_points(coordinate_list)


def get_directions(start, end):
    """Fetchs directions if they are already cached, else builds them.
    """
    directions = cacher.get_object("directions", build_coordinate_list,
                                   [start, end], config.DIRECTIONS_FLAG)
    return directions
