def get_derivative_values_pchip(pchip_spline, s_values):
    first_deriv = pchip_spline.derivative(1)
    second_deriv = pchip_spline.derivative(2)
    first_deriv_values = first_deriv(s_values)
    second_deriv_values = second_deriv(s_values)
    return [first_deriv_values, second_deriv_values]

def compute_explicit_curvature(first_deriv_values, second_deriv_values):
    s_length = first_deriv_values.size
    powers = np.empty(s_length)
    powers.fill(1.5)
    ones = np.ones(s_length)
    curvature_array = np.divide(
        np.absolute(second_deriv_values),
        np.power(
            np.add(
                ones,
                np.square(first_deriv_values)
            ),
            powers
        )
    )
    return curvature_array

def compute_curvature_pchip(pchip_spline, s_values):
    first_deriv_values, second_deriv_values = get_derivative_values_pchip(
                                                   pchip_spline, s_values)
    curvature_array = compute_explicit_curvature(first_deriv_values,
                                                second_deriv_values)
    return curvature_array

def compute_curvature_array_3d(x_first_deriv_values, x_second_deriv_values,
                               y_first_deriv_values, y_second_deriv_values,
                               z_first_deriv_values, z_second_deriv_values):
    s_length = x_first_deriv_values.size
    powers = np.empty(s_length)
    powers.fill(1.5)
    first_term = np.square(
        np.subtract(
            np.multiply(z_second_deriv_values, y_first_deriv_values),
            np.multiply(y_second_deriv_values, z_first_deriv_values)
        )
    )
    second_term = np.square(
        np.subtract(
            np.multiply(x_second_deriv_values, z_first_deriv_values),
            np.multiply(z_second_deriv_values, x_first_deriv_values)
        )
    )
    third_term = np.square(
        np.subtract(
            np.multiply(y_second_deriv_values, x_first_deriv_values),
            np.multiply(x_second_deriv_values, y_first_deriv_values)
        )
    )
    curvature_array_3d = np.divide(
        np.sqrt(
            np.add(
                np.add(first_term, second_term),
                third_term
            )
        ),
        np.power(
            np.add(
                np.add(
                    np.square(x_first_deriv_values),
                    np.square(y_first_deriv_values)
                ),
                np.square(z_first_deriv_values)
            ),
            powers
        )
    )
    return curvature_array_3d

def parametric_splines_3d_curvature(x_spline, y_spline, z_spline, s_values):
    x_first_deriv_values, x_second_deriv_values = get_derivative_values(x_spline,
                                                                        s_values)
    y_first_deriv_values, y_second_deriv_values = get_derivative_values(y_spline,
                                                                        s_values)
    z_first_deriv_values, z_second_deriv_values = get_derivative_values(z_spline,
                                                                        s_values)
    curvature_array3d = compute_curvature_array_3d(
        x_first_deriv_values, x_second_deriv_values,
        y_first_deriv_values, y_second_deriv_values,
        z_first_deriv_values, z_second_deriv_values)
    return curvature_array3d

def parametric_splines_vertical_and_lateral_curvatures(x_spline, y_spline,
                                                       z_spline, s_values):
    x_first_deriv_values, x_second_deriv_values = get_derivative_values(x_spline,
                                                                        s_values)
    y_first_deriv_values, y_second_deriv_values = get_derivative_values(y_spline,
                                                                        s_values)
    z_first_deriv_values, z_second_deriv_values = get_derivative_values(z_spline,
                                                                        s_values)
    vertical_curvature_array = compute_explicit_curvature(z_first_deriv_values,
                                                          z_second_deriv_values)
    lateral_curvature_array = compute_curvature_array_2d(
        x_first_deriv_values, x_second_deriv_values,
        y_first_deriv_values, y_second_deriv_values)
    return [vertical_curvature_array, lateral_curvature_array]

def effective_max_allowed_vels(x_spline, y_spline, z_spline, s_values):
    vertical_curvature_array, lateral_curvature_array = \
        parametric_splines_vertical_and_lateral_curvatures(x_spline, y_spline,
                                                           z_spline, s_values)
    max_allowed_vels_vertical = \
        vertical_curvature_array_to_max_allowed_vels(
            vertical_curvature_array)
    max_allowed_vels_lateral = \
        lateral_curvature_array_to_max_allowed_vels(
            lateral_curvature_array)
    effective_max_allowed_vels = np.minimum(max_allowed_vels_vertical,
                                            max_allowed_vels_lateral)
    return effective_max_allowed_vels

def effective_max_allowed_vels_1d(z_spline, s_values):
    z_first_deriv_values, z_second_deriv_values = get_derivative_values(z_spline,
                                                                        s_values)
    vertical_curvature_array = compute_explicit_curvature(z_first_deriv_values,
                                                          z_second_deriv_values)
    max_allowed_vels = vertical_curvature_array_to_max_allowed_vels(
        vertical_curvature_array)
    return max_allowed_vels

def compute_curvature_threshold(speed, max_acceleration):
    curvature_threshold = max_acceleration / speed**2
    return curvature_threshold

