"""
Original Developer: Jonathan Ward
"""

from bs4 import BeautifulSoup
import geopy
import re
import urllib2
import urlparse


class PlaneDataDownloader(object):
    
    def download_from_flight_durations(self, start, end):
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
        distance_numbers = [int(s) for s in distance_string.split() 
                            if s.isdigit()]
        if len(time_numbers) > 1:
            hours, minutes = time_numbers       
            total_time = 60*hours + minutes
        else:
            total_time = time_numbers[0]
        return total_time

    def __init__(self, start, end):
        total_time = self.download_from_flight_durations(start, end)
        self.total_time = total_time

if __name__ == '__main__':
    start = "San_Francisco"
    end = "Los_Angeles"
    #start = "Paris"
    #end = "Brussels"
    plane_data_downloader = PlaneDataDownloader(start, end)
    print plane_data_downloader.total_time, "minutes."
