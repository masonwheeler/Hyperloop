"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a suite of utility function for the algorithm.
Last Modified: 7/30/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Organized functions by usage.
"""

#Standard Modules
import sys
import math
import itertools
import operator
from collections import OrderedDict
import numpy as np

#Our Modules
import config


#Points Operations:

def round_num(num):
    return round(num, config.ndigits)

def round_nums(nums):
    return [round_num(num) for num in nums]

def round_points(points):
    """Used in directions.build_directions()"""
    return [round_nums(point) for point in points]

def to_pairs(points):
    pairs = []
    for index in range(len(points) - 1):
        pair = [points[index], points[index+1]]
        pairs.append(pair)
    return pairs

def distance_to_point(edge, distance):            
   edgeStart, edgeEnd = edge                       
   edgeVector = subtract(edgeEnd, edgeStart)        
   edgeLength = norm(edgeVector)        
   scaleFactor = distance / edgeLength        
   scaledVector = scale(scaleFactor, edgeVector)        
   point = add(scaledVector, edgeStart)        
   return point



#Pair Operations:

def swap_pair(pair):
    return [pair[1], pair[0]]

def swap_pairs(pairs):
    """Used in proj.py"""
    return [swap_pair(pair) for pair in pairs]


#List Operations:

def get_firstlast(inList):
    """Used in core.get_directions()"""
    return [inList[0], inList[-1]]

def get_maxmin(inList):
    """Used for testing"""
    return [max(inList), min(inList)]

def list_mean(inList):
    """Used in genVelocity.py"""
    mean = sum(inList)/float(len(inList))
    return mean

def remove_duplicates(inList):
    """Used in directions.py"""
    return list(OrderedDict.fromkeys(list(itertools.chain(*inList))))


#List of Lists Operations:

def fast_concat(listOfLists):
    """Used in edges.py"""
    concatenated = itertools.chain.from_iterable(listOfLists)
    return list(concatenated)

def list_of_lists_len(listOfLists):
    """Used for testing"""
    return sum(map(len,listOfLists))


#List Pair Operations:

def smart_concat(listA,listB):
    """Used in graphs.py"""
    newList = listA + listB[1:]
    return newList


#Vector Operations:

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

def entry_multiply(vectorA,vectorB):
    return safe_operation(operator.mul,vectorA,vectorB)

def scale(scalar,vector):
    return [element * scalar for element in vector]

def norm(vector):
    return math.sqrt(sum(map(lambda x: x**2, vector)))

def vector_to_angle(vector):
    xVal, yVal = vector
    angle = math.degrees(math.atan2(yVal, xVal))
    return angle    

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

#Edge Operations:

def edge_to_vector(edge):
    edgeStart, edgeEnd = edge
    edgeVector = subtract(edgeEnd, edgeStart)
    return edgeVector

#String Operations:

def fix_inputString(inputString):
    titleString = inputString.title()
    return titleString.replace(" ","_")

def smart_print(string):
    if config.verboseMode:
        print(string)     

#Other Operations:

def interval_to_value(inputVal, upperboundOutputValPairs, elseVal):
    for upperboundOutputValPair in upperboundOutputValPairs:
        upperbound, outputVal = upperboundOutputValPair
        if inputVal < upperbound:
            return outputVal
    return elseVal

def placeIndexinList(index, orderedList_of_integers):
    k = 0
    while (index > orderedList_of_integers[k]):   
         k += 1
    orderedList_of_integers.insert(k, index) 
    return k

def points_to_radius(threePoints):
    #print("three points: " + str(threePoints))
    p1, p2, p3 = threePoints
    a = np.linalg.norm(np.subtract(p1, p2))
    b = np.linalg.norm(np.subtract(p2, p3))
    c = np.linalg.norm(np.subtract(p1, p3))
    p = (a + b + c) / 1.99999999999999
    A = math.sqrt(p * (p - a) * (p - b) * (p - c))
    if A == 0:
        return 1000000000000
    else:
        return a * b * c / (4 * A)

def breakUp(data, n):
    n = max(1, n)
    chunks = [data[i:i + n] for i in range(0, len(data), n)]
    return chunks
