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
    plt.plot(xValues, yValues, style)   

def plot_colorful_objects(objectsAndStyles):
    for eachObjectAndStyle in objectsAndStyles:
        eachObject, eachStyle = eachObjectAndStyle
        plot_object(eachObject, eachStyle)

def plot_objectslist(objectData, style):
    for eachObjectData in objectData:       
        plot_object(eachObjectData, style)
 
def plot_objects(objects):
    plotDictionary = {1: 211,
                      2: 212}
    functionDictionary = {1: plot_object,
                          2: plot_objectslist}
    for eachObject in objects:              
        objectData, style, plotNumber, functionNumber = eachObject               
        #plt.subplot(plotDictionary[plotNumber])
        plotFunction = functionDictionary[functionNumber]
        plotFunction(objectData, style)
    #plt.subplot(plotDictionary[1])
    plt.axis('equal')
    #plt.subplot(plotDictionary[2])
    #x1, x2, y1, y2 = plt.axis()
    #plt.axis((x1,x2, -10**(-4), 10**(-4)))
    plt.show()























