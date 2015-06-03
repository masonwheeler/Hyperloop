import math
import sys
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.ops import cascaded_union

import config

def coordsgroup_to_polygon(coordsgroup):
    return Polygon(coordsgroup)

def coordsgroups_to_polygons(coordsgroups):
    polygons = [
            coordsgroup_to_polygon(coordsgroup) for coordsgroup in coordsgroups]
    return polygons

def validate_polygons(polygons):
    return all([polygon.is_valid for polygon in polygons])

def repair_polygons(polygons,tolerance):
    return [polygon.buffer(tolerance) for polygon in polygons]

def repair_multipolygon(multipolygon,tolerance):
    polygons = multipolygon.geoms
    repairedPolygons = repair_polygons(polygons,tolerance)
    return MultiPolygon(repairedPolygons)

def repeatedrepair_polygons(polygons,tolerance):
    while not validate_polygons(polygons):
        tolerance *= 10
        polygons = repair_polygons(polygons,tolerance)
    return polygons

def union_multipolygon(polygonalObject,tolerance,maxAttempts):    
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
    repairedPolygons = repeatedrepair_polygons(polygons,tolerance)
    polygonalObject = cascaded_union(repairedPolygons)
    return union_multipolygon(polygonalObject,tolerance,maxAttempts)

def partition_list(inList, partitionSize):
    partitions = []
    for index in range(0, len(inList), partitionSize):
        lenLeft = len(inList) - index
        partitionLen = min(partitionSize,lenLeft)
        partitions.append(inList[index:index + partitionLen])
    return partitions

#splits polygons into partitions and then merges those partitions
def union_polygonpartitions(polygons, partitionSize, tolerance, maxAttempts):
    numPolygons = len(polygons)
    numPolygonPartitions = math.ceil(float(numPolygons)/float(partitionSize))
    polygonSets = partition_list(polygons,partitionSize)
    return [polygons_to_polygon(polygons,tolerance,maxAttempts) for polygons in polygonSets]

#Recursively merges partitions of partitionSize
def recursive_union(polygons, partitionSize, tolerance, maxAttempts):
    while (len(polygons) > 1):    
        polygons = union_polygonpartitions(polygons, partitionSize, tolerance,
                maxAttempts)
    return polygons[0]

def tuples_to_lists(tuples):
    return [list(eachTuple) for eachTuple in tuples]

def polygon_points(polygon):
    tuples = list(polygon.exterior.coords)
    return tuples_to_lists(tuples)

def simplify_polygon(polygon):
    return polygon.simplify(config.tolerance, preserve_topology=True)

def buffer_finalpolygon(polygon):
    return polygon.buffer(config.finalBuffer)

def merge_coordgroups(coordsGroups, partitionSize, tolerance, maxAttempts):
    polygons = coordsgroups_to_polygons(coordsGroups)
    mergedPolygon = recursive_union(polygons, partitionSize, tolerance,
            maxAttempts)
    simplifiedPolygon = simplify_polygon(mergedPolygon)
    bufferedPolygon = buffer_finalpolygon(simplifiedPolygon)
    return polygon_points(bufferedPolygon)





















