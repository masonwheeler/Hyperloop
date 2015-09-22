"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import scipy.interpolate

# Custom Modules:
import curvature
import match_landscape

def get_tube_waypoints_v1(arc_lengths, land_elevations):
    arc_length_waypoints, tube_elevation_waypoints = \
        match_landscape.match_landscape_v1(arc_lengths, land_elevations,
                                                            "elevation")
    return arc_length_waypoints, tube_elevation_waypoints
    

def tube_pchip(arc_length_waypoints, tube_elevation_waypoints, arc_lengths):
    tube_spline = scipy.interpolate.PchipInterpolator(arc_length_waypoints,
                                                  tube_elevation_waypoints)
    tube_curvature = curvature.compute_curvature_pchip(tube_spline, arc_lengths)
    tube_elevations = tube_spline(arc_lengths)
    return [tube_elevations, tube_curvature]
