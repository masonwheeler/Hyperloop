"""
Original Developer: Jonathan Ward
"""

# Custom Modules:
import parameters
import util

def compute_tube_cost_v1(tube_coords):
    tube_length = util.compute_total_arc_length(tube_coords)
    tube_cost = parameters.TUBE_COST_PER_METER * tube_length
    return tube_cost
    
