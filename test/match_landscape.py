"""
Original Developer: David Roberts
Purpose of Module: To build height/velocity profiles satisfying comfort,
                    and volatility constraints.
Last Modified: 8/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify naming and add docstrings
"""

# Standard Modules
import numpy as np

# Our Modules
import util
import config
import clothoid
import parameters
import proj
import elevation


def sort_indices(z, Type):
    z_indices = range(len(z))
    if Type == "elevation":
        return sorted(z_indices, key=lambda i: z[i], reverse=True)
    elif Type == "velocity":
        return sorted(z_indices, key=lambda i: z[i], reverse=False)


def gen_landscape(x, Type):
    s = [0] * len(x)
    for i in range(0, len(x) - 1):
        s[i + 1] = s[i] + np.linalg.norm(x[i + 1] - x[i])

    if Type == "elevation":
        xlnglat = proj.geospatials_to_latlngs(x, config.PROJ)
        z = elevation.usgs_elevation(xlnglat)

    elif Type == "velocity":
        R = [util.points_to_radius(x[i - 1:i + 2])
             for i in range(1, len(x) - 1)]
        z = [0] + [min(np.sqrt(r * parameters.MAX_LATERAL_ACCEL),
                       parameters.MAX_SPEED) for r in R] + [0]

    return [s, z]


def match_landscape(s, z, Type, tradeoffs):
    # the profile initializes as delta-z.
    K = [0, len(z) - 1]

    # we now sort the remaining landscape.
    J = sort_indices(z[1:len(z) - 1], Type)
    J = [j + 1 for j in J]
    cached = [[0 for i in range(len(z))] for i in range(len(z))]

    def bad(index, Type):
        # append newcomer to list; try it on for size
        new = util.sorted_insert(index, K)
        result = test(K[new - 1], K[new], Type) or test(K[new],
                                                        K[new + 1], Type)  # how did we do?
        K.pop(new)  # return list back to normal
        return result

    def test(i, j, Type):
        if cached[i][j]:
            return True
        elif Type == "elevation":
            cached[i][j] = cached[j][i] = True
            slopeConstraint = tradeoffs

            # def curvature(i, j):  # Computes the curvature of the clothoid
            #     x0, x1 = [s[i], s[j]]
            #     y0, y1 = [z[i], z[j]]
            #     tht0, tht1 = [0, 0]
            #     k, K, L = clothoid.build_clothoid(x0, y0, tht0, x1, y1, tht1)
            #     extremal_curvatures = [k + L * K, k]
            #     return max(np.absolute(extremal_curvatures))
            # return curvature(i, j) > curvature_tol
            return np.absolute((z[i]-z[j])/(s[i] - s[j])) > slopeConstraint

        elif Type == "velocity":
            cached[i][j] = cached[j][i] = True
            dz = np.absolute(z[j] - z[i])
            ds = s[j] - s[i]
            v = (z[j] + z[i]) / 2

            C = tradeoffs[0] / v
            D = tradeoffs[1] / v**2

            def dz_tol(s):
                if s < 2 * C / D:
                    return (s / 2)**2 * D
                else:
                    return (s - C / D) * C
            return dz > dz_tol(ds)

    def match_point():
        i = 0
        while bad(J[i], Type) and i < len(J) - 1:
            i += 1
        if i == len(J) - 1:
            # print "Exhausted the landscape. Could not find a point to match."
            return "Exhausted the landscape. Could not find a point to match."
        else:
            util.sorted_insert(J.pop(i), K)
            return "Success! See if we can match another point."

    #l = 0
    while match_point() == "Success! See if we can match another point.":
        #l += 1
        # print "matched the "+ str(l)+ "th point."
        pass
    return [[s[k] for k in K], [z[k] for k in K]]

def match_landscape_v1(s, z, Type):
    # the profile initializes as delta-z.
    K = [0, len(z) - 1]

    # we now sort the remaining landscape.
    J = sort_indices(z[1:len(z) - 1], Type)
    J = [j + 1 for j in J]
    cached = [[0 for i in range(len(z))] for i in range(len(z))]

    def bad(index, Type):
        # append newcomer to list; try it on for size
        new = util.sorted_insert(index, K)
        result = test(K[new - 1], K[new], Type) or test(K[new],
                                                        K[new + 1], Type)  # how did we do?
        K.pop(new)  # return list back to normal
        return result

    def test(i, j, Type):
        if cached[i][j]:
            return True
        elif Type == "elevation":
            cached[i][j] = cached[j][i] = True
            curvature_tol = parameters.MAX_LINEAR_ACCEL / \
                            parameters.MAX_SPEED**2

            def curvature(i, j):  # Computes the curvature of the clothoid
                x0, x1 = [s[i], s[j]]
                y0, y1 = [z[i], z[j]]
                tht0, tht1 = [0, 0]
                k, K, L = clothoid.build_clothoid(x0, y0, tht0, x1, y1, tht1)
                extremal_curvatures = [k + L * K, k]
                return max(np.absolute(extremal_curvatures))
            return curvature(i, j) > curvature_tol

        elif Type == "velocity":
            cached[i][j] = cached[j][i] = True
            dz = np.absolute(z[j] - z[i])
            ds = s[j] - s[i]
            v = (z[j] + z[i]) / 2

            C = parameters.MAX_LINEAR_ACCEL / v
            D = config.JERK_TOL / v**2

            def dz_tol(s):
                if s < 2 * C / D:
                    return (s / 2)**2 * D
                else:
                    return (s - C / D) * C
            return dz > dz_tol(ds)

    def match_point():
        i = 0
        while bad(J[i], Type) and i < len(J) - 1:
            i += 1
        if i == len(J) - 1:
            # print "Exhausted the landscape. Could not find a point to match."
            return "Exhausted the landscape. Could not find a point to match."
        else:
            util.sorted_insert(J.pop(i), K)
            return "Success! See if we can match another point."

    #l = 0
    while match_point() == "Success! See if we can match another point.":
        #l += 1
        # print "matched the "+ str(l)+ "th point."
        pass
    return [[s[k] for k in K], [z[k] for k in K]]

