import config
import directionsCoords
import coordsToPartitions
import partitionsToPolygon

global partitionLength
global mergeGroupSize
global tolerance
global maxAttempts

partitionLength = config.partitionLength
mergeGroupSize = config.mergeGroupSize
tolerance = config.tolerance
maxAttempts = config.maxAttempts

def generatePolygonalRegion(origin,destination):
    coordinatesList = directionsCoords.get_coordinateList(origin,destination)
    print("There are " + str(len(coordinatesList)) + " coordinates in the directions.")
    partitions = coordsToPartitions.partition_list(coordinatesList,partitionLength)
    print("Using polygons with " + str(partitionLength) + " edges there are " + str(len(partitions)) + " polygons in total")
    polygon = partitionsToPolygon.merge_partitions(partitions, mergeGroupSize, tolerance, maxAttempts)
    print("The boundary polygon has " + str(len(polygon)) + " sides")
    return polygon
