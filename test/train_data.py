"""
Original Developer: Jonathan Ward
Todo: Get speeds from legs
"""

# Standard Modules:
import json
import numpy as np
import urllib2

# Custom Modules:
import util


class TrainDataDownloader(object):

    ARC_LENGTH_STEP_SIZE = 100 #Meters
    MAX_SPEED = 80 #Meters/Second

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
        print url
        raw_train_data = urllib2.urlopen(url)
        string_train_data = self.http_to_string(raw_train_data)
        return string_train_data

    def decode_string(self, string_data):
        """Converts Directions string to JSON and extracts the polylines."""
        dict_response = json.loads(string_data)
        steps = dict_response['routes'][0]['legs'][0]['steps']
        are_travel_modes_transit = [step['travel_mode'] == "TRANSIT" 
                                    for step in steps]
        if not all(are_travel_modes_transit):
            return None
        steps_num_stops = [step['transit_details']['num_stops']
                           for step in steps]
        print steps_num_stops
        total_duration = \
            dict_response['routes'][0]['legs'][0]['duration']['value']
        total_distance = \
            dict_response['routes'][0]['legs'][0]['distance']['value']
        polylines = []
        steps_distances = []
        steps_durations = []
        for step in steps:
            polylines.append(step["polyline"]["points"])
            step_distance = step["distance"]["value"]
            step_duration = step["duration"]["value"]
            steps_distances.append(step_distance)
            steps_durations.append(step_duration)
        return [total_duration, total_distance, steps_num_stops,
                steps_durations, steps_distances, polylines]
        
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

    def build_speed_profile(self, steps_durations, steps_distances, 
                            steps_num_stops):
        step_durations_array = np.array(step_durations)
        print step_durations_array
        step_distances_array = np.array(step_distances)
        print step_distances_array
        step_average_speeds_array = np.divide(step_distances_array,
                                              step_durations_array)
        print "average speeds"
        print step_average_speeds_array
        steps_speeds_by_arc_length = np.array([])
        steps_arc_lengths = np.array([])
        for i in range(len(step_durations)):
            step_distance = steps_distances_array[i]
            step_num_stops = steps_num_stops[i]
            num_steps = int(step_distance / self.ARC_LENGTH_STEP_SIZE)
            stop_indices = np.linspace(0, num_steps.shape[0], step_num_stops)
            step_arc_lengths = np.empty(num_steps)
            step_arc_lengths.fill(self.ARC_LENGTH_STEP_SIZE)
            step_arc_lengths = np.cumsum(step_arc_lengths)
            step_speeds_by_arc_length = np.empty(num_steps)
            step_speeds_by_arc_length.fill(self.MAX_SPEED)
            step_speeds_by_arc_length[stop_indices] = 0.0
            steps_speeds_by_arc_length = np.append(steps_speeds_by_arc_length,
                                                    step_speeds_by_arc_length)
            steps_arc_lengths = np.append(steps_arc_lengths, step_arc_lengths)
        speed_profile = speed_profile.match_landscapes.SpeedProfile(
                                steps_arc_lengths, steps_speeds_by_arc_length)
        print round( speed_profile.trip_time / 60.0, 2)
        return speed_profile

    def get_train_data(self, start, end):
        string_train_data = self.fetch_google_directions_rail_data(start, end)
        train_data = self.decode_string(string_train_data)
        if train_data == None:
            return None
        (total_duration, total_distance, steps_num_stops,
          step_durations, step_distances, polylines) = train_data
        speed_profile = self.build_speed_profile(step_durations, step_distances,    
                                                 steps_num_stops)
        latlngs = self.decode_polylines(polylines)
        return [total_duration, total_distance, latlngs]     

    def __init__(self, start, end):
        train_data = self.get_train_data(start, end)
        if train_data == None:
            self.train_route_exists = False
        else:
            self.train_route_exists = True
            total_duration, total_distance, latlngs = train_data
            self.total_duration = round(total_duration / 60.0, 3)
            self.total_distance = total_distance
            self.latlngs = latlngs

        
if __name__ == '__main__':
    #start = "San_Francisco"
    #end = "Los_Angeles"
    start = "New_York"
    end = "Boston"
    train_data_downloader = TrainDataDownloader(start, end)   
