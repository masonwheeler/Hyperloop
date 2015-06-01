import config
import util
import math

def scale_point(point,sizeFactor):
    return [value * sizeFactor for value in point]
    
def scale_points(points,sizeFactor):
    return [scale_point(point,sizeFactor) for point in points]

def get_distance(start,end):
    return math.sqrt( sum( [math.pow(end[i] - start[i],2) for i in range(2)] ) )

def get_angle(start,end):
    xDelta,yDelta = [end[i] - start[i] for i in range(0,2)]
    return math.atan2(yDelta,xDelta)

def subtract_startVector(start, pointToTranslate):
    return [pointToTranslate[i] - start[i] for i in range(0,2)]

def add_startVector(start, pointToTranslate):
    return [pointToTranslate[i] + start[i] for i in range(0,2)]

def rotate_pointCCW(angle,point):
    originalX, originalY = point
    rotatedX = originalX * math.cos(angle) + originalY * math.sin(-angle)
    rotatedY = originalX * math.sin(angle) + originalY * math.cos(angle)
    return [rotatedX,rotatedY]

def transform_point(angle,sizeFactor,startVector,pointToTransform):
    pointWithStartAtOrigin = subtract_startVector(startVector,pointToTransform)
    pointOnXAxis = rotate_pointCCW(-angle, pointWithStartAtOrigin)
    scaledPointOnXAxis = scale_point(pointOnXAxis,sizeFactor)
    return util.round_nums(scaledPointOnXAxis)

def inverseTransform_point(angle,sizeFactor,start,pointToUntransform):
    unscaledPoint = scale_point(pointToUntransform, 1.0/float(sizeFactor))
    pointInOriginalAngle = rotate_pointCCW(angle, unscaledPoint)
    pointAtOriginalPosition = subtract_startVector(start, pointInOriginalAngle)
    return util.round_nums(pointAtOriginalPosition)

def get_params(start,end):
    return [get_angle(start,end),config.baseScale/get_distance(start,end),start]

def transform_object(angle,sizeFactor,startVector,anObject):
    return [transform_point(angle,sizeFactor,startVector,point) for point in anObject]

def inverseTransform_object(angle,sizeFactor,startVector,anObject):
    return [inverseTransform_point(angle,sizeFactor,startVector,point) for point in anObject]


