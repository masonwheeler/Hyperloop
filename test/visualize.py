"""
Original Developer: Jonathan Ward
Purpose of Module: To visualize the output from the algorithm.

Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To remove unnecessary functions and lines.
"""

#Standard Modules
import matplotlib.pyplot as plt
import numpy as np

#Our Modules
import config
import interpolate
import util

def circle_function(x, r):
    if x > r:
        return -float("Inf")
    else:
        y = np.sqrt(np.square(r) - np.square(x)) - r
        return y

def build_window(leftBound, rightBound, radius):
    relativeIndices = range(-leftBound, rightBound + 1)
    window = [{"relativeIndex": relativeIndex,
               "relativeElevation":
                circle_function(abs(relativeIndex * config.pylonSpacing), radius)}
                for relativeIndex  in relativeIndices]
    return window
    
def add_current_window(envelope, currentWindow):
    for point in currentWindow:
        currentIndex = point["index"]
        envelope[currentIndex].append(point["elevation"])        

def build_envelope(elevations, radius):
    windowSize = int(radius / config.pylonSpacing)
    envelopeLists = [[] for i in xrange(len(elevations))]
    for currentIndex in range(0, len(elevations)):
        if currentIndex < windowSize:
            leftBound = currentIndex
        else: 
            leftBound = windowSize
        if currentIndex > (len(elevations) - 1) - windowSize: 
            rightBound = (len(elevations) - 1) - currentIndex
        else:
            rightBound = windowSize
        relativeWindow = build_window(leftBound, rightBound, radius)
        currentElevation = elevations[currentIndex]
        currentWindow = [{
            "index": point["relativeIndex"] + currentIndex,
            "elevation": point["relativeElevation"] + currentElevation
            }
            for point in relativeWindow]
        add_current_window(envelopeLists, currentWindow)
    envelope = map(max, envelopeLists)
    return envelope
        

def visualize_elevation_profile(elevationProfile):
    distances = []
    elevations = []
    numPoints = len(elevationProfile)
    sValues = np.arange(numPoints)
    for elevationPoint in elevationProfile:
        distance = elevationPoint["distanceAlongPath"]
        elevation = elevationPoint["landElevation"]
        distances.append(distance)
        elevations.append(elevation)
    curvatureThresholdA = interpolate.compute_curvature_threshold(       
                          config.maxSpeed, config.verticalAccelConstraint)
    radiusA = 1.0 / curvatureThresholdA
    envelopeA = build_envelope(elevations, radiusA)
    curvatureThresholdB = interpolate.compute_curvature_threshold(       
                          config.maxSpeed/1.2, config.verticalAccelConstraint)
    radiusB = 1.0 / curvatureThresholdB
    envelopeB = build_envelope(elevations, radiusB)
    plt.plot(distances, elevations)
    plt.plot(distances, envelopeA, 'r-')
    plt.plot(distances, envelopeB, 'g-')
    #plt.axis('equal')
    plt.show()

def plot_object(objectData, style):    
    xValues, yValues = objectData
    #print(xValues, yValues, style)
    plt.plot(xValues, yValues, style)   

def plot_objects(objects):
    for eachObject in objects:
        objectData, objectStyle = eachObject
        plot_object(objectData, objectStyle)
    #plt.axis('equal')
    plt.show()

def plot_colorful_objects(objectsAndStyles):
    for eachObjectAndStyle in objectsAndStyles:
        eachObject, eachStyle = eachObjectAndStyle
        plot_object(eachObject, eachStyle)
    plt.show()

def plot_objectslist(objectData, style):
    for eachObjectData in objectData:       
        plot_object(eachObjectData, style)

def scatter_plot(xVals, yVals):
    plt.scatter(xVals, yVals)
    plt.show()
 
def display_inputs(inputs):
    for eachInput in inputs:              
        
        plotFunction = functionDictionary[functionNumber]
        plotFunction(objectData, style)
    #plt.subplot(plotDictionary[1])
    #plt.subplot(plotDictionary[2])
    #plt.axis('equal')
    #x1, x2, y1, y2 = plt.axis()
    #plt.axis((x1,x2, -10**(-4), 10**(-4)))
    plt.show()























