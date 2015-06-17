import math

import util
import config
import proj
import elevation
import pyloncost

class Edge:
    cost = 0
    #startPoint = 0
    #endPoint = 0
    startYVal = 0
    endYVal = 0
    angle = 0
    length = 0
    latlngCoords = []
    xyCoords = []

    def pylon_grid(self):
        startXYCoords, endXYCoords = self.xyCoords
        edgeVector = util.subtract(endXYCoords, startXYCoords)
        effectiveScale = self.length / config.pylonSpacing
        unitVector = util.scale(1.0 / effectiveScale, edgeVector)
        numPylons = int(effectiveScale)
        pylonIndices = range(1, numPylons+1)
        pylonVectors = [util.scale(index, unitVector) for index in pylonIndices]
        pylonXYCoords = [util.add(pylonVector, startXYCoords) 
                         for pylonVector in pylonVectors]
        pylonLonLatCoords = proj.xys_to_lonlats(pylonXYCoords,config.proj)
        pylonLatLngCoords = util.swap_pairs(pylonLonLatCoords)
        return pylonLatLngCoords

    def get_cost(self):
        pylonLatLngCoords = self.pylon_grid()
        pylonElevations = elevation.get_elevation(pylonLatLngCoords)
        pylonCost = pyloncost.pylon_cost(pylonElevations, config.pylonSpacing,
          config.maxSpeed, config.gTolerance, config.costPerPylonLength, 
          config.pylonBaseCost)        
        return pylonCost

    def __init__(self,startPoint,endPoint):
        #self.startPoint = startPoint
        #self.endPoint = endPoint
        self.latlngCoords = [startPoint.latlngCoords, endPoint.latlngCoords]
        self.xyCoords = [startPoint.xyCoords, endPoint.xyCoords]
        self.length = proj.xy_distance(startPoint.xyCoords,endPoint.xyCoords)

        startXVal, self.startYVal = startPoint.latticeCoords
        endXVal, self.endYVal = endPoint.latticeCoords
        self.angle = math.degrees(math.atan(
          (self.endYVal - self.startYVal) / (endXVal - startXVal)))

    def display(self):
        print("The edge's length is: " + str(self.length) + ".")
        print("The edge's lat-lng coords are: " + str(self.latlngCoords) + ".")        
        print("The edge's xy coords are: " + str(self.xyCoords) + ".")
        print("The edge's angle is: " + str(self.angle) + " degrees.")
        
     

def get_edgessets(lattice):
    edgesSets = []
    for sliceIndex in range(len(lattice) - 1):
        sliceA = lattice[sliceIndex]
        sliceB = lattice[sliceIndex + 1]
        edgesSet = []
        for startPoint in sliceA:
            for endPoint in sliceB:                
                edgesSet.append(Edge(startPoint,endPoint))
        edgesSet.sort(key = lambda edge: edge.cost)
        edgesSets.append(edgesSet)
    print(edgesSets[0][0].get_cost())
    return edgesSets

    
    
