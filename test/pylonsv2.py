"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the pylon cost component of an edge
Last Modified: 8/12/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To implement a non naive pylon cost method.
"""

import util
import config
import graphs

class Pylon:
    def __init__(self, pylonHeight, landElevation, pylonCost, geospatials,
                                                              latlngs):
        self.pylonHeight = pylonHeight
        self.landElevation = landElevation
        self.pylonCost = pylonCost
        self.geospatials = geospatials
        self.latlngs = latlngs

class PotentialPylons:

class TubeGraph:
    def __init__(self, numEdges, pylonCost, triptimeExcess, startId, endId,
                                                                     pylons):
        self.numEdges = numEdges
        self.pylonCost = pylonCost
        self.triptimeExcess = triptimeExcess
        self.startId = startId
        self.endId = endId
        self.pylons = pylons
    
class TubePath:
    
    
