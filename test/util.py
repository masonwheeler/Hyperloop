"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a suite of utility function for the algorithm.
Last Modified: 7/17/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Clarify function usage.
"""

#Standard Modules
import sys
import math
import itertools
import operator
from collections import OrderedDict

#Our Modules
import config

#Used by: core.py
def get_firstlast(inList):
    return [inList[0], inList[-1]]

#Used by: directions.py
def round_num(num):
    return round(num, config.ndigits)

def round_nums(nums):
    return [round_num(num) for num in nums]

def round_points(points):
    return [round_nums(point) for point in points]

#Used by: proj.py
def swap_pair(pair):
    return [pair[1], pair[0]]

def swap_pairs(pairs):
    return [swap_pair(pair) for pair in pairs]

#Used by: edges.py
def fast_concat(listOfLists):
    concatenated = itertools.chain.from_iterable(listOfLists)
    return list(concatenated)

def list_of_lists_len(listOfLists):
    return sum(map(len,listOfLists))

#Used by: directions.py
def remove_duplicates(inList):
    return list(OrderedDict.fromkeys(list(itertools.chain(*inList))))

#Used by: routes.py
def smart_concat(listA,listB):
    newList = listA + listB[1:]
    return newList

#def operation_on_pieces(operation,pieceSize,inList):
#    pieces=[inList[index:index+pieceSize] for index in xrange(0,len(inList),pieceSize)]
#    resultPieces = map(operation,pieces)
#    result = fast_concat(resultPieces)
#    return result

def safe_operation(operation,vectorA,vectorB):
    if len(vectorA) == len(vectorB):
        return map(operation,vectorA,vectorB)
    else:
        print("Mismatched vector lengths.")
        print(vectorA)
        print(vectorB)
        sys.exit()
        return None

def add(vectorA,vectorB):
    return safe_operation(operator.add,vectorA,vectorB)

def subtract(vectorA,vectorB):
    return safe_operation(operator.sub,vectorA,vectorB)

def scale(scalar,vector):
    return [element * scalar for element in vector]

def norm(vector):
    return math.sqrt(sum(map(lambda x: x**2, vector)))

def entry_multiply(vectorA,vectorB):
    return safe_operation(operator.mul,vectorA,vectorB)


def to_pairs(points):
    pairs = []
    for index in range(len(points) - 1):
        pair = [points[index], points[index+1]]
        pairs.append(pair)
    return pairs

def get_indices(inList):
    return sorted(range(len(inList)), key = lambda k: inList[k], reverse=True)

def fix_inputString(inputString):
    titleString = inputString.title()
    return titleString.replace(" ","_")

def edge_to_vector(edge):
    edgeStart, edgeEnd = edge
    edgeVector = subtract(edgeEnd, edgeStart)
    return edgeVector

def distance_to_point(edge, distance):    
    edgeStart, edgeEnd = edge               
    edgeVector = subtract(edgeEnd, edgeStart)
    edgeLength = norm(edgeVector)
    scaleFactor = distance / edgeLength
    scaledVector = scale(scaleFactor, edgeVector)
    point = add(scaledVector, edgeStart)
    return point

def sample_vectorinterior(vector, spacing):
    if norm(vector) < spacing:
        return None
    else:
        effectiveScale = norm(vector) / spacing
        unitVector = scale(1.0 / effectiveScale, vector)
        numPoints = int(effectiveScale)
        pointIndices = range(0, numPoints)
        pointVectors = [scale(index, unitVector) for index in pointIndices]
        return pointVectors

def build_grid(vector, spacing, startVector):
    untranslatedGrid = sample_vectorinterior(vector, spacing)
    if untranslatedGrid == None:
        return None
    else:
        grid = [add(point, startVector) for point in untranslatedGrid]
        return grid

def smart_print(string):
    if config.verboseMode:
        print(string)     


