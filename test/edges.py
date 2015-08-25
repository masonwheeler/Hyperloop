"""
Original Developer: Jonathan Ward
Purpose of Module: To build edges with associated cost and elevation data
                   from pairs of lattice points.
Last Modified: 8/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To test out pylonsv2
"""

#Standard Modules:
import math
import time

#Our Modules
import cacher
import config
import elevation
import landcover
import pylons
import proj
#import tube
import util
import visualize

class Edge:
    """
    Object that stores pairs of lattice points, the associated data
    
    Stores whether the line between the pair of points is in the right of way.
    Stores whether the edge is compatible with any other edges.
    """
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

    def get_elevation_profile(self):        
        startGeospatial, endGeospatial = self.geospatials
        pylonSlicesGeospatials, pylonSliceDistances = util.build_grid(
          self.geospatialVector, config.pylonSpacing, startGeospatial)     
        self.elevationProfile = elevation.get_elevation_profile(
                           pylonSlicesGeospatials, pylonSliceDistances)

    def build_pylons(self):
        #if config.visualMode:
        #    visualize.visualize_elevation_profile(elevationProfile)
        #print("started building tubegraphs")
        #tubeGraphs = tube.elevation_profile_to_tube_graphs(elevationProfile)         
        #print("finished building tubegraphs")
        #for tubeGraph in tubeGraphs:
        #    print("pylon cost :" + tubeGraph.pylonCost)
        #    print("tube cost :" + tubeGraph.tubeCost)
      
        newPylons = [{"geospatial" : elevationPoint["geospatial"],
                       "latlng" : elevationPoint["latlng"],
                       "elevation" : elevationPoint["landElevation"],
                       "pylonHeight" : 0,
                       "pylonCost" : 0}
                       for elevationPoint in self.elevationProfile]      
        pylons.build_pylons(newPylons)
        pylons.get_pyloncosts(newPylons)        
        self.pylonCost = pylons.edge_pyloncost(newPylons)                           

    def build_land_cost_samples(self):
        if self.isInRightOfWay:
            self.landCost = config.rightOfWayLandCost          
        else:
            startGeospatial, endGeospatial = self.geospatials
            landcoverGeospatials, distances = util.build_grid(
              self.geospatialVector, config.landPointSpacing, startGeospatial)
            landcoverLatLngs = proj.geospatials_to_latlngs(landcoverGeospatials,
                                                                    config.proj)
            landcoverCostDensities = landcover.landcover_cost_densities(
                                                           landcoverLatLngs)
            self.landCost = landcover.cost_densities_to_landcost(
                                              landcoverCostDensities)

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
    def as_dict(self):
        edgeDict = {"geospatials" : self.geospatials,
                    "latlngs" : self.latlngs,
                    "landCost" : self.landCost,
                    "pylonCost" : self.pylonCost}
        return edgeDict

    def display(self):
        print("The edge's cost is: " + str(self.cost) + ".")
        print("The edge's length is: " + str(self.length) + ".")
        print("The edge's lat-lng coords are: " + str(self.latlngCoords) + ".")        
        print("The edge's xy coords are: " + str(self.geospatialCoords) + ".")
        print("The edge's angle is: " + str(self.angle) + " degrees.")

class EdgesSets:
    baseEdgesSets = []
    filteredEdgesSetsList = []
    finishedEdgesSets = []
    
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
        util.smart_print("The original number of spatial edges: " +
                          str(oldNumEdges))
         
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
            util.smart_print("The number of spatial edges is now: " +
                             str(newNumEdges))
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
    
    def build_land_cost_samples(self, edgesSets):
        for edgesSet in edgesSets:
            for edge in edgesSet:
                edge.build_land_cost_samples()        

    def build_pylons(self, edgesSets):
        for edgesSet in edgesSets:
            for edge in edgesSet:
               edge.build_pylons()       

    def get_elevation_profiles(self, edgesSets):
        for edgesSet in edgesSets:
            for edge in edgesSet:
                edge.get_elevation_profile()

    def __init__(self, lattice):
        self.baseEdgesSets = self.base_edgessets(lattice)
        flattenedBaseEdges = util.fast_concat(self.baseEdgesSets)
        self.iterative_filter()
        self.filteredEdgesSets = self.filteredEdgesSetsList[-1]        
        print("finished building edges")
        t0 = time.time()
        self.get_elevation_profiles(self.filteredEdgesSets)  
        t1 = time.time()
        print("attaching elevations took " + str(t1 - t0) + " seconds.")
        t0 = time.time()
        self.build_land_cost_samples(self.finishedEdgesSets)
        t1 = time.time()
        print("attaching land cost took " + str(t1 - t0) + " seconds.")
        #self.build_pylons(self.finishedEdgesSets)
        #print("finished attaching pylon cost")

def build_pylons(edgesSets):
    for edgesSet in edgesSets:
        for edge in edgesSet:
            edge.build_pylons()

def build_land_cost_samples(edgesSets):
    for edgesSet in edgesSets:
        for edge in edgesSet:
            edge.build_land_cost_samples()        

def build_edgessets(lattice):
    edgesSets = EdgesSets(lattice)
    finishedEdgesSets = edgesSets.filteredEdgesSets
    return finishedEdgesSets

def get_edgessets(lattice):    
    finishedEdgesSets = cacher.get_object("edgessets", build_edgessets,
                        [lattice], cacher.save_edgessets, config.edgesFlag)
    return finishedEdgesSets

