import config
import util
import math

def distance(start,end):
    return util.norm(util.subtract(start,end))

def angle(start,end):
    xDelta,yDelta = [end[i] - start[i] for i in range(0,2)]
    return math.atan2(yDelta,xDelta)

def rotate_point_ccw(angle, point):
    originalX, originalY = point
    rotatedX = originalX * math.cos(angle) + originalY * math.sin(-angle)
    rotatedY = originalX * math.sin(angle) + originalY * math.cos(angle)
    return [rotatedX,rotatedY]

def transform_point(angle, sizeFactor, startPoint, pointToTransform):
    pointWithStartAtOrigin = util.subtract(pointToTransform, startPoint)
    pointOnXAxis = rotate_point_ccw(-angle, pointWithStartAtOrigin)
    scaledPointOnXAxis = util.scale(sizeFactor, pointOnXAxis)
    return util.round_nums(scaledPointOnXAxis)

def untransform_point(angle, sizeFactor, startPoint, pointToUntransform):
    unscaledPoint = util.scale(1.0/float(sizeFactor), pointToUntransform)
    pointInOriginalAngle = rotate_point_ccw(angle, unscaledPoint)
    pointAtOriginalPosition = util.add(startPoint, pointInOriginalAngle)
    return util.round_nums(pointAtOriginalPosition)

def get_params(start,end):
    return [angle(start,end),config.baseScale/distance(start,end),start]

def transform_object(angle,sizeFactor,startVector,anObject):
    transformed = [transform_point(angle, sizeFactor, startVector, point)
            for point in anObject]
    return transformed

def untransform_object(angle,sizeFactor,startVector,anObject):
    untransformed = [untransform_point(angle, sizeFactor, startVector, point)
            for point in anObject]
    return untransformed


