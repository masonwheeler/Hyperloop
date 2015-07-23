"""
Original Developer: David Roberts
Purpose of Module: To determine the pylon cost component of an edge
Last Modified: 7/21/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify naming and fix formatting.
"""

#Standard Modules:
import math 
import numpy as np
import random
import time

#Our Modules:
import util
import config


def build_pylons(pylonLocations):
    pylonLocationsByElevation = sorted(pylonLocations,
        key=lambda pylonLocation : pylonLocation["elevation"])
    highestPylonLocation = pylonLocationsByElevation[-1]
    highestElevation = highestPylonLocation["elevation"]
    for pylonLocation in pylonLocations:
        pylonLocation["pylonHeight"] = \
          highestElevation - pylonLocation["elevation"]
    return pylonLocations
        
def get_pyloncosts(pylonLocations):
    for pylonLocation in pylonLocations:
        pylonLocation["pylonCost"] = (config.pylonBaseCost + 
            pylonLocation["pylonHeight"] * config.pylonCostPerMeter)
    return pylonLocations

def edge_pyloncost(pylonLocations):
    edgePylonCost = sum([pylonLocation["pylonCost"] for pylonLocation
                         in pylonLocations])
    return edgePylonCost

