"""
Original Developer: Jonathan Ward
Purpose of Module: To build edges with associated cost and elevation data
                   from pairs of lattice points.
Last Modified: 7/21/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add a richer datastructure to store pylon and
                           landcover data.
"""

#Standard Modules:
import math
#from progress.bar import Bar

#Our Modules
import util
import config
import proj
import elevation
import pylons
import landcover
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
    pylonCost = 0
    angle = 0
    length = 0
    startId = 0
    endId = 0
    latlngs = []
    geospatials = []
    geospatialVector = []
    pylons = []
    landCostSamples = []

    def build_pylons(self):
        startGeospatial, endGeospatial = self.geospatials
        pylonGeospatials = util.build_grid(self.geospatialVector,
                                config.pylonSpacing, startGeospatial)
        pylonLatLngs = proj.geospatials_to_latlngs(pylonGeospatials,
                                                        config.proj)
        pylonElevations = elevation.usgs_elevation(pylonLatLngs)       
        attributes = zip(*[pylonGeospatials, pylonLatLngs, pylonElevations])
        #attributes = zip(*[pylonGeospatials, pylonLatLngs])
        self.pylons = [{"geospatial" : attribute[0],
                                "latlng" : attribute[1],
                                "elevation" : attribute[2],
                                "pylonHeight" : 0,
                                "pylonCost" : 0}
                               for attribute in attributes]         
        #self.pylons = [{"geospatial" : attributes[0],
        #                "latlng" : attributes[1],
        #                "pylonHeight" : 0,
        #                "pylonCost" : 0}
        #               for attribute in attributes]         
        pylons.build_pylons(self.pylons)
        pylons.get_pyloncosts(self.pylons)
        self.pylonCost = pylons.edge_pyloncost(self.pylons)       
        print(self.pylonCost) 

    def build_landcost_samples(self):
        startGeospatial, endGeospatial = self.geospatials
        landcoverGeospatials = util.build_grid(self.geospatialVector,
                                config.landPointSpacing, startGeospatial)
        landcoverLatLngs = proj.geospatials_to_latlngs(
                               landcoverGeospatials, config.proj)
        landcoverPixelValues = landcover.landcover_pixelvalues(
                                              landcoverLatLngs)
        attributes = zip(*[landcoverGeospatials, landcoverLatLngs,
                           landcoverPixelValues])        
        #attributes = zip(*[landcoverGeospatials, landcoverLatLngs])
        #self.landCostSamples = [{"geospatial" : attributes[0],
        #                         "latlng" : attributes[1]}
        #                        for attribute in attributes]                 
        self.landcostSamples = [{"geospatial" : attribute[0],
                                 "latlng" : attribute[1],
                                 "pixelValues" : attribute[2]}
                                for attribute in attributes]                 
        if self.isInRightOfWay:
            self.landCost = config.rightOfWayLandCost          
        else:
            self.landCost = \
               landcover.pixelvalues_to_landcost(landcoverPixelValues)


#    def pyloncost_and_heights(self):
#        pylonCost, heights = pyloncost.pylon_cost(pylonElevations, config.pylonSpacing,
#          config.maxSpeed, config.gTolerance, config.costPerPylonLength, 
#          config.pylonBaseCost)              
#        return [pylonCost, heights]
   
    def __init__(self,startPoint,endPoint):        
        self.isInRightOfWay = (startPoint["isInRightOfWay"]
                               and endPoint["isInRightOfWay"])
        self.latlngs = [startPoint["latlngCoords"],
                        endPoint["latlngCoords"]]
        self.geospatials = [startPoint["geospatialCoords"],
                            endPoint["geospatialCoords"]]
        self.geospatialVector = util.edge_to_vector(self.geospatials)
        startGeospatial, endGeospatial = self.geospatials
        startXVal, startYVal = startGeospatial
        endXVal, endYVal = endGeospatial
        self.startId = startPoint["pointId"]
        self.endId = endPoint["pointId"]
        self.angle = math.degrees(math.atan2(endYVal - startYVal,
                                             endXVal - startXVal))
#    def as_plottable(self):
#        plottableEdge = zip(*self.geospatialCoords)
#        return [plottableEdge, self.landCostColorCode]

    def as_dict(self):
        edgeDict = {"geospatials" : self.geospatials,
                    "latlngs" : self.latlngs,
                    "landCost" : self.landCost,
                    "pylonCost" : self.pylonCost,
                    "pylons" : self.pylons,
                    "landCostSamples" : self.landCostSamples}
        return edgeDict

    def display(self):
        print("The edge's cost is: " + str(self.cost) + ".")
        print("The edge's length is: " + str(self.length) + ".")
        print("The edge's lat-lng coords are: " + str(self.latlngCoords) + ".")        
        print("The edge's xy coords are: " + str(self.geospatialCoords) + ".")
        print("The edge's angle is: " + str(self.angle) + " degrees.")


#    def add_landcost_colorcode(self):
#        landcostColorCodes = [[1000000, 'r-'], #least expensive
#                              [2000000, 'm-'],
#                              [3000000, 'y-'],
#                              [5000000, 'g-'],
#                              [10000000, 'b-']]                              
#        overflowCode = 'k-'                    #most expensive
#        colorCode = util.interval_to_value(self.landCost,
#                             landcostColorCodes, overflowCode)
#        print(colorCode)
#        self.landCostColorCode = colorCode


class EdgesSets:
    baseEdgesSets = []
    filteredEdgesSetsList = []
    finishedEdgesSets = []
    #plottableBaseEdges = []
    #plottableFilteredEdges = []
    #plottableFinishedEdges = []
   
    
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
        return edgesSets    
    
    def edge_pair_compatible(self, edgeA, edgeB):
        if edgeA.endId == edgeB.startId:
            if abs(edgeA.angle - edgeB.angle) < config.degreeConstraint:
                return True
        return False

    def determine_useful_edges(self, edgesSets):
        "An edge is useful if it has compatible edges in the adjacent \
         edge sets."

        "For edges in the first edge set."
        for edgeA in edgesSets[0]:
            "Check that each edge in the first edge set has an edge \
             which is compatible with it in the second edge set."
            compatibles = [self.edge_pair_compatible(edgeA,edgeB)
                           for edgeB in edgesSets[1]]
            edgeA.isUseful = any(compatibles)
        "For edges in the second through second to last edge set."
        for edgeSetIndex in range(1,len(edgesSets)-1):
            for edgeB in edgesSets[edgeSetIndex]:
                "Check that each edge in the ith edge set has an edge \
                 which is compatible with it in the (i-1)th edge set \
                 and in the (i+1)th edge set."
                compatiblesA = [self.edge_pair_compatible(edgeA, edgeB)
                              for edgeA in edgesSets[edgeSetIndex-1]]
                compatiblesC = [self.edge_pair_compatible(edgeB, edgeC)
                              for edgeC in edgesSets[edgeSetIndex+1]]
                edgeB.isUseful = any(compatiblesA) and any(compatiblesC)
        "For edges in the last edge set."
        for edgeB in edgesSets[-1]:
            "Check that each edge in the last edge set has an edge which \
             is compatible with it in the second to last edge set."
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
            #self.plottableFilteredEdges.append([edge.as_plottable()
            #                              for edge in flattenedFilteredEdges])        
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

#    def add_pyloncosts_and_heights(self, edgesSets):
#        numEdges = sum([len(edgeSet) for edgeSet in edgesSets])
#        bar = SlowBar('computing construction cost of edge-set...', max=numEdges, width = 50)
#        for edgesSet in edgesSets:
#            for edge in edgesSet:
#                edge.add_pyloncost_and_heights()
#                bar.next()
#        bar.finish()
#        return edgesSets

    def build_landcost_samples(self, edgesSets):
        for edgesSet in edgesSets:
            for edge in edgesSet:
                edge.build_landcost_samples()        

    def build_pylons(self, edgesSets):
        for edgesSet in edgesSets:
            for edge in edgesSet:
               edge.build_pylons()        

    def __init__(self, lattice):
        self.baseEdgesSets = self.base_edgessets(lattice)
        flattenedBaseEdges = util.fast_concat(self.baseEdgesSets)
        #self.plottableBaseEdges = [edge.as_plottable()
        #                           for edge in flattenedBaseEdges]
        self.iterative_filter()
        self.finishedEdgesSets = self.filteredEdgesSetsList[-1]
        self.build_landcost_samples(self.finishedEdgesSets)
        self.build_pylons(self.finishedEdgesSets)
        #flattenedFinishedEdges = util.fast_concat(self.finishedEdgesSets)
        #self.plottableFinishedEdges = [edge.as_plottable() for edge
        #                               in flattenedFinishedEdges]
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
    #plottableFinishedEdges = edgesSets.plottableFinishedEdges
    return finishedEdgesSets #[finishedEdgesSets, plottableFinishedEdges]

def get_edgessets(lattice):    
    #finishedEdgesSets, plottableFinishedEdges = cacher.get_object("edgessets",
    finishedEdgesSets = cacher.get_object("edgessets", build_edgessets,
                        [lattice], cacher.save_edgessets, config.edgesFlag)
    return finishedEdgesSets #[finishedEdgesSets, plottableFinishedEdges]

