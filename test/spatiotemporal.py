"""
Original Developer: Jonathan Ward
"""


import config
import spatiotemporal_paths_4d
import speed_profile_match_landscapes


if config.VISUAL_MODE:
    import visualize
    VISUALIZE_COMFORT = True
    VISUALIZE_VELOCITY = True
    VISUALIZE_ACCELERATION = False
    

def paths_3d_to_paths_4d(spatial_paths_sets_3d):
    spatiotemporal_paths_sets_4d = \
        spatiotemporal_paths_4d.get_spatiotemporal_paths_sets_4d(
            spatial_paths_sets_3d, speed_profile_match_landscapes.SpeedProfile)
    if config.VISUAL_MODE:
        if VISUALIZE_COMFORT:
            pass
        if VISUALIZE_VELOCITY:
            pass
        if VISUALIZE_ACCELERATION:
            pass
    return spatiotemporal_paths_sets_4d
    
