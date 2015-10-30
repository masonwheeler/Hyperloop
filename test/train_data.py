"""
Original Developer: Jonathan Ward
Todo: Get speeds from legs
"""

# Standard Modules:
import json
import urllib2

# Custom Modules:
import util


class TrainDataDownloader(object):

    def http_to_string(self, http_data):
        """Reads HTTP bytecode response and converts it to a string"""
        byte_data = http_data.read()
        string_data = byte_data.decode("utf-8")
        return string_data

    def fetch_google_directions_rail_data(self, start, end):
        url = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + \
               start + '&destination=' + end + \
               '&mode=transit' + '&transit_mode=rail' + \
               '&key=AIzaSyDNlWzlyeHuRVbWrMSM2ojZm-LzINVcoX4'
        #print url
        raw_train_data = urllib2.urlopen(url)
        string_train_data = self.http_to_string(raw_train_data)
        return string_train_data

    def decode_string(self, string_data):
        """Converts Directions string to JSON and extracts the polylines."""
        dict_response = json.loads(string_data)
        steps = dict_response['routes'][0]['legs'][0]['steps']
        total_time = dict_response['routes'][0]['legs'][0]['duration']['value']
        total_distance = dict_response['routes'][0]['legs'][0]['duration']['value']
        polylines = []
        for step in steps:
            polylines.append(step["polyline"]["points"])
        return [total_time, total_distance, polylines]
        
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

    def get_train_data(self, start, end):
        string_train_data = self.fetch_google_directions_rail_data(start, end)
        total_time, total_distance, polylines = self.decode_string(
                                                     string_train_data)
        latlngs = self.decode_polylines(polylines)
        return [total_time, total_distance, latlngs]        

    def __init__(self, start, end):
        total_time, total_distance, latlngs = self.get_train_data(start, end)
        self.total_time = round(total_time / 60.0, 3)
        self.total_distance = total_distance
        self.latlngs = latlngs

        
if __name__ == '__main__':
    start = "San_Francisco"
    end = "Los_Angeles"
    train_data_downloader = TrainDataDownloader(start, end)   
