"""
Jonathan Ward 4/22/2015

This file contains the function definitions for creating the shapely 
multipolygon object corresponding to the polygonal bounding region.
"""

from shapely.ops import cascaded_union
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon
from shapely.geometry import Point

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