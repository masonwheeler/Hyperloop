"""
Original Developer:
    Jonathan Ward

Purpose of Module:
    To pull directions data from the Google Maps API.

Last Modified:
    9/8/15

Last Modified By:
    Jonathan Ward

Last Modification Purpose:
    To add the Directions class.

Todo:
    Add method to get alternative Google directions routes.

Citations:
  (http://seewah.blogspot.com/2009/11/gpolyline-decoding-in-python.html)
    - See Wah Chang
"""

# Standard Modules:
import json
import urllib2

# Our Modules:
import cacher
import config
import proj
import util

class Directions(object):

    def http_to_string(self, http_data):
        """Reads HTTP bytecode response and converts it to a string"""
        byte_data = http_data.read()
        string_data = byte_data.decode("utf-8")
        return string_data

    def fetch_google_directions(self, origin, destination):
        """Pulls directions from Google API"""
        url = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + \
            origin + '&destination=' + destination + \
            '&key=AIzaSyDNlWzlyeHuRVbWrMSM2ojZm-LzINVcoX4'
        util.smart_print("url: " + url)
        raw_directions = urllib2.urlopen(url)
        string_directions = self.http_to_string(raw_directions)
        return string_directions

    def string_to_polylines(self, string_data):
        """Converts Directions string to JSON and extracts the polylines."""
        dict_response = json.loads(string_data)
        steps = dict_response['routes'][0]['legs'][0]['steps']
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


    def get_directions_latlngs(self, start, end):
        """Applies decoding functions to Google API response"""
        string_directions = self.fetch_google_directions(start, end)
        util.smart_print("Obtained directions.")
        polyline_directions = self.string_to_polylines(string_directions)
        util.smart_print("Opened directions.")
        latlngs_with_duplicates = self.decode_polylines(polyline_directions)
        util.smart_print("Decoded directions.")
        raw_latlngs = util.remove_duplicates(latlngs_with_duplicates)
        util.smart_print("Removed duplicate Coordinates.")
        directions_latlngs = util.round_points(raw_latlngs)
        return directions_latlngs

    def geospatials_to_latlngs(self, geospatials):
        latlngs = proj.geospatials_to_latlngs(geospatials, self.projection)
        return latlngs        

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.latlngs = self.get_directions_latlngs(start, end)
        self.start_latlng = self.latlngs[0]
        self.end_latlng = self.latlngs[-1]
        self.projection = proj.set_projection(self.start_latlng, self.end_latlng)
        self.geospatials = proj.latlngs_to_geospatials(
                                      self.latlngs, self.projection)


def get_directions(start, end):
    """Fetchs Directions if already cached, else builds Directions.
    """
    directions = cacher.get_object("directions", Directions,
                                   [start, end], config.DIRECTIONS_FLAG)
    return directions
