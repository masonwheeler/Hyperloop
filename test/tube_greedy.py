"""
Original Developer: Jonathan Ward
"""

# Custom Modules:
import angle_constraint
import config
import curvature
import parameters
import smoothing_interpolate
import tube_edges
import tube_graphs
import tube_lattice


VISUALIZE_LATTICE = True
VISUALIZE_EDGES = True


def compute_tube_angle_constraint(length_scale, resolution):
    max_curvature = curvature.compute_curvature_threshold(parameters.MAX_SPEED,
                                                 parameters.MAX_VERTICAL_ACCEL)
    tube_interpolator = smoothing_interpolate.bounded_error_graph_interpolation
    tube_angle_constraint = angle_constraint.compute_angle_constraint(
           length_scale, tube_interpolator, max_curvature, resolution)
    return tube_angle_constraint

def elevation_profile_to_tube_points_lattice(elevation_profile,
                           elevation_mesh_bisection_depth=None,
                          arc_length_mesh_bisection_depth=None):
    if elevation_mesh_bisection_depth == None:
        elevation_mesh_bisection_depth = 1
    if arc_length_mesh_bisection_depth == None:
        arc_length_mesh_bisection_depth = 1
    tube_points_lattice = tube_lattice.TubePointsLattice(elevation_profile,
           elevation_mesh_bisection_depth, arc_length_mesh_bisection_depth)
    if config.VISUAL_MODE and VISUALIZE_LATTICE:
        tube_points_lattice.visualize()
    return tube_points_lattice

def tube_points_lattice_to_tube_edges_sets(tube_points_lattice):
    length_scale = tube_points_lattice.arc_length_step_size
    resolution = tube_points_lattice.elevation_step_size
    tube_angle_constraint = compute_tube_angle_constraint(length_scale,
                                                            resolution)
    tube_edges_sets = tube_edges.TubeEdgesSets(tube_points_lattice,
                                             tube_angle_constraint) 
    if config.VISUAL_MODE and VISUALIZE_EDGES:       
        print "tube angle constraint: " + str(tube_angle_constraint)
    return [tube_edges_sets, resolution]

def tube_edges_sets_to_tube_graphs(tube_edges_sets, resolution):
    tube_graphs_sets = tube_graphs.TubeGraphsSets(tube_edges_sets,
          smoothing_interpolate.bounded_error_graph_interpolation,
                                                       resolution)
    selected_tube_graphs = tube_graphs_sets.selected_graphs
    return selected_tube_graphs 

def elevation_profile_to_tube_graphs(elevation_profile,
                   elevation_mesh_bisection_depth=None,
                  arc_length_mesh_bisection_depth=None):
    tube_points_lattice = elevation_profile_to_tube_points_lattice(
                 elevation_profile, elevation_mesh_bisection_depth=None,
                                   arc_length_mesh_bisection_depth=None)
    tube_edges_sets, resolution = tube_points_lattice_to_tube_edges_sets(
                                                     tube_points_lattice)
    selected_tube_graphs = tube_edges_sets_to_tube_graphs(tube_edges_sets,
                                                               resolution)
    return selected_tube_graphs
