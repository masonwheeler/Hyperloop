import json, urllib2, ast, itertools
import sys
from pykml.factory import KML_ElementMaker as KML
from collections import OrderedDict
from lxml import etree
from pykml import parser

origin ='Los_Angeles'
destination ='San_Francisco'

"""Number of points in polygon"""
N = 300

def HTTPToString(HTTPData):
    byteData = HTTPData.read()
    stringData = byteData.decode("utf-8")
    return stringData

def getData():    
    Data = urllib2.urlopen('https://maps.googleapis.com/maps/api/directions/json?origin=' + origin + '&destination=' + destination + '&key=AIzaSyDNlWzlyeHuRVbWrMSM2ojZm-LzINVcoX4')
    stringData = HTTPToString(Data) 
    return stringData

def StringtoPolylines( stringData ):
	dictResponse = ast.literal_eval(stringData) # converts string to dict
	steps = dictResponse['routes'][0]['legs'][0]['steps']
	polylines = []	
	for step in steps : 
		polylines.append(step["polyline"]["points"])
	return polylines  

def decode_line(encoded):

    """Decodes a polyline that was encoded using the Google Maps method.

    See http://code.google.com/apis/maps/documentation/polylinealgorithm.html
    
    This is a straightforward Python port of Mark McClure's JavaScript polyline decoder
    (http://facstaff.unca.edu/mcmcclur/GoogleMaps/EncodePolyline/decode.js)
    and Peter Chng's PHP polyline decode
    (http://unitstep.net/blog/2008/08/02/decoding-google-maps-encoded-polylines-using-php/)

    This is based on code by See Wah Chang
    (http://seewah.blogspot.com/2009/11/gpolyline-decoding-in-python.html)
    """

    encoded_len = len(encoded)
    index = 0
    array = []
    lat = 0
    lng = 0

    while index < encoded_len:

        b = 0
        shift = 0
        result = 0

        while True:
            b = ord(encoded[index]) - 63
            index = index + 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break

        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat

        shift = 0
        result = 0

        while True:
            b = ord(encoded[index]) - 63
            index = index + 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break

        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng

        array.append((lat * 1e-5, lng * 1e-5))

    return array

def decodedPolylines( polylines ):
	decoded = []
	for polyline in polylines:
		decoded.append(decode_line(polyline))
	return decoded

def toTuples( inputList ):
    CoordTuples = []
    numTuples = len(inputList) - (N - 1)
    """Creates each of the N+1 tuples which define each N-gon"""
    for x in range(0, numTuples):
        repeated = inputList[x]
        currentSlice = inputList[x:x + N] 
        currentSlice.append(repeated)
        CoordTuples.append(currentSlice)
    return CoordTuples

def CoordinateToString (inputCoordinate):
    xCoord = str(inputCoordinate[0])
    yCoord = str(inputCoordinate[1])
    """formats the coordinates"""
    coordinateString = ''.join(['\n','              ',yCoord,',',xCoord, '\n','              '])
    return coordinateString

def tupleToKMLPolygon (inputTuple):
    """initializes container list for Polygon Coordinates"""
    PolygonCoords = [] 

    """Adds input coordinates to container list"""
    for Tuple in inputTuple:
        PolygonCoords.append(CoordinateToString(Tuple))

    """initializes string which contains polygon coordinates """
    PolygonCoordinatesString = ''

    for PolygonCoord in PolygonCoords:
        PolygonCoordinatesString = PolygonCoordinatesString + str(PolygonCoord)
    
    """Creates the KML polygon object"""
    KMLPolygon = KML.Polygon(
        KML.outerBoundaryIs(
            KML.LinearRing(
                KML.coordinates(
                    PolygonCoordinatesString
                )
            )
        )
    )
    return KMLPolygon

def CoordinateTuplestoPolygons(inputCoordinateTuples):
    Polygons = []
    for coordTuple in inputCoordinateTuples:
        Polygons.append(tupleToKMLPolygon(coordTuple))
    return Polygons

def polygonsToMultiGeometry(inputPolygons):
    multigeometry = KML.MultiGeometry()
    for polygon in inputPolygons:
        multigeometry.append(polygon)
    return multigeometry

def removeDuplicates(inputList):
    outputList = list(OrderedDict.fromkeys(list(itertools.chain(*inputList))))
    return outputList

"""Removes duplicate coordinate pairs"""
CoordinateList = removeDuplicates(decodedPolylines(StringtoPolylines(getData())))

CoordinateTuples = toTuples(CoordinateList)
Polygons = CoordinateTuplestoPolygons(CoordinateTuples)
MultiGeometry = polygonsToMultiGeometry(Polygons)
PlacemarkMulti = KML.Placemark(MultiGeometry)
kmlMulti = KML.kml(PlacemarkMulti)
printableMulti = etree.tostring(kmlMulti, pretty_print = True).decode("utf-8")

outputFile = open('MultigeometryPolygonalRegion.kml','w+')
outputFile.write(printableMulti)
outputFile.close()

