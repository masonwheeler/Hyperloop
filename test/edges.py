import math

import util
import config
import proj
import elevation
import pyloncost

class Edge:
    cost = 0
    inRightOfWay = False
    startYVal = 0
    endYVal = 0
    angle = 0
    length = 0
    latlngCoords = []
    xyCoords = []
    vector = []

    def get_vector(self):
        startXYCoords, endXYCoords = self.xyCoords
        return util.subtract(endXYCoords, startXYCoords)        

    def pylon_grid(self):
        startXYCoords, endXYCoords = self.xyCoords
        pylonXYCoords = util.build_grid(self.vector, config.pylonSpacing, 
                                        startXYCoords)
        pylonLonLatCoords = proj.xys_to_lonlats(pylonXYCoords,config.proj)
        pylonLatLngCoords = util.swap_pairs(pylonLonLatCoords)
        return pylonLatLngCoords

    def land_grid(self):
        startXYCoords, endXYCoords = self.xyCoords
        landXYCoords = util.build_grid(self.vector, config.landGridSpacing, 
                                       startXYCoords)
        landpointsLonLatCoords = proj.xys_to_lonlats(pylonXYCoords,config.proj)
        return landpointsLonLatCoords

    def pylon_cost(self):
        pylonLatLngCoords = self.pylon_grid()
        pylonElevations = elevation.get_elevation(pylonLatLngCoords)
        pylonCost = pyloncost.pylon_cost(pylonElevations, config.pylonSpacing,
          config.maxSpeed, config.gTolerance, config.costPerPylonLength, 
          config.pylonBaseCost)              
        return pylonCost

    def land_cost(self):
        if self.inRightOfWay:
            return config.rightOfWayCost
        else:
            landpointsLonLatCoords = self.land_grid()  
            return land_cost(landPointsLonLatCoords)

    def add_cost(self):
        if config.hasNlcd:
            self.cost = self.pylon_cost() + self.land_cost()
        else:
            self.cost = self.pylon_cost()

    def __init__(self,startPoint,endPoint):
        self.inRightOfWay = (startPoint.inRightOfWay and endPoint.inRightOfWay)

        self.latlngCoords = [startPoint.latlngCoords, endPoint.latlngCoords]
        self.xyCoords = [startPoint.xyCoords, endPoint.xyCoords]
        self.length = proj.xy_distance(startPoint.xyCoords,endPoint.xyCoords)
        self.vector = self.get_vector()

        startXVal, self.startYVal = startPoint.latticeCoords
        endXVal, self.endYVal = endPoint.latticeCoords
        self.angle = math.degrees(math.atan(
          (self.endYVal - self.startYVal) / (endXVal - startXVal)))
        

    def display(self):
        print("The edge's cost is: " + str(self.cost) + ".")
        print("The edge's length is: " + str(self.length) + ".")
        print("The edge's lat-lng coords are: " + str(self.latlngCoords) + ".")        
        print("The edge's xy coords are: " + str(self.xyCoords) + ".")
        print("The edge's angle is: " + str(self.angle) + " degrees.")

def forward_project(edge):
    
        
def filter_edge(edge,envelope):
    forwardProjection = forward_project(edge)
    backwardProjection = backward_project(edge)
    edgeValid =  (projection_in_envelope(forwardProjection,envelope) and
                  projection_in_envelope(backwardProjection,envelope))
    return edgeValid     

def filter_edgesset(edgesSet, envelope):
    filteredEdgesSet = [edge for edge in edgesSet if filter_edge(edge,envelope)]
    return filteredEdgesSet

def filter_edgessets(edgesSets, envelope):
    filteredEdgesSets  = [filter_edgesset(edgesSet,envelope) for edgesSet in edgesSets]
    return filteredEdgesSets

def base_edgessets(lattice):
    edgesSets = []
    numEdges = 0
    for sliceIndex in range(len(lattice) - 1):
        sliceA = lattice[sliceIndex]
        sliceB = lattice[sliceIndex + 1]
        edgesSet = []
        for startPoint in sliceA:
            for endPoint in sliceB:
                numEdges += 1                
                edgesSet.append(Edge(startPoint,endPoint))
        edgesSet.sort(key = lambda edge: edge.cost)
        edgesSets.append(edgesSet)
    if config.verboseMode:
        print("Here is a sample Edge object: ")
        edgesSets[0][0].display()
    print("The total number of edges: " + str(numEdges))
    return edgesSets

def add_costs(edgesSets):
    for edgesSet in edgesSets:
        for edge in edgesSet:
            edge.add_cost()
    return edgesSets
    
def build_edgesets(lattice):
    baseEdgesSets = base_edgessets(lattice)
    filterEdgesSets = filter_edgessets(baseEdgesSets)
    finishedEdgesSets = add_costs(baseEdgesSets)
    return finishedEdgesSets



