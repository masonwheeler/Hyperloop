"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import numpy as np

# Custom Modules:
import parameters
import util

def compute_arc_length_steps(points):
    """Computes the arclength separations between each point in a path of points
    """
    pairs = util.to_pairs(points)
    vectors = [util.edge_to_vector(pair) for pair in pairs]
    arc_length_steps = [np.linalg.norm(vector) for vector in vectors]
    return arc_length_steps

def compute_total_arc_length(points):
    """Compute the total arclength of the path defined by the points
    """
    arc_length_steps = compute_arc_length_steps(points)
    total_arc_length = np.sum(arc_length_steps)
    return total_arc_length

def compute_tube_cost_v1(tube_coords):
    tube_length = compute_total_arc_length(tube_coords)
    tube_cost = parameters.TUBE_COST_PER_METER * tube_length
    return tube_cost
    
def compute_tube_cost_v1(tube_profile):
    tube_cost = parameters.TUBE_COST_PER_METER * tube_profile.tube_length
    return tube_cost
