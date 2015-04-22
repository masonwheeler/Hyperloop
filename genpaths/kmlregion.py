"""
Jonathan Ward 4/22/2015

This file contains the function definitions for creating the KML 
MultiGeometry object corresponding to the polygonal bounding region.
"""

from pykml.factory import KML_ElementMaker as KML
from lxml import etree
from pykml import parser

def CoordinateToString (inputCoordinate, isMultiGeometry):
    xCoord = str(inputCoordinate[0])
    yCoord = str(inputCoordinate[1])
    """formats the coordinates"""
    if isMultiGeometry:
        coordinateString = ''.join(['\n','              ',yCoord,',',xCoord, '\n','              '])
    else:    
        coordinateString = ''.join(['\n','          ',yCoord,',',xCoord, '\n','          '])
    return coordinateString

def setToKMLPolygon (inputSet, isMultiGeometry):
    """initializes container list for Polygon Coordinates"""
    PolygonCoords = [] 

    """Adds input coordinates to container list"""
    for eachCoord in inputSet:
        PolygonCoords.append(CoordinateToString(eachCoord, isMultiGeometry))

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

def wrapKMLObject(unwrappedObject):
    placemarkObject = KML.Placemark(unwrappedObject)
    wrappedObject = KML.kml(placemarkObject)    
    return wrappedObject

def displayKMLObject(KMLObject):
    wrappedObject = wrapKMLObject(KMLObject)
    displayableKMLObject = etree.tostring(wrappedObject, pretty_print = True).decode("utf-8")
    return displayableKMLObject

def CoordinateSetstoPolygons(inputCoordinateTuples, isMultiGeometry):
    Polygons = []
    for coordTuple in inputCoordinateTuples:
        Polygons.append(setToKMLPolygon(coordTuple, isMultiGeometry))
    return Polygons

def polygonsToMultiGeometry(inputPolygons):
    multigeometry = KML.MultiGeometry()
    for polygon in inputPolygons:
        multigeometry.append(polygon)
    return multigeometry

    
