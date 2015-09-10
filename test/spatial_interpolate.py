"""
Original Developer:
    Jonathan Ward
"""

import advanced_interpolate as interp
import interpolate

def spatial_interpolation_v2(graph_geospatials):
    sampled_geospatials = interpolate.sample_path(graph_geospatials,
                                         geospatial_sample_distance)
    arc_lengths = 0 #!!
    x_array, y_array = points_2d_to_arrays(sampled_geospatials)
    num_points = len(sampled_geospatials)
    s_values = interpolate.get_s_values(num_points)
    x_spline, y_spline = interpolate.interpolating_splines_2d(x_array,
                                                     y_array, s_values)
    x_values = interpolate.get_spline_values(x_spline, s_values)
    y_values = interpolate.get_spline_values(y_spline, s_values)
    interpolating_geospatials = [x_values, y_values]
    return [interpolating_geospatials, arc_lengths]

def quintic(graph_geospatials):
    interpolating_geospatials_array = interp.para_super_q(
                                        graph_geospatials, 25)
    interpolating_geospatials = interpolating_geospatials_array.tolist()
    arc_lengths = util.compute_arc_lengths(interpolating_geospatials)
    return [interpolating_geospatials, arc_lengths]


