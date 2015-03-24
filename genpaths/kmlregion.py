"""
Jonathan Ward 3/18/2015

This file contains the function definitions for creating the KML 
MultiGeometry object corresponding to the polygonal bounding region.
"""

from pykml.factory import KML_ElementMaker as KML
from lxml import etree
from pykml import parser

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

    
