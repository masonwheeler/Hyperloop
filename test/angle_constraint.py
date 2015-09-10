"""
Original Developer: 
    Jonathan Ward
"""


def test_path_points(path_points):
    sampled_path_points = interpolate.sample_path(path_points, 500)
    #print("sampled points: " + str(sampled_path_points))
                                           #config.BASE_RESOLUTION)
    x_spline, y_spline, s_values = interpolate.interpolate_points_2d(
                                                            sampled_path_points)
    curvature_array_2d = curvature.parametric_splines_2d_curvature(
                                            x_spline, y_spline, s_values)
    curvature_threshold = curvature.compute_curvature_threshold(
                                            parameters.MAX_SPEED/2.0,
                                            parameters.MAX_LATERAL_ACCEL)
    is_curvature_valid = curvature.test_curvature_validity(
                        curvature_array_2d, curvature_threshold)
    return is_curvature_valid

def compute_spatial_degree_constraint(spatial_lattice):
    spatial_degree_constraint = 90
    angle = math.radians(spatial_degree_constraint)
    length = spatial_lattice.spatial_x_spacing
    origin = [0, 0]
    pointA = [length, 0]
    pointB = util.round_nums([math.cos(angle) * length,
                              math.sin(angle) * length])
    path_points = [pointA, origin, pointB]
    while not SpatialEdgesSets.test_path_points(path_points):
        print(spatial_degree_constraint)
        spatial_degree_constraint -= 1
        angle = math.radians(180 - spatial_degree_constraint)
        pointB = [math.cos(angle) * length, math.sin(angle) * length]
        path_points = [pointA, origin, pointB]
    return spatial_degree_constraint

