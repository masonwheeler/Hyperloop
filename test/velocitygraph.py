"""
Original Developer: David Roberts
Purpose of Module: To generate a discrete velocity profile.
Last Modified: 7/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

import math
import numpy as np


class VelocityGraph:
    velByArclength = []
    velByTime = []
    tripTime = 0
    comfortRating = 0

    def reparametrize_velocity(self):
        pass
  
    def velocity_to_tripTime(self, velByTime):
        pass
    
    def velocity_to_comfort(self, velByTime):
        pass
      
    def __init__(self, velByArcLength):
        self.velByArcLength = velByArcLength
        self.velByTime = self.reparametrize_velocity(velByArcLength)
        self.tripTime = self.velocity_to_triptime(self.velByTime)
        self.comfortRating = self.velocity_to_comfort(self.velByTime)
        
    

