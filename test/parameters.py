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

PYLON_SPACING = 100.0 #Meters
MAX_SPEED = 330.0 #Meters/Second

####################
#Comfort Parameters#
####################

MAX_LONGITUDINAL_ACCEL = 0.5 * 9.81 #Meters/Second^2
MAX_LATERAL_ACCEL = 0.5 * 9.81 #Meters/Second^2
MAX_VERTICAL_ACCEL = 0.3 * 9.81 #Meters/Second^2

######################
#Financial Parameters#
######################

LAND_PADDING = 30.0 #Meters
RIGHT_OF_WAY_LAND_COST = 0.0 #Dollars
TUNNELING_COST_PER_METER = 10000.0 #Dollars/Meter
PYLON_BASE_COST = 2000.0 #Dollars
PYLON_COST_PER_METER = 10000.0 #Dollars
TUBE_COST_PER_METER = 1000.0 #Dollars

#########################
#Tube Profile Parameters#
#########################
PYLON_HEIGHT_STEP_SIZE = 10.0 #Meters

##########################
#Speed Profile Parameters#
##########################

MIN_SPEED = MAX_SPEED / 2.0
JERK_TOL = 2
