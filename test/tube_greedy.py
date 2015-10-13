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
import visualize


VISUALIZE_LATTICE = True
VISUALIZE_EDGES = True
VISUALIZE_GRAPHS = True


def compute_tube_angle_constraint(length_scale, resolution):
    max_curvature = parameters.MAX_VERTICAL_CURVATURE
    tube_interpolator = smoothing_interpolate.bounded_error_graph_interpolation
    tube_angle_constraint = angle_constraint.compute_angle_constraint(
           length_scale, tube_interpolator, max_curvature, resolution)
    return tube_angle_constraint

def elevation_profile_to_tube_points_lattice(elevation_profile,
                           elevation_mesh_bisection_depth=None,
                          arc_length_mesh_bisection_depth=None):
    if elevation_mesh_bisection_depth == None:
        elevation_mesh_bisection_depth = 2
    if arc_length_mesh_bisection_depth == None:
        arc_length_mesh_bisection_depth = 2
    tube_points_lattice = tube_lattice.TubePointsLattice(elevation_profile,
           elevation_mesh_bisection_depth, arc_length_mesh_bisection_depth)
    if config.VISUAL_MODE and VISUALIZE_LATTICE:
        axes_equal = False
        land_elevations_points = [tube_points_lattice.arc_lengths, 
                                  tube_points_lattice.land_elevations]
        plottable_land_elevations = [land_elevations_points, 'b-']
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(plottable_land_elevations)

        lower_tube_envelope_points = [tube_points_lattice.arc_lengths,
                                      tube_points_lattice.lower_tube_envelope]
        plottable_lower_tube_envelope = [lower_tube_envelope_points, 'r-']
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(
                            plottable_lower_tube_envelope)
        upper_tube_envelope_points = [tube_points_lattice.arc_lengths,
                                      tube_points_lattice.upper_tube_envelope]
        plottable_upper_tube_envelope = [upper_tube_envelope_points, 'g-']
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(
                            plottable_upper_tube_envelope)

        plottable_lattice = tube_points_lattice.get_plottable_lattice('k.')
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(plottable_lattice)

        visualize.plot_objects(visualize.ELEVATION_PROFILE_PLOT_QUEUE,
                               axes_equal)
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
    return tube_points_lattice

def tube_points_lattice_to_tube_edges_sets(tube_points_lattice, max_grade):
    length_scale = tube_points_lattice.length_scale
    resolution = tube_points_lattice.resolution
    tube_angle_constraint = compute_tube_angle_constraint(length_scale,
                                                            resolution)
    tube_edges_sets = tube_edges.TubeEdgesSets(tube_points_lattice,
                                  tube_angle_constraint, max_grade) 
    if config.VISUAL_MODE and VISUALIZE_EDGES:
        print "tube angle constraint: " + str(tube_angle_constraint)
        axes_equal = False
        land_elevations_points = [tube_points_lattice.arc_lengths, 
                                  tube_points_lattice.land_elevations]
        plottable_land_elevations = [land_elevations_points, 'b-']
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(plottable_land_elevations)

        lower_tube_envelope_points = [tube_points_lattice.arc_lengths,
                                      tube_points_lattice.lower_tube_envelope]
        plottable_lower_tube_envelope = [lower_tube_envelope_points, 'r-']
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(
                            plottable_lower_tube_envelope)
        upper_tube_envelope_points = [tube_points_lattice.arc_lengths,
                                      tube_points_lattice.upper_tube_envelope]
        plottable_upper_tube_envelope = [upper_tube_envelope_points, 'g-']
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(
                            plottable_upper_tube_envelope)

        plottable_edges = tube_edges_sets.get_plottable_edges('k-')
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(plottable_edges)

        visualize.plot_objects(visualize.ELEVATION_PROFILE_PLOT_QUEUE,
                               axes_equal)
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
    return [tube_edges_sets, resolution]

def tube_edges_sets_to_tube_graphs(tube_edges_sets, resolution):
    tube_graphs_sets = tube_graphs.TubeGraphsSets(tube_edges_sets,
          smoothing_interpolate.bounded_error_graph_interpolation,
                                                       resolution)
    selected_tube_graphs = tube_graphs_sets.selected_graphs
    if config.VISUAL_MODE and VISUALIZE_GRAPHS:
        print "Num selected tube graphs: " + str(len(selected_tube_graphs))
        axes_equal = False
        land_elevations_points = [tube_points_lattice.arc_lengths, 
                                  tube_points_lattice.land_elevations]
        plottable_land_elevations = [land_elevations_points, 'b-']
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(plottable_land_elevations)

        lower_tube_envelope_points = [tube_points_lattice.arc_lengths,
                                      tube_points_lattice.lower_tube_envelope]
        plottable_lower_tube_envelope = [lower_tube_envelope_points, 'r-']
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(
                            plottable_lower_tube_envelope)
        upper_tube_envelope_points = [tube_points_lattice.arc_lengths,
                                      tube_points_lattice.upper_tube_envelope]
        plottable_upper_tube_envelope = [upper_tube_envelope_points, 'g-']
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(
                            plottable_upper_tube_envelope)

        plottable_tube_graphs = tube_graphs_sets.get_plottable_tube_graphs('k-')
        visualize.ELEVATION_PROFILE_PLOT_QUEUE += plottable_tube_graphs

        visualize.plot_objects(visualize.ELEVATION_PROFILE_PLOT_QUEUE,
                               axes_equal)
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
        visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
    return selected_tube_graphs 

def elevation_profile_to_tube_graphs(elevation_profile,
                   elevation_mesh_bisection_depth=None,
                  arc_length_mesh_bisection_depth=None):
    tube_points_lattice = elevation_profile_to_tube_points_lattice(
                 elevation_profile, elevation_mesh_bisection_depth=None,
                                   arc_length_mesh_bisection_depth=None)
    tube_edges_sets, resolution = tube_points_lattice_to_tube_edges_sets(
                          tube_points_lattice, parameters.MAX_TUBE_GRADE)
    selected_tube_graphs = tube_edges_sets_to_tube_graphs(tube_edges_sets,
                                                               resolution)
    return selected_tube_graphs
