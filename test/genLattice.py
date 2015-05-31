import config
import util
import genBaseLattice
import proj
import transform       
import cost

import math

def projectBounds(bounds, startLatLng, endLatLng):
    #print("In latitude and longitude the bounds are: ")
    #print(bounds)
    startLonLat = util.swapPair(startLatLng)
    endLonLat = util.swapPair(endLatLng)
    swappedBounds = util.swapPairs(bounds)
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
    config.angle, config.sizeFactor, config.startVector = transform.get_params(startXY,endXY)
    print("The angle we rotate clockwise by is: " + str(math.degrees(config.angle)) + ".")
    print("The size factor we scale by is: " + str(config.sizeFactor) + ".")
    print("The start vector we translate by is: " + str(config.startVector) + ".")
    return [config.angle,config.sizeFactor,config.startVector]

def transformBounds(boundsXY,startXY,endXY):    
    #print("The untransformed bounds are:")
    #print(boundsXY)
    transformedBounds = transform.transform_object(config.angle,config.sizeFactor,config.startVector,boundsXY)
    transformedStart = transform.transform_point(config.angle,config.sizeFactor,config.startVector,startXY)
    transformedEnd = transform.transform_point(config.angle,config.sizeFactor,config.startVector,endXY)
    #print(max([pair[0] for pair in transformedBounds]))
    #print(min([pair[0] for pair in transformedBounds]))
    #print("The transformed bounds are:")
    #print(transformedBounds)
    #print("The transformed start is: ")
    #print(transformedStart)
    #print("The transformed end is: ")
    #print(transformedEnd)    
    return transformedBounds

def gen_baseLattice(boundingPolygon):
    print("We rescale so that distance between the start and end becomes " + str(config.baseScale) + ".")
    print("The initial vertical spacing between lattice points (which shrinks if necessary) is " + str(config.sliceYSpacing) + ".")
    print("The horizontal spacing between lattice points (which remains constant) is " + str(config.latticeXSpacing) + ".")
    return genBaseLattice.gen_baseLattice(boundingPolygon,config.baseScale,config.sliceYSpacing,config.latticeXSpacing)

def attach_lngLat(baseLattice):
    print("Now attaching longitudes and latitudes to the lattice...")
    for xIndex in range(len(baseLattice)):
        for yIndex in range(len(baseLattice[xIndex])):
            pointData = baseLattice[xIndex][yIndex]
            xValue = xIndex * config.latticeXSpacing
            yValue = baseLattice[xIndex][yIndex][0]
            unTransformedPoint = transform.inverseTransform_point(config.angle,config.sizeFactor,config.startVector,[xValue,yValue])
            unProjectedPoint = proj.xy_to_lonlat(unTransformedPoint,config.proj)
            baseLattice[xIndex][yIndex].append(unProjectedPoint)
    print("Completed attaching longitudes and latitudes.")
    print("Here is a sample Lattice point:")
    print(baseLattice[0][0])
    return baseLattice

