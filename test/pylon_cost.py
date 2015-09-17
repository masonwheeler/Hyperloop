"""
Original Developer: Jonathan Ward
"""

# Custom Modules:
import parameters

def compute_pylon_cost_v1(pylon_height):
    if pylon_height >= 0:
        height_cost = pylon_height * parameters.PYLON_COST_PER_METER
    else:
        height_cost = -pylon_height * 5 * parameters.PYLON_COST_PER_METER
    pylon_cost = parameters.PYLON_BASE_COST + height_cost
    return pylon_cost

def compute_pylons_total_cost_v1(pylon_heights):
    pylons_total_cost = sum(map(compute_pylon_cost_v1, pylon_heights))
    return pylons_total_cost
