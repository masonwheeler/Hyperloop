"""
Jonathan Ward 3/18/2015

This file contains the function definitions for creating the shapely 
multipolygon object corresponding to the polygonal bounding region.
"""

from shapely.ops import cascaded_union
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon
from shapely.geometry import Point

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
