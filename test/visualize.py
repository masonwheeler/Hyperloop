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
import interpolate
import util

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
    distancesArray = np.array(distances)  
    elevationsArray = np.array(elevations)
    #xSpline, ySpline = interpolate.interpolating_splines_2d(
    #               distancesArray, elevationsArray, sValues)
    xSpline, ySpline = interpolate.smoothing_splines_2d(distancesArray,
        elevationsArray, sValues, 1, 10**5)      
    xValues = interpolate.get_spline_values(xSpline, sValues)
    yValues = interpolate.get_spline_values(ySpline, sValues)
    plt.plot(distances, elevations)
    plt.plot(xValues, yValues, 'r-')
    ##plt.axis('equal')
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























