import time

import config
import directions
import groupcoords
import mergepolygons

groupSize = config.groupSize
polygonMergeChunkSize = config.polygonMergeChunkSize
tolerance = config.tolerance
maxAttempts = config.maxAttempts

def bounding_polygon(origin,destination):
    t0 = time.clock()
    config.coordinatesList = directions.coordinate_list(origin,destination)
    coordinatesList = config.coordinatesList
    t1 = time.clock()
    print("Getting the coordinates took: " + str(t1-t0) + " seconds.")
    print("There are " + str(len(coordinatesList)) +
            " coordinates in the directions.")
    startLatLng = coordinatesList[0]
    endLatLng = coordinatesList[-1]
    print("The coordinates of the start are: " + str(startLatLng) +
            ". The coordinates of the end are: " + str(endLatLng) + ".")
    coordGroups = groupcoords.group_coords(coordinatesList,groupSize)
    print("Using polygons with " + str(groupSize) + " edges there are "
            + str(len(coordGroups)) + " polygons in total.")
    print("Merging polygons...")
    t2 = time.clock()
    polygon = mergepolygons.merge_coordgroups(coordGroups,
            polygonMergeChunkSize, tolerance, maxAttempts)
    t3 = time.clock()
    print("Merging the polygons took: " + str(t3-t2) + " seconds.")
    print("The boundary polygon has " + str(len(polygon)) + " sides.")
    return [polygon,startLatLng,endLatLng]

