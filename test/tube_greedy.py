"""
Original Developer: Jonathan Ward
"""

import angle_constraint
import curvature
import parameters
import smoothing_interpolate
import tube_edges
import tube_graphs
import tube_lattice


def compute_tube_angle_constraint(tube_point_arc_length_step_size,
                                   tube_point_elevation_step_size):
    length_scale = tube_point_arc_length_step_size
    resolution = tube_point_elevation_step_size
    max_curvature = curvature.compute_curvature_threshold(parameters.MAX_SPEED,
                                                 parameters.MAX_VERTICAL_ACCEL)
    tube_interpolator = smoothing_interpolate.bounded_error_graph_interpolation
    tube_angle_constraint = angle_constraint.compute_angle_constraint(
           length_scale, tube_interpolator, max_curvature, resolution)
    return tube_angle_constraint

def elevation_profile_to_tube_graphs(elevation_profile,
                   tube_point_elevation_step_size=None):
    if tube_point_elevation_step_size == None:
        tube_point_elevation_step_size = parameters.PYLON_HEIGHT_STEP_SIZE
    tube_point_arc_length_step_size = elevation_profile.elevation_point_spacing
    tube_angle_constraint = compute_tube_angle_constraint(
        tube_point_arc_length_step_size, tube_point_elevation_step_size)
    tube_points_lattice = tube_lattice.TubePointsLattice(elevation_profile)
    #tube_points_lattice.visualize()
    tube_edges_sets = tube_edges.TubeEdgesSets(tube_points_lattice,
                                             tube_angle_constraint)
    tube_graphs_sets = tube_graphs.TubeGraphsSets(tube_edges_sets)
    selected_tube_graphs = tube_graphs_sets.selected_graphs
    return selected_tube_graphs
