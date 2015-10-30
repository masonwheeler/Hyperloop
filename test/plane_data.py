"""
Original Developer: Jonathan Ward
"""

from bs4 import BeautifulSoup
from geopy.distance import great_circle
import json
import urllib2
import urlparse


class PlaneDataDownloader(object):
    
    def get_time_from_flight_durations(self, start, end):
        base_url = "http://www.flight-durations.com/"
        extension = ('-').join([start, "to", end])
        full_url = base_url + extension
        #print full_url
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
              'address=address' + \
              '&key=AIzaSyDNlWzlyeHuRVbWrMSM2ojZm-LzINVcoX4'
        url_response = urllib2.urlopen(url)
        string_response = self.http_to_string(url_response)
        dict_response = json.loads(string_response)

    def compute_distance(self, start, end):
        start_latlng = self.get_latlng(start)
        end_latlng = self.get_latlng(end)
        total_distance = great_circle(start_latlng, end_latlng).meters
        return total_distance

    def __init__(self, start, end):
        total_time = self.get_time_from_flight_durations(start, end)
        total_distance = self.compute_distance(start, end)        
        self.total_time = total_time
        self.total_distance = total_distance


if __name__ == '__main__':
    start = "San_Francisco"
    end = "Los_Angeles"
    #start = "Paris"
    #end = "Brussels"
    plane_data_downloader = PlaneDataDownloader(start, end)
    print plane_data_downloader.total_time, "minutes."
    print plane_data_downloader.total_distance, "meters."
