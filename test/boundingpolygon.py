import time

import config
import groupcoords
import mergepolygons
import cacher

def bounding_polygon(directionsCoords):    
    #t0 = time.clock()
    #config.directionsCoords = directions.get_directions(start, end)  
    #t1 = time.clock()
    #startLatLng = config.directionsCoords[0]
    #endLatLng = config.directionsCoords[-1]
    coordGroups = groupcoords.group_coords(directionsCoords, config.groupSize)
    t2 = time.clock()
    polygon = mergepolygons.merge_coordgroups(coordGroups,
      config.polygonMergeChunkSize, config.tolerance, config.maxAttempts)
    t3 = time.clock()
    if config.verboseMode:
        print("There are " + str(len(coordinatesList)) +
              " coordinates in the directions.")
        print("Using polygons with " + str(groupSize) + " edges there are "
              + str(len(coordGroups)) + " polygons in total.")
        print("Merging polygons...")
        print("The boundary polygon has " + str(len(polygon)) + " sides.")
    if config.timingMode:
        print("Getting the coordinates took: " + str(t1-t0) + " seconds.")
        print("Merging the polygons took: " + str(t3-t2) + " seconds.")
    return polygon

def get_boundingpolygon(directions):
    boundingPolygon = cacher.get_object("boundingpolygon", bounding_polygon,
                      [directions], cacher.save_listlike)
    return boundingPolygon
