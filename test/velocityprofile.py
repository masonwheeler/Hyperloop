"""
Original Developer: David Roberts
Purpose of Module: To generate the velocity profile of a route.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Removed unecessary lines and fixed formatting
"""

import math
import numpy as np
from scipy.interpolate import interp1d
import time


class VelocityProfile:
   x = 0 

