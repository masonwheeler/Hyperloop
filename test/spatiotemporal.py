"""
Original Developer: Jonathan Ward
"""


import config
import spatiotemporal_paths_4d
import speed_profile_match_landscapes


if config.VISUAL_MODE:
    import visualize
    VISUALIZE_COMFORT = False
    VISUALIZE_SPEEDS_BY_ARC_LENGTH = True
    VISUALIZE_SPEEDS_BY_TIME = True
    VISUALIZE_ACCELS_BY_TIME = False
    

def paths_3d_to_paths_4d(spatial_paths_sets_3d):
    spatiotemporal_paths_sets_4d = \
        spatiotemporal_paths_4d.get_spatiotemporal_paths_sets_4d(
            spatial_paths_sets_3d, speed_profile_match_landscapes.SpeedProfile)
    if config.VISUAL_MODE:
        for path_4d in spatiotemporal_paths_sets_4d.selected_paths:
            if VISUALIZE_COMFORT:
                are_axes_equal = False
                plottable_comfort_profile = \
                    path_4d.get_plottable_comfort_profile('b-')
                visualize.COMFORT_PROFILE_PLOT_QUEUE.append(
                                      plottable_comfort_profile)
                visualize.plot_objects(visualize.COMFORT_PROFILE_PLOT_QUEUE,
                                       are_axes_equal)
                visualize.COMFORT_PROFILE_PLOT_QUEUE.pop()
            if VISUALIZE_SPEEDS_BY_ARC_LENGTH:
                are_axes_equal = False
                plottable_speeds_by_arc_length = \
                    path_4d.get_plottable_speeds_by_arc_length('g-')
                visualize.SPEED_PROFILE_PLOT_QUEUE.append(
                               plottable_speeds_by_arc_length)
                visualize.plot_objects(visualize.SPEED_PROFILE_PLOT_QUEUE,
                                       are_axes_equal)
                visualize.SPEED_PROFILE_PLOT_QUEUE.pop()
            if VISUALIZE_SPEEDS_BY_TIME:
                are_axes_equal = False
                plottable_speeds_by_time = \
                    path_4d.get_plottable_speeds_by_time('r-')
                visualize.SPEED_PROFILE_PLOT_QUEUE.append(
                                  plottable_speeds_by_time)
                visualize.plot_objects(visualize.SPEED_PROFILE_PLOT_QUEUE,
                                       are_axes_equal)
                visualize.SPEED_PROFILE_PLOT_QUEUE.pop()
            if VISUALIZE_ACCELS_BY_TIME:
                pass
    return spatiotemporal_paths_sets_4d
    
