"""
Original Developer:
   Jonathan Ward

Purpose of Module:
   To provide curvature functions

Last Modified:
   9/03/15

Last Modified By:
   Jonathan Ward

Last Modification Purpose:
   Created Module
"""

#Standard Modules:
import scipy.interpolate
import math
import numpy as np

#Our Modules:
import util

def get_derivative_values(spline, s_values):
    first_deriv = spline.derivative(n=1)
    second_deriv = spline.derivative(n=2)
    first_deriv_values = first_deriv(s_values)
    second_deriv_values = second_deriv(s_values)
    return [first_deriv_values, second_deriv_values]

def compute_curvature_array_2d(x_first_deriv_values, x_second_deriv_values,
                               y_first_deriv_values, y_second_deriv_values):
    array_length = x_first_deriv_values.size
    powers = np.empty(array_length)
    powers.fill(1.5)
    curvature_array_2d = np.divide(
        np.absolute(
            np.subtract(
                np.multiply(x_first_deriv_values,
                            y_second_deriv_values),
                np.multiply(y_first_deriv_values,
                            x_second_deriv_values)
            )
        ),
        np.power(
            np.add(
                np.square(x_first_deriv_values),
                np.square(y_first_deriv_values)
            ),
            powers
        )
    )
    return curvature_array_2d

def parametric_splines_2d_curvature(x_spline, y_spline, s_values):
    x_first_deriv_values, x_second_deriv_values = get_derivative_values(x_spline,
                                                                        s_values)
    y_first_deriv_values, y_second_deriv_values = get_derivative_values(y_spline,
                                                                        s_values)
    curvature_array_2d = compute_curvature_array_2d(
        x_first_deriv_values, x_second_deriv_values,
        y_first_deriv_values, y_second_deriv_values)
    return curvature_array_2d

def test_curvature_validity(curvature_array, curvature_threshhold):
    curvature_size = curvature_array.size
    curvature_threshhold_array = np.empty(curvature_size)
    curvature_threshhold_array.fill(curvature_threshhold)
    absolute_curvature_array = np.absolute(curvature_array)
    relative_curvature_array = np.subtract(absolute_curvature_array,
                                           curvature_threshhold_array)
    excess_curvature_array = relative_curvature_array.clip(min=0)
    total_excess_curvature = np.sum(excess_curvature_array)
    is_curvature_valid = (total_excess_curvature == 0)
    return is_curvature_valid

def curvature_test_2d(x_spline, y_spline, s_values, curvature_threshold):
    splines_curvature = parametric_splines_2d_curvature(x_spline, y_spline,
                                                        s_values)
    print "spline curvature: " 
    print np.amax(splines_curvature)   
    is_curvature_valid = test_curvature_validity(splines_curvature,
                                               curvature_threshold)
    return is_curvature_valid

