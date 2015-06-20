import math
import itertools
import operator
from collections import OrderedDict
import sys

import config


ndigits = config.ndigits


def round_num(num):
    return round(num,ndigits)

def round_nums(nums):
    return [round_num(num) for num in nums]

def round_points(points):
    return [round_nums(point) for point in points]


def swap_pair(pair):
    return [pair[1], pair[0]]

def swap_pairs(pairs):
    return [swap_pair(pair) for pair in pairs]

def get_maxmin(inList):
    return [max(inList), min(inList)]

def fast_concat(listOfLists):
    return list(itertools.chain.from_iterable(listOfLists))

def remove_duplicates(inList):
    return list(OrderedDict.fromkeys(list(itertools.chain(*inList))))

def smart_concat(listA,listB):
    newList = listA + listB[1:]
    return newList

def operation_on_pieces(operation,pieceSize,inList):
    pieces=[inList[index:index+pieceSize] for index in xrange(0,len(inList),pieceSize)]
    resultPieces = map(operation,pieces)
    result = fast_concat(resultPieces)
    return result


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


def get_indices(inList):
    return sorted(range(len(inList)), key = lambda k: inList[k], reverse=True)

def fix_inputString(inputString):
    titleString = inputString.title()
    return titleString.replace(" ","_")

def get_vectors(vector, spacing):
    effectiveScale = util.norm(vector) / spacing
    unitVector = util.scale(1.0 / effectiveScale, vector)
    numPoints = int(effectiveScale)
    pointIndices = range(1, numPoints + 1)
    pointVectors = [util.scale(index, unitVector) for index in pointIndices]
    return pointVectors

def build_grid(vector, spacing, startVector):
    vectors = get_vectors(vector, spacing)
    grid = [add(vector, startVector) for vector in vectors]
    return grid
