"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the pylon cost component of an edge
Last Modified: 7/23/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add support for tube heights.
"""

import util
import config


def build_pylons(pylon_locations):
    pylon_locations_by_elevation = sorted(pylon_locations,
                                          key=lambda pylon_location: pylon_location["elevation"])
    highest_pylon_location = pylon_locations_by_elevation[-1]
    highest_elevation = highest_pylon_location["elevation"]

    for pylon_location in pylon_locations:
        pylon_location["pylon_height"] = \
            highest_elevation - pylon_location["elevation"]

    return pylon_locations


def get_pyloncosts(pylon_locations):
    for pylon_location in pylon_locations:
        pylon_location["pylon_cost"] = (config.pylon_base_cost +
                                        pylon_location["pylon_height"] * config.pylon_cost_per_meter)
    return pylon_locations


def edge_pyloncost(pylon_locations):
    edge_pylon_cost = sum([pylon_location["pylon_cost"] for pylon_location
                           in pylon_locations])
    return edge_pylon_cost
