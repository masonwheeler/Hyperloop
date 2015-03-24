"""
Jonathan Ward 3/18/2015

This file contains the function definitions for importing the national
park boundaries, and converting their format.
"""

from os import path
from pykml import parser

def get_parkBoundsKML():
	parkBoundsKML = open('nps_boundary.kml','r')
	return parkBoundsKML

def kml_to_coordinates():
	return parkBoundCoords	