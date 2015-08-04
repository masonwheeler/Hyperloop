"""
Original Developer: Jonathan Ward
Purpose of Module: To visualize the output from the algorithm.

Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To remove unnecessary functions and lines.
"""

import numpy as np
import matplotlib.pyplot as plt

import util


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























