import config
import proj
import directionsCoords
import coordsToPartitions
import partitionsToPolygon

import time

groupSize = config.groupSize
polygonMergeChunkSize = config.polygonMergeChunkSize
tolerance = config.tolerance
maxAttempts = config.maxAttempts

def genBoundingPolygon(origin,destination):
    t0 = time.clock()
    coordinatesList = getDirectionsCoords.get_coordinateList(origin,destination)
    t1 = time.clock()
    print("Getting the coordinates took: " + str(t1-t0) + " seconds.")
    print("There are " + str(len(coordinatesList)) + " coordinates in the directions.")
    startLatLng = coordinatesList[0]
    endLatLng = coordinatesList[-1]
    print("The coordinates of the start are: " + str(startLatLng) + ". The coordinates of the end are: " + str(endLatLng) + ".")
    groups = coordsToGroups.coords_to_groups(coordinatesList,groupSize)
    print("Using polygons with " + str(groupSize) + " edges there are " + str(len(groups)) + " polygons in total.")
    print("Merging polygons...")
    t2 = time.clock()
    polygon = coordGroupsToPolygon.merge_polygons(coordGroups, polygonMergeChunks, tolerance, maxAttempts)
    t3 = time.clock()
    print("Merging the polygons took: " + str(t3-t2) + " seconds.")
    print("The boundary polygon has " + str(len(polygon)) + " sides.")
    return [polygon,startLatLng,endLatLng]

