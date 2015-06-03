import config

import itertools
import operator

ndigits = config.ndigits

def round_num(num):
    return round(num,ndigits)

def round_nums(nums):
    return [round_num(num) for num in nums]

def round_points(points):
    return [round_nums(point) for point in points]

def swapPair(pair):
    return [pair[1],pair[0]]

def swapPairs(pairs):
    return [swapPair(pair) for pair in pairs]

def fastConcat(listOfLists):
    return list(itertools.chain.from_iterable(listOfLists))

def operationOnPieces(operation,pieceSize,inList):
    pieces=[inList[index:index+pieceSize] for index in xrange(0,len(inList),pieceSize)]
    resultPieces = map(operation,pieces)
    result = fastConcat(resultPieces)
    return result

def safeOperation(operation,vectorA,vectorB):
    if len(vectorA) == len(vectorB):
        return map(operation,vectorA,vectorB)
    else:
        print("Mismatched vector lengths.")
        return None

def add(vectorA,vectorB):
    return safeOperation(operator.add,vectorA,vectorB)

def subtract(vectorA,vectorB):
    return safeOperation(operator.sub,vectorA,vectorB)

def scale(scalar,vector):
    return [element * scale for element in vector]

def norm(vector):
    return math.sqrt(sum(map(lambda x: x**2, vector)))

def entry_multiply(vectorA,vectorB):
    return safeOperation(operator.mul,vectorA,vectorB)

def getIndices(inList):
    return sorted(range(len(inList)), key = lambda k: inList[k], reverse=True)
