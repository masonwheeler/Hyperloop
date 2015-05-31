import config

import math
import sys
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.ops import cascaded_union

def partition_to_polygon(partition):
    return Polygon(partition)

def partitions_to_polygons(partitions):
    return [partition_to_polygon(partition) for partition in partitions]

def validate_polygons(polygons):
    return all([polygon.is_valid for polygon in polygons])

def repair_polygons(polygons,tolerance):
    return [polygon.buffer(tolerance) for polygon in polygons]

def repair_multipolygon(multipolygon,tolerance):
    polygons = multipolygon.geoms
    repairedPolygons = repairPolygon(polygons,tolerance)
    return MultiPolygon(repairedPolygons)

def repeatedRepair_polygons(polygons,tolerance):
    while not validate_polygons(polygons):
        tolerance *= 10
        polygons = repair_polygons(polygons,tolerance)
    return polygons

def union_multiPolygon(polygonalObject,tolerance,maxAttempts):    
    attemptNum = 0
    while(polygonalObject.geom_type=="MultiPolygon" and attemptNum < maxAttempts):
        attemptNum += 1
        repairedObjects = repair_polygons(polygonalObject.geoms,tolerance)
        polygonalObject = cascaded_union(repairedObjects)
        tolerance *= 10
    if polygonalObject.geom_type=="MultiPolygon":
        print('Failed to fuse polygons:')
        print(polygonalObject)
        print('with buffer: ')
        print(tolerance)
        print('Were the polygons were valid? ')
        print(validate_polygons(polygonalObject.geoms))        
        sys.exit()
        return 0
    else:
        return polygonalObject

#merges list of polygons into a polygon
def polygons_to_polygon(polygons,tolerance,maxAttempts):
    repairedPolygons = repeatedRepair_polygons(polygons,tolerance)
    polygonalObject = cascaded_union(repairedPolygons)
    return union_multiPolygon(polygonalObject,tolerance,maxAttempts)

#
def partition_list(inList, partitionSize):
    partitions = []
    for index in range(0, len(inList), partitionSize):
        lenLeft = len(inList) - index
        partitionLen = min(partitionSize,lenLeft)
        partitions.append(inList[index:index + partitionLen])
    return partitions

#splits polygons into partitions and then merges those partitions
def union_partitions(polygons, partitionSize, tolerance, maxAttempts):
    numPolygons = len(polygons)
    numPolygonPartitions = math.ceil(float(numPolygons)/float(partitionSize))
    polygonSets = partition_list(polygons,partitionSize)
    return [polygons_to_polygon(polygons,tolerance,maxAttempts) for polygons in polygonSets]

#Recursively merges sets of groupSize
def recursive_union(polygons, groupSize, tolerance, maxAttempts):
    while (len(polygons) > 1):    
        polygons = union_partitions(polygons, groupSize, tolerance, maxAttempts)
    return polygons[0]

def tuples_to_lists(tuples):
    return [list(eachTuple) for eachTuple in tuples]

def get_polygonPoints(polygon):
    tuples = list(polygon.exterior.coords)
    return tuples_to_lists(tuples)

def simplifyPolygon(polygon):
    return polygon.simplify(config.tolerance, preserve_topology=True)

def bufferFinalPolygon(polygon):
    return polygon.buffer(config.finalBuffer)

def merge_partitions(partitions, groupSize, tolerance, maxAttempts):
    polygons = partitions_to_polygons(partitions)
    mergedPolygon = recursive_union(polygons, groupSize, tolerance, maxAttempts)
    simplifiedPolygon = simplifyPolygon(mergedPolygon)
    bufferedPolygon = bufferFinalPolygon(simplifiedPolygon)
    return get_polygonPoints(bufferedPolygon)
