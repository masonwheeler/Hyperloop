import time

import config
import directions
import groupcoords
import mergepolygons
import cacher

def bounding_polygon(origin,destination):    
    t0 = time.clock()
    config.directionsCoords = directions.coordinate_list(origin,destination)  
    t1 = time.clock()
    startLatLng = coordinatesList[0]
    endLatLng = coordinatesList[-1]
    coordGroups = groupcoords.group_coords(config.directionsCoords,
                  config.groupSize)
    t2 = time.clock()
    polygon = mergepolygons.merge_coordgroups(coordGroups,
      config.polygonMergeChunkSize, config.tolerance, config.maxAttempts)
    t3 = time.clock()
    if config.verboseMode:
        print("There are " + str(len(coordinatesList)) +
              " coordinates in the directions.")
        print("The coordinates of the start are: " + str(startLatLng) + ".")
        print("The coordinates of the end are: " + str(endLatLng) + ".")
        print("Using polygons with " + str(groupSize) + " edges there are "
              + str(len(coordGroups)) + " polygons in total.")
        print("Merging polygons...")
        print("The boundary polygon has " + str(len(polygon)) + " sides.")
    if config.timingMode:
        print("Getting the coordinates took: " + str(t1-t0) + " seconds.")
        print("Merging the polygons took: " + str(t3-t2) + " seconds.")
    return [polygon,startLatLng,endLatLng]
