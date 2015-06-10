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


def fast_concat(listOfLists):
    return list(itertools.chain.from_iterable(listOfLists))

def remove_duplicates(inList):
    return list(OrderedDict.fromkeys(list(itertools.chain(*inList))))


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
