import config
import math

def scale_point(point, scaleFactor):
    return [value * scaleFactor for value in point]
    
def scale_points(points, scaleFactor):
    return [scale_point(point,scaleFactor) for point in points]

def round_nums(nums,ndigits):
    return [round(val,ndigits) for val in nums]

def round_points(points,ndigits):
    return [round_nums(point,ndigits) for point in points]

def get_distance(start,end):
    return math.sqrt( sum( [math.pow(end[i] - start[i],2) for i in range(0,2)] ) )

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

def transform_point (angle, scale, start, pointToTransform, ndigits):
    pointWithStartAtOrigin = subtract_startVector(start,pointToTransform)
    pointOnXAxis = rotate_pointCCW(-angle, pointWithStartAtOrigin)
    scaledPointOnXAxis = scale_point(pointOnXAxis, scale)
    return round_nums(scaledPointOnXAxis,ndigits)

def inverseTransform_point(angle, scale, start, pointToUntransform, ndigits):
    unscaledPoint = scale_point(pointOnXAxis, 1.0/float(scale))
    pointInOriginalAngle = rotate_pointCCW(angle, unscaledPoint)
    pointAtOriginalPosition = subtract_startVector(start, pointInOriginalAngle)
    return round_nums(pointAtOriginalPosition, ndigits)

