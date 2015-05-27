import config
import shapely

def partition_to_polygon(partition):
    return shapely.geometry.Polygon(partition)

def partitions_to_polygons(partitions):
    return [partition_to_polygon(polygon) for polygon in polygons]

def validate_polygons(polygons):
    return all([polygon.is_valid for polygon in shapelyPolygons])

def repair_polygons(polygons,tolerance):
    return [polygon.buffer(tolerance) for polygon in polygons]

def repair_multipolygon(multipolygon,tolerance):
    polygons = multipolygon.geoms
    repairedPolygons = repairPolygon(polygons,tolerance)
    return shapely.geometry.MultiPolygon(repairedPolygons)

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
        polygonalObject = shapely.ops.cascaded_union(repairedObjects)
        tolerance *= 10
    if testPolygon.geom_type=="MultiPolygon":
        print('Failed to fuse polygons:')
        print(testPoly)
        print('with buffer: ')
        print(currentTolerance)
        print('The polygons were valid: ')
        print(validate_shapelyPolygons(testPolygon.geoms))
        polygon = None
        sys.exit()
        return 0
    else:
        return polygon

def polygons_to_polygon(polygons,tolerance,maxAttempts):
    repairedPolygons = repeatedRepair_polygons(polygon,tolerance)
    polygonalObject = shapely.ops.cascaded_union(repairedPolygons)
    return union_multiPolygon(polygonalObject)

def partition_list(inList, partitionSize):
    partitions = []
    for index in range(0, len(alist), partitionSize):
        lenLeft = len(inList) - index
        partitionLen = min(partitionSize,lenLeft)
        partitions.append(inList[index:index + partitionLen])
    return partitions

def union_partitions(polygons, partitionSize, tolerance, maxAttempts):
    numPolygons = len(polygons)
    numPolygonPartitions = math.ceil(float(numPolygons)/float(partitionSize))
    polygonSets = partition_list(polygons,partitionSize)
    return [polygons_to_polygon(polygons,tolerance,maxAttempts) for polygons in polygonSets]

def recursive_union(polygons, partitionSize, tolerance, maxAttempts):
    while (len(polygons) > 1):
        polygons = union_partitions(polygons, partitionSize, tolerance, maxAttempts)
    return polygons[0]

def tuples_to_lists(tuples):
    return [list(eachTuple) for eachTuple in tuples]

def get_polygonPoints(polygon):
    tuples = list(polygon.exterior.coords)
    return tuples_to_lists(tuples)
