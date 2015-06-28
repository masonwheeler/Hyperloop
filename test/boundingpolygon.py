import time

import config
import groupcoords
import mergepolygons
import cacher

def bounding_polygon(directionsCoords):    
    coordGroups = groupcoords.group_coords(directionsCoords, config.groupSize)
    t0 = time.clock()
    polygon = mergepolygons.merge_coordgroups(coordGroups,
      config.polygonMergeChunkSize, config.tolerance, config.maxAttempts)
    t1 = time.clock()
    if config.verboseMode:
        print("There are " + str(len(coordinatesList)) +
              " coordinates in the directions.")
        print("Using polygons with " + str(groupSize) + " edges there are "
              + str(len(coordGroups)) + " polygons in total.")
        print("Merging polygons...")
        print("The boundary polygon has " + str(len(polygon)) + " sides.")
    if config.timingMode:
        print("Merging the polygons took: " + str(t1-t0) + " seconds.")
    return polygon

def get_boundingpolygon(directions):
    boundingPolygon = cacher.get_object("boundingpolygon", bounding_polygon,
               [directions], cacher.save_listlike, config.boundingPolygonFlag)
    return boundingPolygon
