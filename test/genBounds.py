import config
import proj
import directionsCoords
import coordsToPartitions
import partitionsToPolygon

import time

partitionLength = config.partitionLength
mergeGroupSize = config.mergeGroupSize
tolerance = config.tolerance
maxAttempts = config.maxAttempts

def genBoundingPolygon(origin,destination):
    t0 = time.clock()
    coordinatesList = directionsCoords.get_coordinateList(origin,destination)
    t1 = time.clock()
    print("Getting the coordinates took: " + str(t1-t0) + " seconds.")
    print("There are " + str(len(coordinatesList)) + " coordinates in the directions.")
    startLatLng = coordinatesList[0]
    endLatLng = coordinatesList[-1]
    print("The coordinates of the start are: " + str(startLatLng) + ". The coordinates of the end are: " + str(endLatLng) + ".")
    partitions = coordsToPartitions.coords_to_partitions(coordinatesList,partitionLength)
    print("Using polygons with " + str(partitionLength) + " edges there are " + str(len(partitions)) + " polygons in total.")
    print("Merging polygons...")
    t2 = time.clock()
    polygon = partitionsToPolygon.merge_partitions(partitions, mergeGroupSize, tolerance, maxAttempts)
    t3 = time.clock()
    print("Merging the polygons took: " + str(t3-t2) + " seconds.")
    print("The boundary polygon has " + str(len(polygon)) + " sides.")
    return [polygon,startLatLng,endLatLng]

