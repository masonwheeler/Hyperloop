"""
Original Developer: Jonathan Ward

Purpose of Module: Provides a namespace for engineering and financial parameters

Last Modified: 09/02/15

Last Modifed By: Jonathan Ward

Last Modification Purpose: Created Module
"""


########################
#Engineering Parameters#
########################

PYLON_SPACING = 60.96 #Meters
MAX_SPEED = 326.0 #Meters/Second
MAX_TUBE_GRADE = 1.0 #Degrees

####################
#Comfort Parameters#
####################

MAX_LATERAL_ACCEL = 0.5 * 9.81 #Meters/Second^2
MAX_LONGITUDINAL_ACCEL = 0.5 * 9.81 #Meters/Second^2
MAX_VERTICAL_ACCEL = 0.3 * 9.81 #Meters/Second^2

######################
#Financial Parameters#
######################

PYLON_BASE_COST = 105.0 * 10.0**3 #Dollars
PYLON_COST_PER_METER = 1.5 * 10.0**3 #Dollars
TUBE_COST_PER_METER = 4.0 * 10.0**3 #Dollars
TUNNELING_COST_PER_METER = 32.0 * 10.0**3 #Dollars

##########################
#Speed Profile Parameters#
##########################

MIN_SPEED = MAX_SPEED / 2.0
JERK_TOL = 2.0

####################
#Derived Parameters#
####################

MAX_LATERAL_CURVATURE = MAX_LATERAL_ACCEL / MAX_SPEED**2 #Meters^{-1}
MAX_LONGITUDINAL_CURVATURE = MAX_LONGITUDINAL_ACCEL / MAX_SPEED**2 #Meters^{-1}
MAX_VERTICAL_CURVATURE = MAX_VERTICAL_ACCEL / MAX_SPEED**2 #Meters^{-1}
