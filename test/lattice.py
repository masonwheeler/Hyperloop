import math

import config
import util
import baselattice
import proj
import transform       
import cost

def project_bounds(bounds, startLatLng, endLatLng):
    startLonLat = util.swap_pair(startLatLng)
    endLonLat = util.swap_pair(endLatLng)
    swappedBounds = util.swap_pairs(bounds)
    config.proj = proj.omerc_proj(startLonLat,endLonLat)
    boundsXY = proj.lonlats_to_xys(swappedBounds,config.proj)
    startXY = proj.lonlat_to_xy(startLonLat,config.proj)
    endXY = proj.lonlat_to_xy(endLonLat,config.proj)
    if config.verboseMode: 
        print("We are using the Oblique Mercator Projection.")
        print("In geospatial coordinates the start is: " + str(startXY) + ".")
        print("In geospatial coordinates the end is: " + str(endXY) + ".")
        print("The distance between the start and end in meters is: " +
        str(util.norm(util.subtract(startXY,endXY))) + ".")
    return [boundsXY,startXY,endXY] 

def set_params(startXY,endXY):
    config.angle, config.sizeFactor, config.startVector \
    = transform.get_params(startXY,endXY)
    if config.verboseMode:
        print("The angle we rotate clockwise by is: "
                + str(math.degrees(config.angle)) + ".")
        print("The size factor we scale by is: " + str(config.sizeFactor) + ".")
        print("The vector we translate by is: " + str(config.startVector) + ".")
    return [config.angle,config.sizeFactor,config.startVector]

def transform_bounds(boundsXY,startXY,endXY):    
    transformedBounds = transform.transform_object(
            config.angle, config.sizeFactor, config.startVector, boundsXY)
    transformedStart = transform.transform_point(
            config.angle, config.sizeFactor, config.startVector, startXY)
    transformedEnd = transform.transform_point(
            config.angle, config.sizeFactor, config.startVector, endXY)
    if config.verboseMode:
        print("The transformed start is: ")
        print(transformedStart)
        print("The transformed end is: ")
        print(transformedEnd)    
    return transformedBounds

def base_lattice(boundingPolygon):
    baseLattice, envelope = baselattice.base_lattice(boundingPolygon, 
        config.baseScale, config.latticeYSpacing, config.latticeXSpacing)
    if config.verboseMode:
        print("We rescale so that distance between the start and end becomes "
                + str(config.baseScale) + ".")
        print("The initial vertical spacing between lattice points is "
                + str(config.latticeYSpacing) + ".")
        print("The horizontal spacing between lattice points is "
                + str(config.latticeXSpacing) + ".")
        print("Here is a sample lattice point:")
        baseLattice[0][0].display()
    return [baseLattice, envelope]

def attach_lnglats(lattice):
    for eachSlice in lattice:
        for eachPoint in eachSlice:
            latticeCoords = eachPoint.latticeCoords
            xyCoords = transform.untransform_point(config.angle,
                    config.sizeFactor,config.startVector,latticeCoords)
            eachPoint.xyCoords = xyCoords
            lonlatCoords = proj.xy_to_lonlat(xyCoords,config.proj)
            latlngCoords = util.swap_pair(lonlatCoords)
            eachPoint.latlngCoords = latlngCoords
    if config.verboseMode:
        print("Here is a sample Lattice point:")
        lattice[0][0].display()
    return lattice

def distance_from_rightofway(point, xyDirectionsCoords):
    distances = [proj.xy_distance(point.xyCoords, xyCoord) for xyCoord in 
                 xyDirectionsCoords]
    distance = min(distances)
    return distance

def add_rightOfWay(lattice, directionsCoords):
    lonlatDirectionsCoords = util.swap_pairs(directionsCoords)
    xyDirectionsCoords = proj.lonlats_to_xys(lonlatDirectionsCoords,config.proj)
    for eachSlice in lattice:
        for eachPoint in eachSlice:
            eachPoint.distanceFromRightOfWay = distance_from_rightofway(
                                               eachPoint, xyDirectionsCoords)
        sortedSlice = sorted(eachSlice,
                      key = lambda point : point.distanceFromRightOfWay)
        closestPoint = sortedSlice[0]
        closestPoint.inRightOfWay = True
    return lattice


