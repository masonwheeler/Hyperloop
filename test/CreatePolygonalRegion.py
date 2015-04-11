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

t0 = time.time()

ORIGIN ='Los_Angeles'
DESTINATION ='San_Francisco'

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

def get_coordinateList():
    stringDirections = get_directions()
    polylineDirections = string_to_polylines(stringDirections)
    rawCoordinateList = decode_polylines(polylineDirections)
    coordinateList = removeDuplicates(rawCoordinateList)
    return coordinateList         

def list_to_sets( inputList, repeatFirst, polygonDegree ):
    CoordTuples = []
    numTuples = len(inputList) - polygonDegree
    """Creates each of the N+1 sets which define each N-gon"""
    for x in range(0, numTuples):
        currentSlice = inputList[x:x + polygonDegree] 
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

def setToKMLPolygon (inputSet):
    """initializes container list for Polygon Coordinates"""
    PolygonCoords = [] 

    """Adds input coordinates to container list"""
    for eachCoord in inputSet:
        PolygonCoords.append(CoordinateToString(eachCoord))

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

def displayKMLObject(KMLObject):
    displayableKMLObject = etree.tostring(KMLObject, pretty_print = True).decode("utf-8")
    return displayableKMLObject

def CoordinateSetstoPolygons(inputCoordinateTuples):
    Polygons = []
    for coordTuple in inputCoordinateTuples:
        Polygons.append(setToKMLPolygon(coordTuple))
    return Polygons

def polygonsToMultiGeometry(inputPolygons):
    multigeometry = KML.MultiGeometry()
    for polygon in inputPolygons:
        multigeometry.append(polygon)
    return multigeometry

def scaleUp_point(inPoint, scaleFactor):
    outPoint = [value * scaleFactor for value in inPoint]
    return outPoint

def scaleUp_list_of_points(inList,scaleFactor):
    outList = [scaleUp_point(point,scaleFactor) for point in inList]
    return outList

def scaleDown_point(inPoint, scaleFactor):
    outPoint = [value / scaleFactor for value in inPoint]
    return outPoint

def scaleDown_list_of_points(inList,scaleFactor):
    outList = [scaleDown_point(point,scaleFactor) for point in inList]
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

def repair_shapelyPolygons(shapelyPolygons,tolerance):
    repairedPolygons = []
    for shapelyPolygon in shapelyPolygons:
        repairedPolygon = shapelyPolygon.buffer(tolerance)
        repairedPolygons.append(repairedPolygon)            
    return repairedPolygons

def repair_multiPolygon(multiPolygon,tolerance):
    shapelyPolygons = multiPolygon.geoms
    repairedPolygons = repair_shapelyPolygons(shapelyPolygons,tolerance)
    repairedMultiPolygon = MultiPolygon(repairedPolygons)
    return repairedMultiPolygon

def split_list_into_sets(inList, pieceLen):
    pieceLen = max(1, pieceLen)
    sets = []
    for index in range(0, len(inList), pieceLen):
        lenLeft = len(inList) - index
        setLen = min(pieceLen,lenLeft)
        sets.append(inList[index:index + setLen])
    return sets

"""
print(split_list_into_sets([1,2,3,4,5],2) == [[1,2],[3,4],[5]])
"""
def recursiveRepair_PolygonSet(polygonSet,initialTolerance):
    testSet = polygonSet
    currentBuffer = initialTolerance
    while (not validate_shapelyPolygons(testSet)):
        currentBuffer = currentBuffer * 10
        testSet = repair_shapelyPolygons(testSet,currentBuffer)
    repairedSet = testSet    
    return repairedSet

def multiPolygon_to_polygon(testPolygon,initialTolerance,maxAttempts):
    currentTolerance = initialTolerance
    currentAttempt = 0
    while(testPolygon.geom_type=="MultiPolygon" and currentAttempt<maxAttempts):
        currentAttempt = currentAttempt + 1
        currentPolygonSet = testPolygon.geoms
        repairedPolygonSet = repair_shapelyPolygons(currentPolygonSet,currentTolerance)
        testPolygon = cascaded_union(repairedPolygonSet)
        currentTolerance = currentTolerance * 10
    if testPolygon.geom_type=="MultiPolygon":
        print('Failed to fuse polygons:')
        print(testPoly)
        print('with buffer: ')
        print(currentTolerance)
        print('The polygons were valid: ')
        print(validate_shapelyPolygons(testPolygon.geoms))
        polygon = None
        sys.exit()
    else:
        #print('Successfully fused polygon with tolerance: ')
        #print(currentTolerance)
        polygon = testPolygon        
    return polygon

def polygonSet_to_polygon(polygonSet,initialTolerance,maxAttempts):
    repairedPolygons = recursiveRepair_PolygonSet(polygonSet,initialTolerance)
    testPolygon = cascaded_union(repairedPolygons)
    polygon = multiPolygon_to_polygon(testPolygon,initialTolerance,maxAttempts)
    return polygon

def recursive_union(shapelyPolygons,maxUnionNum,initialTolerance,maxAttempts):
    currentNumPolygons = len(shapelyPolygons)
    currentNumPolygonSets = math.ceil(float(currentNumPolygons) / float(maxUnionNum))
    polygonSets = split_list_into_sets(shapelyPolygons, maxUnionNum)
    unionedPolygons = [polygonSet_to_polygon(polygonSet,initialTolerance,maxAttempts) for polygonSet in polygonSets]
    return unionedPolygons

def unionAllPolygons(shapelyPolygons,maxUnionNum,initialTolerance,maxAttempts):
    while (len(shapelyPolygons) > 1):
        shapelyPolygons = recursive_union(shapelyPolygons,maxUnionNum,initialTolerance,maxAttempts)
    boundingPolygon = shapelyPolygons[0]    
    return boundingPolygon

def tuples_to_lists(tuples):
    lists = [list(eachTuple) for eachTuple in tuples]
    return lists

def shapelyPolygon_to_listOfPoints(shapelyPolygon):
    tuplesOfPoints = list(shapelyPolygon.exterior.coords)
    listsOfPoints = tuples_to_lists(tuplesOfPoints)
    return listsOfPoints

scaleFactor = 1000000.0
tolerance = 0.000001
repeatFirst = False 
maxUnionNum = 3

coordinateList = get_coordinateList()
#shortList = coordinateList[0:10]
#print(shortList)

scaledUpList = scaleUp_list_of_points(coordinateList,scaleFactor)
coordinateTuples = list_to_sets(scaledUpList,repeatFirst,10)

rawPolygons = tuples_to_shapelyPolygons(coordinateTuples)
boundingPolygon = unionAllPolygons(rawPolygons,maxUnionNum, tolerance,20)
#this simplifies using the tolerance given
simplifiedPolygon = boundingPolygon.simplify(1.0, preserve_topology=True) 
listOfPoints = shapelyPolygon_to_listOfPoints(simplifiedPolygon)
shortList = listOfPoints[0:10]
print(len(listOfPoints))

""""
scaledDownList = scaleDown_list_of_points(listOfPoints,scaleFactor)
shortList = scaledDownList[0:10]
testKMLPolygon = setToKMLPolygon(shortList)
displayableKMLObject = displayKMLObject(testKMLPolygon)
print(displayableKMLObject)
"""


#For writing to file
"""
fileName = ORIGIN + 'to' + DESTINATION + 'BoundingPolygon.txt' 
pointsFile = open(fileName,'w+')
pointsFile.write(pointsString)
pointsFile.close()
"""

#For KML Polygon Output


#For KML MultiGeometry Output
"""
Polygons = CoordinateSetstoPolygons(CoordinateTuples)
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


