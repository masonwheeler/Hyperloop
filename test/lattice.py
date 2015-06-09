import math

import config
import util
import baselattice
import proj
import transform       
import cost

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
            + str(config.sliceYSpacing) + ".")
    print("The horizontal spacing between lattice points is "
            + str(config.latticeXSpacing) + ".")
    print("Now building the base lattice")
    baseLattice, angles = baselattice.base_lattice(boundingPolygon,
            config.baseScale, config.sliceYSpacing, config.latticeXSpacing)
    print("Here is a sample lattice point:")
    print(baseLattice[0][0])
    print("Here are the angles:")
    print(angles)
    return [baseLattice, angles]

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
    return baseLattice

def attach_cost(geotiff,lattice,directionsCoords):
    lattice = cost.attach_cost(geotiff,lattice,directionsCoords) 
    print("Completed attaching costs.")
    print("Here is a sample Lattice point:")
    print(lattice[0][0])
    return lattice
