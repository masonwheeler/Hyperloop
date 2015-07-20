"""
Original Developer: Jonathan Ward
Purpose of Module: To build edges with associated cost and elevation data
                   from pairs of lattice points.
Last Modified: 7/17/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To fix grid naming issues.
"""

#Standard Modules:
import math
#from progress.bar import Bar

#Our Modules
import util
import config
import proj
import elevation
import pyloncost
import landcost
import cacher

"""
class SlowBar(Bar):
    suffix = '%(percent).1f%% - %(minutes)d minutes remaining...'
    @property
    def minutes(self):
        return self.eta // 60
"""

class Edge:
    isInRightOfWay = False
    isUseful = True
    landCost = 0
    landCostColorCode = 0
    pylonCost = 0
    angle = 0
    length = 0
    startId = 0
    endId = 0
    latlngCoords = []
    geospatialCoords = []
    geospatialVector = []
    pylonGrid = []
    landcostGrid = []
    heights = []

    def build_pylon_grid(self):
        startGeospatialCoords, endGeospatialCoords = self.geospatialCoords
        pylonGeospatialCoords = util.build_grid(self.geospatialVector,
                                config.pylonSpacing, startGeospatialCoords)
        pylonGrid = proj.geospatials_to_latlngs(pylonGeospatialCoords,
                                                        config.proj)
        self.pylonGrid = pylonGrid

    def build_landcost_grid(self):
        startGeospatialCoords, endGeospatialCoords = self.geospatialCoords
        landGeospatialCoords = util.build_grid(self.geospatialVector,
                                config.landPointSpacing, startGeospatialCoords)
        landcostGrid = proj.geospatials_to_latlngs(
                               landGeospatialCoords, config.proj)
        self.landcostGrid = landcostGrid

    def add_landcost(self):
        if self.isInRightOfWay:
            self.landCost = 0          
        else:
            self.landCost = landcost.edge_land_cost(self.landcostGrid)
        #print(self.landCost)

    def pyloncost_and_heights(self):
        self.build_pylon_grid()
        pylonLatLngCoords = self.pylonGrid
        pylonElevations = elevation.usgs_elevation(pylonLatLngCoords)
        pylonCost, heights = pyloncost.pylon_cost(pylonElevations, config.pylonSpacing,
          config.maxSpeed, config.gTolerance, config.costPerPylonLength, 
          config.pylonBaseCost)              
        return [pylonCost, heights]

    def add_pyloncost_and_heights(self):
        self.pylonCost, self.heights = self.pyloncost_and_heights()
        print("Pylon cost for edge: " + str(self.pylonCost))

    def __init__(self,startPoint,endPoint):        
        self.isInRightOfWay = (startPoint["isInRightOfWay"]
                               and endPoint["isInRightOfWay"])
        self.latlngCoords = [startPoint["latlngCoords"],
                             endPoint["latlngCoords"]]
        self.geospatialCoords = [startPoint["geospatialCoords"],
                                 endPoint["geospatialCoords"]]
        self.geospatialVector = util.edge_to_vector(self.geospatialCoords)
        startGeospatialCoords, endGeospatialCoords = self.geospatialCoords
        startXVal, startYVal = startGeospatialCoords
        endXVal, endYVal = endGeospatialCoords
        self.startId = startPoint["pointId"]
        self.endId = endPoint["pointId"]
        self.angle = math.degrees(math.atan2(endYVal - startYVal,
                                             endXVal - startXVal))
    def as_plottable(self):
        plottableEdge = zip(*self.geospatialCoords)
        return [plottableEdge, self.landCostColorCode]

    def display(self):
        print("The edge's cost is: " + str(self.cost) + ".")
        print("The edge's length is: " + str(self.length) + ".")
        print("The edge's lat-lng coords are: " + str(self.latlngCoords) + ".")        
        print("The edge's xy coords are: " + str(self.geospatialCoords) + ".")
        print("The edge's angle is: " + str(self.angle) + " degrees.")


    def add_landcost_colorcode(self):
        landcostColorCodes = [[1000000, 'r'],
                              [2000000, 2],
                              [3000000, 3],
                              [5000000, 4],
                              [10000000, 5]]                              
        overflowCode = 6
        colorCode = util.interval_to_value(self.landCost,
                             landcostColorCodes, overflowCode)
        print(colorCode)
        self.landCostColorCode = colorCode


class EdgesSets:
    baseEdgesSets = []
    filteredEdgesSetsList = []
    finishedEdgesSets = []
    plottableBaseEdges = []
    plottableFilteredEdges = []
    plottableFinishedEdges = []
   
    
    def base_edgessets(self,lattice):
        edgesSets = []
        for sliceIndex in range(len(lattice) - 1):
            sliceA = lattice[sliceIndex]
            sliceB = lattice[sliceIndex + 1]
            edgesSet = []
            for startPoint in sliceA:
                for endPoint in sliceB:
                    edgesSet.append(Edge(startPoint,endPoint))
            edgesSets.append(edgesSet)
        if config.verboseMode:
            print("Here is a sample Edge object: ")
            edgesSets[0][0].display()
        return edgesSets    
    
    def edge_pair_compatible(self, edgeA, edgeB):
        if edgeA.endId == edgeB.startId:
            if abs(edgeA.angle - edgeB.angle) < config.degreeConstraint:
                return True
        return False

    def determine_useful_edges(self, edgesSets):
        for edgeA in edgesSets[0]:
            compatibles = [self.edge_pair_compatible(edgeA,edgeB)
                           for edgeB in edgesSets[1]]
            edgeA.isUseful = any(compatibles)
        for edgeSetIndex in range(1,len(edgesSets)-1):
            for edgeB in edgesSets[edgeSetIndex]:
                compatiblesA = [self.edge_pair_compatible(edgeA, edgeB)
                              for edgeA in edgesSets[edgeSetIndex-1]]
                compatiblesC = [self.edge_pair_compatible(edgeB, edgeC)
                              for edgeC in edgesSets[edgeSetIndex+1]]
                edgeB.isUseful = any(compatiblesA) and any(compatiblesC)
        for edgeB in edgesSets[-1]:
            compatibles = [self.edge_pair_compatible(edgeA, edgeB)
                           for edgeA in edgesSets[-2]]
            edgeB.isUseful = any(compatibles)                    

    def filter_edges(self, edgesSets):
        filteredEdgesSets = []
        for edgesSet in edgesSets:
            filteredEdgesSet = filter(lambda edge : edge.isUseful, edgesSet)
            filteredEdgesSets.append(filteredEdgesSet)
        return filteredEdgesSets

    def check_empty(self, edgesSets):
        for edgesSet in edgesSets:
            if len(edgesSet) == 0:
                print(edgesSet)
                print("empty edge")
                return True
        return False
    
    def iterative_filter(self):
        oldNumEdges = util.list_of_lists_len(self.baseEdgesSets)        
        util.smart_print("The original number of edges: " + str(oldNumEdges))
         
        filteredEdgesIndex = 0

        self.determine_useful_edges(self.baseEdgesSets)      
        filteredEdges = self.filter_edges(self.baseEdgesSets)
        if self.check_empty(filteredEdges):
            raise ValueError("encountered empty edge")
        self.filteredEdgesSetsList.append(filteredEdges)
        flattenedFilteredEdges = util.fast_concat(
                                self.filteredEdgesSetsList[filteredEdgesIndex])
        newNumEdges = len(flattenedFilteredEdges)

        while newNumEdges != oldNumEdges:          
            self.plottableFilteredEdges.append([edge.as_plottable()
                                          for edge in flattenedFilteredEdges])        
            util.smart_print("The number of edges is now: " + str(newNumEdges))
            self.determine_useful_edges(
                            self.filteredEdgesSetsList[filteredEdgesIndex])
            filteredEdges = self.filter_edges(
                            self.filteredEdgesSetsList[filteredEdgesIndex])
            if self.check_empty(filteredEdges):
                raise ValueError("encountered empty edge")
            self.filteredEdgesSetsList.append(filteredEdges)
            filteredEdgesIndex += 1
            flattenedFilteredEdges = util.fast_concat(
                                self.filteredEdgesSetsList[filteredEdgesIndex])
            oldNumEdges, newNumEdges = newNumEdges, len(flattenedFilteredEdges)
        
#    def add_costs(self):
#        for edgesSet in self.baseEdgesSets:
#            for edge in edgesSet:
#                edge.add_cost()
#        return edgesSets

    def add_pyloncosts_and_heights(self, edgesSets):
        numEdges = sum([len(edgeSet) for edgeSet in edgesSets])
        bar = SlowBar('computing construction cost of edge-set...', max=numEdges, width = 50)
        for edgesSet in edgesSets:
            for edge in edgesSet:
                edge.add_pyloncost_and_heights()
                bar.next()
        bar.finish()
        return edgesSets

    def build_landcost_grids(self, edgesSets):
        for edgesSet in edgesSets:
            for edge in edgesSet:
                edge.build_landcost_grid()        

    def build_pyloncost_grids(self, edgesSets):
        for edgesSet in edgesSets:
            for edge in edgesSet:
               edge.build_pyloncost_grid()        

    def add_edge_landcosts(self, edgesSets):
        for edgesSet in edgesSets:
            for edge in edgesSet:
                edge.add_landcost()        

    def add_landcost_colorcodes(self, edgesSets):
        for edgesSet in edgesSets:
            for edge in edgesSet:
                edge.add_landcost_colorcode()

    def __init__(self, lattice):
        self.baseEdgesSets = self.base_edgessets(lattice)
        flattenedBaseEdges = util.fast_concat(self.baseEdgesSets)
        self.plottableBaseEdges = [edge.as_plottable()
                                   for edge in flattenedBaseEdges]
        self.iterative_filter()
        self.finishedEdgesSets = self.filteredEdgesSetsList[-1]
        flattenedFinishedEdges = util.fast_concat(self.finishedEdgesSets)
        self.plottableFinishedEdges = [edge.as_plottable() for edge
                                       in flattenedFinishedEdges]
        self.build_landcost_grids(self.finishedEdgesSets)
        self.add_edge_landcosts(self.finishedEdgesSets)
        self.add_landcost_colorcodes(self.finishedEdgesSets)
        flattened = util.fast_concat(self.finishedEdgesSets)
        landCosts = [edge.landCostColorCode for edge in flattened]
        #print(sorted(landCosts))
        #print(util.get_maxmin(landCosts))      
        #self.finishedEdgesSets = self.add_pyloncosts_and_heights(self.finishedEdgesSets)
        #numEdges = sum([len(edgeSet) for edgeSet in edgesSets])
        #bar = SlowBar('computing construction cost of edge-set...', max=numEdges, width = 50)
        #for edgesSet in edgesSets:
        #   for edge in edgesSet:
        #      edge.add_costAndHeight()
        #      bar.next()
        #bar.finish()


def build_edgessets(lattice):
    edgesSets = EdgesSets(lattice)
    finishedEdgesSets = edgesSets.finishedEdgesSets
    plottableFinishedEdges = edgesSets.plottableFinishedEdges
    return [finishedEdgesSets, plottableFinishedEdges]

def get_edgessets(lattice):
    finishedEdgesSets, plottableFinishedEdges = cacher.get_object("edgessets",
          build_edgessets, [lattice], cacher.save_edgessets, config.edgesFlag)
    return [finishedEdgesSets, plottableFinishedEdges]

