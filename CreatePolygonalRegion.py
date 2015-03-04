import json, urllib2, ast, itertools
import sys
import time
import math
from collections import OrderedDict
from pykml.factory import KML_ElementMaker as KML
from lxml import etree
from pykml import parser
from shapely.ops import cascaded_union
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon
from shapely.geometry import Point
from copy import deepcopy

t0 = time.time()

ORIGIN ='Los_Angeles'
DESTINATION ='San_Francisco'
NUM_PTS = 4
TOLERANCE = 0.000001
BUFFER = 0.000001
MAX_UNION_LENGTH = 5
SCALE_FACTOR = 1000000

def HTTP_to_string(HTTPData):
    byteData = HTTPData.read()
    stringData = byteData.decode("utf-8")
    return stringData

def get_directions():    
    rawDirections = urllib2.urlopen('https://maps.googleapis.com/maps/api/directions/json?origin=' + ORIGIN + '&destination=' + DESTINATION + '&key=AIzaSyDNlWzlyeHuRVbWrMSM2ojZm-LzINVcoX4')
    stringDirections = HTTP_to_string(rawDirections) 
    return stringDirections

def string_to_polylines( stringData ):
	dictResponse = ast.literal_eval(stringData) # converts string to dict
	steps = dictResponse['routes'][0]['legs'][0]['steps']
	polylines = []	
	for step in steps : 
		polylines.append(step["polyline"]["points"])
	return polylines  

def decode_line(encoded):

    """
    Decodes a polyline that was encoded using the Google Maps method.

    See http://code.google.com/apis/maps/documentation/polylinealgorithm.html

    Source: See Wah Chang
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

def decode_polylines( polylines ):
	decoded = []
	for polyline in polylines:
		decoded.append(decode_line(polyline))
	return decoded

def removeDuplicates(inputList):
    outputList = list(OrderedDict.fromkeys(list(itertools.chain(*inputList))))
    return outputList

def list_to_tuples( inputList, repeatFirst ):
    CoordTuples = []
    numTuples = len(inputList) - NUM_PTS
    """Creates each of the N+1 tuples which define each N-gon"""
    for x in range(0, numTuples):
        currentSlice = inputList[x:x + NUM_PTS] 
        if repeatFirst:
            currentSlice.append(inputList[x])
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

def scale_point(inPoint):
    outPoint = [value * SCALE_FACTOR for value in inPoint]
    return outPoint

def scale_list_of_points(inList):
    outList = [scale_point(point) for point in inList]
    return outList

def tuple_to_shapelyPolygon(aTuple):
    shapelyPolygon = Polygon(aTuple)
    return shapelyPolygon

def tuples_to_shapelyPolygons(tuples):
    Polygons = [Polygon(eachTuple) for eachTuple in tuples]
    return Polygons

def validate_shapelyPolygons(shapelyPolygons):
    isValid = True
    for polygon in shapelyPolygons:
        polygonValid = polygon.is_valid
        isValid = (isValid and polygonValid)
    return isValid

def repair_shapelyPolygons(shapelyPolygons):
    repairedPolygons = []
    for shapelyPolygon in shapelyPolygons:
        if (not shapelyPolygon.is_valid):
            shapelyPolygon = shapelyPolygon.buffer(BUFFER)
        repairedPolygons.append(shapelyPolygon)            
    return repairedPolygons

def split_list_into_pieces(inList, pieceLen):
    pieceLen = max(1, pieceLen)
    outList = [inList[i:i + pieceLen] for i in range(0, len(inList), pieceLen)]
    return outList

def recursive_union(shapelyPolygons):
    numPolygons = len(shapelyPolygons)
    numPolygonSets = math.ceil(numPolygons / MAX_UNION_LENGTH)
    shapelyPieces = split_list_into_pieces(shapelyPolygons, MAX_UNION_LENGTH)
    shapelyMultis = [MultiPolygon(piece) for piece in shapelyPieces]
    shapelyUnions = [cascaded_union(multi) for multi in shapelyMultis]
    multiPolygon = cascaded_union(shapelyUnions)
    unionPolygon = cascaded_union(multiPolygon)
    simplifiedPolygon = unionPolygon.simplify(TOLERANCE, preserve_topology=True)
    return simplifiedPolygon

def tuples_to_lists(tuples):
    lists = [list(eachTuple) for eachTuple in tuples]
    return lists

def shapelyPolygon_to_listOfPoints(shapelyPolygon):
    tuplesOfPoints = list(shapelyPolygon.exterior.coords)
    listsOfPoints = tuples_to_lists(tuplesOfPoints)
    return listsOfPoints

stringDirections = get_directions()
polylineDirections = string_to_polylines(stringDirections)
rawCoordinateList = decode_polylines(polylineDirections)
coordinateList = removeDuplicates(rawCoordinateList)

rawShortList = coordinateList[0:17]
shortList = scale_list_of_points(rawShortList)
coordinateTuples = list_to_tuples(shortList, False)
#coordinateTuples = list_to_tuples(coordinateList, False)

rawPolygons = tuples_to_shapelyPolygons(coordinateTuples)
shapelyPolygons = repair_shapelyPolygons(rawPolygons)
simplifiedPolygon = recursive_union(shapelyPolygons)
listOfPoints = shapelyPolygon_to_listOfPoints(simplifiedPolygon)
print(listOfPoints)

"""
Polygons = CoordinateTuplestoPolygons(CoordinateTuples)
MultiGeometry = polygonsToMultiGeometry(Polygons)
PlacemarkMulti = KML.Placemark(MultiGeometry)
kmlMulti = KML.kml(PlacemarkMulti)
printableMulti = etree.tostring(kmlMulti, pretty_print = True).decode("utf-8")

outputFile = open('MultigeometryPolygonalRegion.kml','w+')
outputFile.write(printableMulti)
outputFile.close()
"""
t1 = time.time()
print(t1 - t0)
