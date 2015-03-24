"""
Jonathan Ward 3/18/2015

This file contains the function definitions for generating and validating
routes on the lattice.
"""

def lists_to_tuples(lists):
    tuples = [tuple(eachList) for eachList in lists]
    return tuples

def generate_random_route(lattice, scale):
    route = [[0,0]]
    for latticeSlice in lattice:
        route.append(random.choice(latticeSlice))
    route.append([scale,0])        
    return route

def edge_to_vector(edge):
    firstPoint = edge[0]
    secondPoint = edge[1]
    firstX = firstPoint[0]
    secondX = secondPoint[0]
    firstY = firstPoint[1]
    secondY = secondPoint[1]
    vector = [secondX - firstX, secondY - firstY]
    return vector

def is_edge_deltaY_valid(edge, allowedRange):
    vector = edge_to_vector(edge)
    yDifference = abs(vector[1])
    edge_valid = yDifference <= allowedRange
    return edge_valid

def is_route_deltaY_valid(route, allowedDeltaYRange):
    routeDeltaYValid = True
    edges = list_to_pairs(route)
    for edge in edges:
        currentEdgeDeltaYValid = is_edge_deltaY_valid(edge, allowedDeltaYRange)
        routeDeltaYValid = (routeDeltaYValid and currentEdgeDeltaYValid)
    return routeDeltaYValid

def create_vectors(edges):
    vectors = [edge_to_vector(edge) for edge in edges]
    return vectors

def create_vector_pairs(vectors):
    vectorPairs = list_to_pairs(vectors)
    return vectorPairs

def get_deltaTheta_between_vectorPair(vectorPair):
    firstVector = vectorPair[0]
    secondVector = vectorPair[1]
    theta1 = math.atan2(firstVector[1], firstVector[0])
    theta2 = math.atan2(secondVector[1], secondVector[0])
    deltaTheta = abs(theta2 - theta1)
    return deltaTheta

def vecPair_deltaTheta_valid(vectorPair, allowedDegreeRange):
    deltaTheta = get_deltaTheta_between_vectorPair(vectorPair)
    vectorPairDeltaThetaValid = (deltaTheta <= math.radians(allowedDegreeRange))
    return vectorPairDeltaThetaValid

def is_route_deltaTheta_valid(route, degreeRange):
    routeDeltaThetaValid = True
    edges = list_to_pairs(route)
    vectors = create_vectors(edges)
    vectorPairs = create_vector_pairs(vectors)
    for vecPair in vectorPairs:
        vecPairDeltaThetaValid = vecPair_deltaTheta_valid(vecPair, degreeRange)
        routeDeltaThetaValid = (routeDeltaThetaValid and vecPairDeltaThetaValid)
    return routeDeltaThetaValid

def gen_ran_sat_route(degreeRange, lattice):
    testRoute = generate_random_route(lattice)
    while (not is_route_deltaTheta_valid(testRoute, 60)):
        testRoute = generate_random_route(lattice)
    return testRoute
