import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

import util

def lists_to_tuples(lists):
    tuples = [tuple(eachList) for eachList in lists]
    return tuples

def plot_object(objectData, style):    
    xValues, yValues = objectData
    plt.plot(xValues, yValues, style)   

def plot_objectslist(objectData, style):
    for eachObjectData in objectData:       
        plot_object(eachObjectData, style)
 
def plot_objects(objects):
    plotDictionary = {1: 211,
                      2: 212}
    functionDictionary = {1: plot_object,
                          2: plot_objectslist}
    for eachObject in objects:              
        #print(len(eachObject)) 
        objectData, style, plotNumber, functionNumber = eachObject               
        #print(len(objectData))
        #plt.subplot(plotDictionary[plotNumber])
        plotFunction = functionDictionary[functionNumber]
        plotFunction(objectData, style)
    #plt.subplot(plotDictionary[1])
    plt.axis('equal')
    #plt.subplot(plotDictionary[2])
    #x1, x2, y1, y2 = plt.axis()
    #plt.axis((x1,x2, -10**(-4), 10**(-4)))
    plt.show()























