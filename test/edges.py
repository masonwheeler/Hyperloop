import math

import util
import config
import proj
import elevation
import pyloncost
import cacher
#from progress.bar import Bar

#class SlowBar(Bar):
#    suffix = '%(percent).1f%% - %(minutes)d minutes remaining...'
#    @property
#    def minutes(self):
#        return self.eta // 60



class Edge:
    cost = 0
    angle = 0
    length = 0
    startId = 0
    endId = 0
    latlngCoords = []
    geospatialCoords = []
    heights = []
    inRightOfWay = False
    isUseful = True

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

    def pylon_cost_and_heights(self):
        pylonLatLngCoords = self.pylon_grid()
        pylonElevations = elevation.usgs_elevation(pylonLatLngCoords)
        pylonCost, heights = pyloncost.pylon_cost(pylonElevations, config.pylonSpacing,
          config.maxSpeed, config.gTolerance, config.costPerPylonLength, 
          config.pylonBaseCost)              
        return [pylonCost, heights]

    def land_cost(self):
        if self.inRightOfWay:
            return config.rightOfWayCost
        else:
            landpointsLonLatCoords = self.land_grid()  
            return land_cost(landPointsLonLatCoords)

    def add_costAndHeight(self):
        pylonCost, Heights = self.pylon_cost_and_Heights()
        self.heights = Heights
        if config.hasNlcd:
            self.cost = pylonCost + self.land_cost()
        else:
            self.cost = pylonCost

    def __init__(self,startPoint,endPoint):        
        self.isInRightOfWay = (startPoint["isInRightOfWay"]
                               and endPoint["isInRightOfWay"])
        self.latlngCoords = [startPoint["latlngCoords"],
                             endPoint["latlngCoords"]]
        self.geospatialCoords = [startPoint["geospatialCoords"],
                                 endPoint["geospatialCoords"]]
        startGeospatialCoords, endGeospatialCoords = self.geospatialCoords
        startXVal, startYVal = startGeospatialCoords
        endXVal, endYVal = endGeospatialCoords
        self.startId = startPoint["pointId"]
        self.endId = endPoint["pointId"]
        self.angle = math.degrees(math.atan2(endYVal - startYVal,
                                             endXVal - startXVal))
    def as_plottable(self):
        plottableEdge = zip(*self.geospatialCoords)
        return plottableEdge

    def display(self):
        print("The edge's cost is: " + str(self.cost) + ".")
        print("The edge's length is: " + str(self.length) + ".")
        print("The edge's lat-lng coords are: " + str(self.latlngCoords) + ".")        
        print("The edge's xy coords are: " + str(self.xyCoords) + ".")
        print("The edge's angle is: " + str(self.angle) + " degrees.")


class EdgesSets:
    baseEdgesSets = []
    filteredEdgesSets = []
    plottableBaseEdges = []
    plottableFilteredEdges = []
    
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

    def add_costs(self):
        for edgesSet in self.baseEdgesSets:
            for edge in edgesSet:
                edge.add_cost()
        return edgesSets        

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
        self.filteredEdgesSets.append(filteredEdges)
        flattenedFilteredEdges = util.fast_concat(
                                 self.filteredEdgesSets[filteredEdgesIndex])
        newNumEdges = len(flattenedFilteredEdges)

        while newNumEdges != oldNumEdges:          
            self.plottableFilteredEdges.append([edge.as_plottable()
                                          for edge in flattenedFilteredEdges])        
            util.smart_print("The number of edges is now: " + str(newNumEdges))
            self.determine_useful_edges(
                                  self.filteredEdgesSets[filteredEdgesIndex])
            filteredEdges = self.filter_edges(
                                  self.filteredEdgesSets[filteredEdgesIndex])
            if self.check_empty(filteredEdges):
                raise ValueError("encountered empty edge")
            self.filteredEdgesSets.append(filteredEdges)
            filteredEdgesIndex += 1
            flattenedFilteredEdges = util.fast_concat(
                                  self.filteredEdgesSets[filteredEdgesIndex])
            oldNumEdges, newNumEdges = newNumEdges, len(flattenedFilteredEdges)
        
        def add_costsAndHeights(self):
            edgesSets = self.baseEdgesSets
            numEdges = sum([len(edgeSet) for edgeSet in edgesSets])
            bar = SlowBar('computing construction cost of edge-set...', max=numEdges, width = 50)
            for edgesSet in edgesSets:
                for edge in edgesSet:
                    edge.add_costAndHeight()
                    bar.next()
            bar.finish()
            return edgesSets

    def __init__(self, lattice):
        self.baseEdgesSets = self.base_edgessets(lattice)
        flattenedBaseEdges = util.fast_concat(self.baseEdgesSets)
        self.plottableBaseEdges = [edge.as_plottable()
                                   for edge in flattenedBaseEdges]
        self.iterative_filter()

def build_edgessets(lattice):
    edgesSets = EdgesSets(lattice)
    return edgesSets



#def get_edgessets(lattice):
#    edgesSets = cacher.get_object("edgessets", build_edgessets,
#                [lattice], cacher.save_edgessets, config.edgesFlag)
#    return edgesSets

