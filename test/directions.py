"""
Original Developer:
    Jonathan Ward

Purpose of Module:
    To pull directions data from the Google Maps API.

Last Modified:
    11/2/15

Last Modified By:
    Mason Wheeler

Last Modification Purpose:
    Adding alternate route functionality

Todo:
    Add method to get alternative Google directions routes.

Citations:
  (http://seewah.blogspot.com/2009/11/gpolyline-decoding-in-python.html)
    - See Wah Chang
"""

# Standard Modules:
from collections import OrderedDict
import numpy as np
import itertools
import json
import urllib2

# Our Modules:
import cacher
import config
import proj
import util

class Directions(object):

    NAME = "directions"
    FLAG = cacher.DIRECTIONS_FLAG
    IS_SKIPPED = cacher.SKIP_DIRECTIONS

    def remove_duplicates(self, in_list):
        """removes duplicates from a list while preserving order"""
        return list(OrderedDict.fromkeys(list(itertools.chain(*in_list))))

    @staticmethod
    def http_to_string(http_data):
        """Reads HTTP bytecode response and converts it to a string"""
        byte_data = http_data.read()
        string_data = byte_data.decode("utf-8")
        return string_data

    @staticmethod
    def from_google_directions(origin, destination):
        """Pulls directions from Google API"""
        url = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + \
            origin + '&destination=' + destination + \
            '&key=AIzaSyDNlWzlyeHuRVbWrMSM2ojZm-LzINVcoX4'
        util.smart_print("url: " + url)
        raw_directions = urllib2.urlopen(url)
        string_directions = http_to_string(raw_directions)
        dict_response = json.loads(string_data)
        routes = dict_response['routes']
        result = []
        for route in routes:
            result.append(Directions(origin, destination, route))
        return result

    def string_to_polylines(self, route_data):
        """Converts Directions string to JSON and extracts the polylines."""
        steps = route_data['legs'][0]['steps']
        polylines = []
        for step in steps:
            polylines.append(step["polyline"]["points"])
        return polylines

    def decode_polyline(self, encoded):
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

    def decode_polylines(self, polylines):
        """decodes a list of polylines
        """
        return [self.decode_polyline(polyline) for polyline in polylines]


    def get_directions_latlngs(self, route_data):
        """Applies decoding functions to Google API response"""
        polyline_directions = self.string_to_polylines(route_data)
        util.smart_print("Opened directions.")
        latlngs_with_duplicates = self.decode_polylines(polyline_directions)
        util.smart_print("Decoded directions.")
        raw_latlngs = self.remove_duplicates(latlngs_with_duplicates)
        util.smart_print("Removed duplicate Coordinates.")
        directions_latlngs = util.round_points(raw_latlngs)
        directions_latlngs_array = np.array([np.array(latlng) for latlng
                                             in directions_latlngs])
        return directions_latlngs_array

    def geospatials_to_latlngs(self, geospatials):
        latlngs = proj.geospatials_to_latlngs(geospatials, self.projection)
        return latlngs

    def __init__(self, start, end, route_data):
        start_name = start.replace("_", " ")
        end_name = end.replace("_", " ")
        self.latlngs = self.get_directions_latlngs(route_data)
        start_latlng = list(self.latlngs[0])
        end_latlng = list(self.latlngs[-1])
        self.spatial_metadata = {"startName" : start_name,
                                 "endName" : end_name,
                                 "startLatLng" : start_latlng,
                                 "endLatLng" : end_latlng}
        self.projection = proj.set_projection(start_latlng, end_latlng)
        self.geospatials = proj.latlngs_to_geospatials(
                                      self.latlngs, self.projection)


class Routes(object):
    NAME = "routes"
    FLAG = cacher.DIRECTIONS_FLAG
    IS_SKIPPED = cacher.SKIP_DIRECTIONS

    def __init__(self, start, end):
        self.values = Directions.from_google_directions(start, end)

def get_directions(*args):
    """Fetchs Directions if already cached, else builds Directions.
    """
    directions = cacher.get_object(Routes.NAME,
                                   Routes,
                                   args,
                                   Routes.FLAG,
                                   Routes.IS_SKIPPED)
    return directions
