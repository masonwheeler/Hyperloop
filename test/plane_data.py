"""
Original Developer: Jonathan Ward
Citation: http://www.rita.dot.gov/bts/sites/rita.dot.gov.bts/files/publications/special_reports_and_issue_briefs/special_report/2008_008/html/entire.html
"""

# Standard Modules:
from bs4 import BeautifulSoup
from geopy.distance import great_circle
import json
import numpy as np
from pyproj import Geod
import urllib2
import urlparse

# Custom Modules:
import speed_profile_match_landscapes
import util


class PlaneDataDownloader(object):
    
    PLANE_MAX_SPEED = 216.0 #Meters/Second
    ARC_LENGTH_SPACING = 50.0 #Meters
    TAXI_IN_TIME = 6.9 #Min
    TAXI_OUT_TIME = 16.7 #Min

    def get_time_from_flight_durations(self, start, end):
        base_url = "http://www.flight-durations.com/"
        extension = ('-').join([start, "to", end])
        full_url = base_url + extension
        html_reponse = urllib2.urlopen(full_url)
        soup = BeautifulSoup(html_reponse, 'lxml')
        relevant_spans = soup.find_all('span', {"class" : "lead"})
        relevant_spans_text = [span.getText() for span in relevant_spans]
        time_string, distance_string = relevant_spans_text 
        time_numbers = [int(s) for s in time_string.split() if s.isdigit()]
        if len(time_numbers) > 1:
            hours, minutes = time_numbers       
            total_time = 60*hours + minutes
        else:
            total_time = time_numbers[0]
        return total_time

    def http_to_string(self, http_data):
        """Reads HTTP bytecode response and converts it to a string"""
        byte_data = http_data.read()
        string_data = byte_data.decode("utf-8")
        return string_data

    def get_latlng(self, address):
        url = 'https://maps.googleapis.com/maps/api/geocode/json?' + \
              'address=' + address + \
              '&key=AIzaSyBkiX4t39S75fE8Cqk5guvoLJEVurKyRpA'
        url_response = urllib2.urlopen(url)       
        string_response = self.http_to_string(url_response)
        dict_response = json.loads(string_response)
        lat = dict_response['results'][0]['geometry']['location']['lat']
        lng = dict_response['results'][0]['geometry']['location']['lng']
        return [lat, lng]

    def reverse_geocode(self, start, end):
        start_latlng = self.get_latlng(start)
        end_latlng = self.get_latlng(end)
        return [start_latlng, end_latlng]

    def compute_distance(self, start_latlng, end_latlng):
        total_distance = great_circle(start_latlng, end_latlng).meters
        return total_distance

    def build_great_circle(self, start_latlng, end_latlng, distance):
        num_points = int(distance / self.ARC_LENGTH_SPACING)
        geod = Geod(ellps='WGS84')
        start_lat, start_lon = start_latlng
        end_lat, end_lon = end_latlng
        lonlats = geod.npts(start_lon, start_lat, end_lon, end_lat, num_points)
        latlngs = util.swap_pairs(lonlats)
        return latlngs

    def build_speed_profile(self, total_distance, total_time):
        num_arc_lengths = int(total_distance / self.ARC_LENGTH_SPACING)
        steps = np.empty(num_arc_lengths)
        steps.fill(self.ARC_LENGTH_SPACING)        
        arc_lengths = np.cumsum(steps)
        max_speeds_by_arc_length = np.empty(num_arc_lengths)
        max_speeds_by_arc_length.fill(self.PLANE_MAX_SPEED)
        print "computing speed profile..."
        speed_profile = speed_profile_match_landscapes.SpeedProfile(arc_lengths,
                                                       max_speeds_by_arc_length)
        print "computed speed profile"
        return speed_profile

    def __init__(self, start, end):
        total_time = self.get_time_from_flight_durations(start, end)
        start_latlng, end_latlng = self.reverse_geocode(start, end)
        total_distance = self.compute_distance(start_latlng, end_latlng)
        speed_profile = self.build_speed_profile(total_distance, total_time)
        air_time = round(speed_profile.trip_time / 60.0, 2)
        taxiing_time = self.TAXI_IN_TIME + self.TAXI_OUT_TIME
        total_flight_time = air_time + taxiing_time
        print total_flight_time, "minutes."
        #print speed_profile.speeds_by_arc_length[:10]        
        latlngs = self.build_great_circle(start_latlng, end_latlng, 
                                                    total_distance)
        self.total_time = total_time
        self.total_distance = total_distance
        self.latlngs = latlngs


if __name__ == '__main__':
    start = "San_Francisco"
    end = "Los_Angeles"
    #start = "Paris"
    #end = "Brussels"
    plane_data_downloader = PlaneDataDownloader(start, end)
    print plane_data_downloader.total_time, "minutes."
    print plane_data_downloader.total_distance, "meters."
