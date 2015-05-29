import config
import proj
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

def genBoundingPolygon(origin,destination):
    coordinatesList = directionsCoords.get_coordinateList(origin,destination)
    print("There are " + str(len(coordinatesList)) + " coordinates in the directions.")
    startLatLng = coordinatesList[0]
    endLatLng = coordinatesList[-1]
    print("The coordinates of the start are: " + str(startLatLng) + ". The coordinates of the end are: " + str(endLatLng))
    partitions = coordsToPartitions.partition_list(coordinatesList,partitionLength)
    print("Using polygons with " + str(partitionLength) + " edges there are " + str(len(partitions)) + " polygons in total")
    polygon = partitionsToPolygon.merge_partitions(partitions, mergeGroupSize, tolerance, maxAttempts)
    print("The boundary polygon has " + str(len(polygon)) + " sides")
    return [polygon,startLatLng,endLatLng]

