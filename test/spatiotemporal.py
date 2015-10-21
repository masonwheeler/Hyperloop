"""
Original Developer: Jonathan Ward
"""

import config
import spatiotemporal_paths_4d
import speed_profile_match_landscapes as speed_profile

def paths_3d_to_paths_4d(spatial_paths_sets_3d):
    spatiotemporal_paths_sets_4d = \
        spatiotemporal_paths_4d.get_spatiotemporal_paths_sets_4d(
            spatial_paths_sets_3d, speed_profile.SpeedProfile)
    if config.VISUAL_MODE:
        pass
    return spatiotemporal_paths_sets_4d
    
