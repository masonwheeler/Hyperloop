import math

import config
import util
import baselattice
import proj
import transform       
import cost
import cacher
import import_export as io

def set_projection(startLatLng, endLatLng):
    config.proj = proj.albers_proj()

def project_bounds(bounds):
    swappedBounds = util.swap_pairs(bounds)
    boundsXY = proj.lonlats_to_xys(swappedBounds,config.proj)
    if config.verboseMode: 
        print("We are using the Oblique Mercator Projection.")
        print("In geospatial coordinates the start is: " + str(startXY) + ".")
        print("In geospatial coordinates the end is: " + str(endXY) + ".")
        print("The distance between the start and end in meters is: " +
        str(util.norm(util.subtract(startXY,endXY))) + ".")
    return boundsXY

def get_boundsxy(bounds):
    boundsXY = cacher.get_object("boundsxy", project_bounds, [bounds], 
                                 cacher.save_listlike)
    return boundsXY
    

def project_startend(startLatLng, endLatLng):
    startLonLat, endLonLat = util.swap_pairs([startLatLng, endLatLng])
    startXY, endXY = proj.lonlats_to_xys([startLonLat, endLonLat], config.proj) 
    return [startXY, endXY]    

def set_params(startXY,endXY):
    config.angle, config.sizeFactor, config.startVector \
    = transform.get_params(startXY,endXY)
    if config.verboseMode:
        print("The angle we rotate clockwise by is: "
                + str(math.degrees(config.angle)) + ".")
        print("The size factor we scale by is: " + str(config.sizeFactor) + ".")
        print("The vector we translate by is: " + str(config.startVector) + ".")
    return [config.angle,config.sizeFactor,config.startVector]

def transform_bounds(boundsXY):    
    transformedBounds = transform.transform_object(
            config.angle, config.sizeFactor, config.startVector, boundsXY)
    return transformedBounds

def get_latticebounds(boundsXY):
    latticeBounds = cacher.get_object("latticebounds", transform_bounds,
                                     [boundsXY], cacher.save_listlike)
    return latticeBounds

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

def get_baselattice(boundingPolygon):
    baseLattice = cacher.get_object("baselattice", base_lattice,
                                    [boundingPolygon], cacher.save_baselattice)
    return baseLattice

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

def get_lnglatlattice(lattice):
    lnglatLattice = cacher.get_object("lnglatlattice", attach_lnglats,
                                      [lattice], cacher.save_lnglatlattice)
    return lnglatLattice

def distance_from_rightofway(point, xyDirectionsCoords):
    distances = [proj.xy_distance(point.xyCoords, xyCoord) for xyCoord in 
                 xyDirectionsCoords]
    distance = min(distances)
    return distance

def add_rightOfWay(lattice, directionsCoords):
    lonlatDirectionsCoords = util.swap_pairs(directionsCoords)
    xyDirectionsCoords = proj.lonlats_to_xys(lonlatDirectionsCoords,config.proj)
    RightOfWay = [[]]
    for eachSlice in lattice:
        for eachPoint in eachSlice:
            eachPoint.distanceFromRightOfWay = distance_from_rightofway(
                                               eachPoint, xyDirectionsCoords)
        sortedSlice = sorted(eachSlice,
                      key = lambda point : point.distanceFromRightOfWay)
        closestPoint = sortedSlice[0]
        closestPoint.inRightOfWay = True
        RightOfWay += [closestPoint]
    #RightOfWay.pop(0)
    #data = [point.xyCoords for point in RightOfWay]
    #print "exporting highway..."
    #io.export(data, 'highway')
    return lattice

def get_rightofway(lattice, directionsCoords):
    rightofwayLattice = cacher.get_object("rightofwaylattice", add_rightOfWay,
                     [lattice, directionsCoords], cacher.save_rightofwaylattice)
    return rightofwayLattice

