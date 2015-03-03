import time
import math 
import random
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

t0 = time.time()
 
POLYGON = [[0,0], [0,1], [1,1], [1,0]] 
START = [0,0]
END = [1,1]

NDIGITS = 6
LATTICE_SIZE = 0.2

def round_nums(listOfNums):
    outputList = [round(value, NDIGITS) for value in listOfNums]
    return outputList    
    
def round_points(listOfPoints):
    outputList = [round_nums(point) for point in listOfPoints]
    return outputList

def get_distance(start, end):
    xDelta = end[0] - start[0]
    yDelta = end[1] - start[1]
    distance = math.sqrt(math.pow(xDelta,2) + math.pow(yDelta,2))
    return distance 
    
def get_angle(start, end):
    xDelta = end[0] - start[0]
    yDelta = end[1] - start[1]
    angleFromAxis = math.atan2(yDelta,xDelta)
    return angleFromAxis
    
def translate_point(start, point):
    translatedPoint = [point[i] - start[i] for i in range(0,len(start)) ] 
    return translatedPoint
    
def rotate_point(angle, point):
    originalX = point[0]
    originalY = point[1]
    rotatedX = originalX * math.cos(angle) + originalY * math.sin(-angle)
    rotatedY = originalX * math.sin(angle) + originalY * math.cos(angle)
    rotatedPoint = [rotatedX, rotatedY]
    return rotatedPoint
    
def scale_point(scaleFactor, point):
    scaledPoint = [point[0] / scaleFactor, point[1] / scaleFactor]    
    return scaledPoint

def transform_point(start, end, point):
    distance = get_distance(start, end)
    angle = get_angle(start, end)
    tPoint = translate_point(start, point)
    trPoint = rotate_point(-angle, tPoint)
    trsPoint = scale_point(distance, trPoint)
    trsPoint = round_nums(trsPoint)
    return trsPoint
    
def transform_polygon(start, end, polygon):
    transformedPolygon = [transform_point(start, end, point) for point in polygon]
    return transformedPolygon
    
def create_x_lattice():
    numPointsInLattice = int(1 / LATTICE_SIZE)
    xLattice = [ LATTICE_SIZE * i for i in range(1, numPointsInLattice) ]
    return xLattice
    
def create_edge_list(polygon):
    edgeList = [ [polygon[i], polygon[i+1]] for i in range(0, len(polygon) - 1)]
    edgeList.append([polygon[len(polygon) - 1], polygon[0]])
    return edgeList

def is_edge_relevant(edge, xValue):
    firstPointXValue = edge[0][0]
    secondPointXValue = edge[1][0]
    relevance = (((firstPointXValue <= xValue and xValue <= secondPointXValue ) or
                  (secondPointXValue <= xValue and xValue <= firstPointXValue )) and
                   firstPointXValue != secondPointXValue )                
    return relevance

def relevant_edges_for_xvalue(edgeList, xValue):
    relevantEdges = [edge for edge in edgeList if is_edge_relevant(edge, xValue)]
    return relevantEdges
    
def edge_to_slopeIntercept(edge):
    slope = ((edge[1][1] - edge[0][1]) / (edge[1][0] - edge[0][0]))
    intercept = edge[1][1] - slope*edge[1][0]
    slopeIntercept = [slope, intercept]
    return slopeIntercept

def get_intersections(relevantEdges, xValue):
    slopeInts = [edge_to_slopeIntercept(edge) for edge in relevantEdges]
    intersections = [slopeInt[0] * xValue + slopeInt[1] for slopeInt in slopeInts]
    return intersections
    
def get_maxANDmin(inputList):
    maxANDmin = [max(inputList), min(inputList)]
    return maxANDmin

def value_to_lattice(value, shiftUp):
    latticeSteps = value/LATTICE_SIZE
    truncatedLatticeSteps = int(value/LATTICE_SIZE)
    shiftedTruncatedLatticeSteps = truncatedLatticeSteps + shiftUp
    shiftedValue = shiftedTruncatedLatticeSteps * LATTICE_SIZE
    return shiftedValue

def onLattice(value):
    isOnLattice = (value_to_lattice(value,0) == value)
    return isOnLattice
    
def maxANDmin_to_lattice(maxANDmin):
    maxOnLattice = value_to_lattice(maxANDmin[0],0)
    if onLattice(maxANDmin[1]):
        minOnLattice = value_to_lattice(maxANDmin[1],0)
    else:
        minOnLattice = value_to_lattice(maxANDmin[1],1)
    maxANDminOnLattice = [ maxOnLattice, minOnLattice ]
    return maxANDminOnLattice
    
def build_lattice_slice(maxANDmin, xValue):
    maxim = maxANDmin[0]
    minim = maxANDmin[1]
    gap = maxANDmin[0] - maxANDmin[1]
    ySteps = int(round(gap/LATTICE_SIZE)) + 1
    latticeYSlice = [minim + (LATTICE_SIZE * i) for i in range(0, ySteps)]
    latticeSlice = [[xValue, yValue] for yValue in latticeYSlice]
    return latticeSlice
    
def generate_lattice(polygon):
    lattice = []
    xLattice = create_x_lattice()
    edgeList = create_edge_list(polygon)
    for xValue in xLattice:
        relevantEdges = relevant_edges_for_xvalue(edgeList, xValue)
        intersections = get_intersections(relevantEdges, xValue)
        intersections = round_nums(intersections)
        roughMaxAndMin = get_maxANDmin(intersections)
        maxANDmin = maxANDmin_to_lattice(roughMaxAndMin)
        RoughLatticeSlice = build_lattice_slice(maxANDmin, xValue)
        latticeSlice = round_points(RoughLatticeSlice)
        lattice.append(latticeSlice)
    return lattice

def lattice_to_plotLattice(lattice):
    xValues = []
    yValues = []
    for latticeSlice in lattice:
        for point in latticeSlice:
            xValues.append(point[0])
            yValues.append(point[1])
    return [xValues,yValues]

def lists_to_tuples(lists):
    tuples = [tuple(eachList) for eachList in lists]
    return tuples

def generate_random_path(lattice):
    path = [[0,0]]
    for latticeSlice in lattice:
        path.append(random.choice(latticeSlice))
    path.append([1,0])        
    return path

def create_codes(path):
    numEdges = len(path)
    codes = [Path.MOVETO]
    for edgeNum in range(1, numEdges):
        codes.append(Path.LINETO)
    return codes

transformedPolygon = transform_polygon(START, END, POLYGON)

matplotPolygon = lists_to_tuples(transformedPolygon)
plottablePolygon = patches.Polygon(matplotPolygon, closed = True)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.add_patch(plottablePolygon)
ax.set_xlim(-2,2)
ax.set_ylim(-2,2)

lattice = generate_lattice(transformedPolygon)
plotLattice = lattice_to_plotLattice(lattice)
xvals = plotLattice[0]
yvals = plotLattice[1]
plt.plot(xvals, yvals, 'ro')

vertices = lists_to_tuples(generate_random_path(lattice))
codes = create_codes(vertices)
path = Path(vertices, codes)
pathPatch = patches.PathPatch(path, lw=2)
ax.add_patch(pathPatch)

t1 = time.time()
totalTime = t1 - t0
print(totalTime)
plt.show()


