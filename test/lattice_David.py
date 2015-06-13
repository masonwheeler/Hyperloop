import math

import config
import util
import baselattice
import proj
import transform       
import cost_David

def project_bounds(bounds, startLatLng, endLatLng):
    #print("In latitude and longitude the bounds are: ")
    #print(bounds)
    startLonLat = util.swap_pair(startLatLng)
    endLonLat = util.swap_pair(endLatLng)
    swappedBounds = util.swap_pairs(bounds)
    print("We are using the Oblique Mercator Projection.")
    config.proj = proj.omerc_proj(startLonLat,endLonLat)
    boundsXY = proj.lonlats_to_xys(swappedBounds,config.proj)
    #print("In geospatial coordinates the bounds are: ")
    #print(boundsXY)
    startXY = proj.lonlat_to_xy(startLonLat,config.proj)
    print("In geospatial coordinates the start is: " + str(startXY) + ".")
    endXY = proj.lonlat_to_xy(endLonLat,config.proj)
    print("In geospatial coordinates the end is: " + str(endXY) + ".")
    print("The distance between the start and end in meters is: " +
    str(util.norm(util.subtract(startXY,endXY))) + ".")
    return [boundsXY,startXY,endXY] 

def set_params(startXY,endXY):
    config.angle, config.sizeFactor, config.startVector \
    = transform.get_params(startXY,endXY)
    print("The angle we rotate clockwise by is: "
            + str(math.degrees(config.angle)) + ".")
    print("The size factor we scale by is: " + str(config.sizeFactor) + ".")
    print("The vector we translate by is: " + str(config.startVector) + ".")
    return [config.angle,config.sizeFactor,config.startVector]

def transform_bounds(boundsXY,startXY,endXY):    
    #print("The untransformed bounds are:")
    #print(boundsXY)
    transformedBounds = transform.transform_object(
            config.angle, config.sizeFactor, config.startVector, boundsXY)
    transformedStart = transform.transform_point(
            config.angle, config.sizeFactor, config.startVector, startXY)
    transformedEnd = transform.transform_point(
            config.angle, config.sizeFactor, config.startVector, endXY)
    #print(max([pair[0] for pair in transformedBounds]))
    #print(min([pair[0] for pair in transformedBounds]))
    #print("The transformed bounds are:")
    #print(transformedBounds)
    #print("The transformed start is: ")
    #print(transformedStart)
    #print("The transformed end is: ")
    #print(transformedEnd)    
    return transformedBounds

def base_lattice(boundingPolygon):
    print("We rescale so that distance between the start and end becomes "
            + str(config.baseScale) + ".")
    print("The initial vertical spacing between lattice points is "
            + str(config.latticeYSpacing) + ".")
    print("The horizontal spacing between lattice points is "
            + str(config.latticeXSpacing) + ".")
    print("Now building the base lattice")
    baseLattice, angles, ySpacing = baselattice.base_lattice(boundingPolygon,
            config.baseScale, config.latticeYSpacing, config.latticeXSpacing)
    print("Here is a sample lattice point:")
    print(baseLattice[0][0])
    print("Here are the angles:")
    print(angles)
    return [baseLattice, angles, ySpacing]

def attach_lnglats(baseLattice):
    print("Now attaching longitudes and latitudes to the lattice...")
    for eachSlice in baseLattice:
        for eachPoint in eachSlice:
            latticeXY = eachPoint[0]
            unTransformedPoint = transform.untransform_point(config.angle,
                    config.sizeFactor,config.startVector,latticeXY)
            eachPoint.append(unTransformedPoint)
            unProjectedPoint = proj.xy_to_lonlat(unTransformedPoint,
                    config.proj)
            eachPoint.append(unProjectedPoint)
    print("Completed attaching longitudes and latitudes.")
    print("Here is a sample Lattice point:")
    print(baseLattice[0][0])

    x0, y0 = transform.untransform_point(config.angle, config.sizeFactor,
            config.startVector, [0,0])
    x1, y1 = transform.untransform_point(config.angle, config.sizeFactor,
            config.startVector, [0,1])
    x2, y2 = transform.untransform_point(config.angle, config.sizeFactor,
            config.startVector, [1,0])
    xPrimVec = [x1 - x0, y1 - y0]
    yPrimVec = [x2 - x0, y2 - y0]
    print("Completed generating primitive vectors.")
    print("In the x-direction: " + str(xPrimVec))
    print("In the y-direction: " + str(yPrimVec))
    return [baseLattice, xPrimVec, yPrimVec]

def attach_cost(geotiff,lattice,directionsCoords,primVec):
    lattice = cost_David.attach_cost(geotiff,lattice,directionsCoords,primVec) 
    print("Completed attaching costs.")
    print("Here is a sample Lattice point:")
    print(lattice[0][0])
    return lattice
