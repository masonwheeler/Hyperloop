"""
Original Developer: Jonathan Ward
"""

# Custom Modules:
import parameters

def compute_tube_point_pylon_cost(tube_point):
    if not tube_point.is_underground:
        height_cost = pylon_height * parameters.PYLON_COST_PER_METER
        base_cost = parameters.PYLON_BASE_COST
        pylon_cost = height_cost + base_cost
    else:
        pylon_cost = 0
    return pylon_cost

def compute_tube_profile_total_pylon_cost(tube_profile):
    pylons_costs = [compute_tube_point_pylon_cost(tube_point)
                    for tube_point in tube_profile.tube_points]
    pylons_total_cost = sum(pylons_costs)
    return pylons_total_cost
