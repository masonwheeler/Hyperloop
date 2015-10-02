"""
Original Developer: Jonathan Ward
"""

import tube
import tube_profile_match_landscapes

def tube_builder(elevation_profile):
    tube_profile = tube_profile_match_landscapes.TubeProfileMatchLandscapes(
                                                          elevation_profile)
    route_tube = tube.Tube(tube_profile)
    return route_tube
