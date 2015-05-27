import config

def scale_point(point, scaleFactor):
    return [value * scaleFactor for value in point]
    
def scale_points(points, scaleFactor):
    return [scale_point(point,scaleFactor) for point in points]
