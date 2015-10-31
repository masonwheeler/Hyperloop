"""
Original Developer: Jonathan Ward
Todo: Get speeds from legs
"""

# Standard Modules:
import json
import numpy as np
import urllib2

# Custom Modules:
import speed_profile_match_landscapes
import util

import matplotlib.pyplot as plt

class TrainDataDownloader(object):

    ARC_LENGTH_STEP_SIZE = 30.0 #Meters
    MAX_SPEED = 67.0 # Meters/Second
    MAX_ACCEL = 4.9 # Meters/Second^2
    MAX_JERK = 2.0 # Meters/Second^3

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
        do_travel_modes_contain_train = [step['travel_mode'] == "TRANSIT" 
                                    for step in steps]
        if not any(do_travel_modes_contain_train):
            return None
        steps_num_stops = [step['transit_details']['num_stops']
                           for step in steps]
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
        steps_durations_array = np.array(steps_durations)
        steps_distances_array = np.array(steps_distances)
        steps_speeds_by_arc_length = np.array([])
        steps_arc_lengths = np.array([])
        for i in range(len(steps_durations)):
            step_distance = steps_distances_array[i]
            step_num_stops = steps_num_stops[i] - 1
            num_arc_lengths = int(step_distance / self.ARC_LENGTH_STEP_SIZE)
            stop_indices = np.linspace(0, num_arc_lengths, step_num_stops,
                                       endpoint=False)
            stop_indices = np.rint(stop_indices)
            stop_indices = [int(index) for index in stop_indices.tolist()]
            step_arc_lengths = np.empty(num_arc_lengths)
            step_arc_lengths.fill(self.ARC_LENGTH_STEP_SIZE)
            step_arc_lengths = np.cumsum(step_arc_lengths)
            step_speeds_by_arc_length = np.empty(num_arc_lengths)
            step_speeds_by_arc_length.fill(self.MAX_SPEED)
            step_speeds_by_arc_length[stop_indices] = 0.0
            steps_speeds_by_arc_length = np.append(steps_speeds_by_arc_length,
                                                    step_speeds_by_arc_length)
            steps_arc_lengths = np.append(steps_arc_lengths, step_arc_lengths)
        speed_profile = speed_profile_match_landscapes.SpeedProfile(
                                steps_arc_lengths, steps_speeds_by_arc_length,
                                max_longitudinal_accel = self.MAX_ACCEL,
                                max_longitudinal_jerk = self.MAX_JERK)     
        plt.plot(speed_profile.cumulative_time_steps, speed_profile.speeds_by_time)
        return speed_profile

    def get_train_data(self, start, end):
        string_train_data = self.fetch_google_directions_rail_data(start, end)
        train_data = self.decode_string(string_train_data)
        if train_data == None:
            return None
        (total_duration, total_distance, steps_num_stops,
          step_durations, step_distances, polylines) = train_data
        #speed_profile = self.build_speed_profile(step_durations, step_distances,    
        #                                         steps_num_stops)
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
    #start = "New_York"
    #end = "Boston"
    start = "Paris"
    end = "Brussels"
    train_data_downloader = TrainDataDownloader(start, end)
    if train_data_downloader.train_route_exists:
        print train_data_downloader.total_duration
