import random
import clothoid
import matplotlib.pyplot as plt
import numpy as np


def random_subset_track(a, N, K):
    used = [False] * N
    result = []

    for i in range(0, K):
        # get a random element between 0 and N.
        j = int(random.random() * N)
        while (used[j]):
            j = int(random.random() * N)
        result.append(j)
        used[j] = True

    return result


# s = sorted(list(set([random.uniform(0,100) for i in range(10)])))
# z = [random.uniform(0,150) for i in range(len(s))]


def curvature(i, j):  # Computes the curvature of the clothoid
    x0, x1 = [s[i], s[j]]
    y0, y1 = [z[i], z[j]]
    tht0, tht1 = [0, 0]
    k, K, L = clothoid.build_clothoid(x0, y0, tht0, x1, y1, tht1)
    extremal_curvatures = [k + L * K, k]
    return max(np.absolute(extremal_curvatures))


def plot_clothoid(i, j):
    x0, x1 = [s[i], s[j]]
    y0, y1 = [z[i], z[j]]
    tht0, tht1 = [0, 0]
    k, K, L = clothoid.build_clothoid(x0, y0, tht0, x1, y1, tht1)
    s_vals = np.arange(0, L, 1)
    x_vals = [s[i] + s_val *
              clothoid.eval_x_y(K * s_val**2, k * s_val, 0, 1)[0][0] for s_val in s_vals]
    y_vals = [z[i] + s_val *
              clothoid.eval_x_y(K * s_val**2, k * s_val, 0, 1)[1][0] for s_val in s_vals]

    plt.plot(x_vals, y_vals, '.', s, z, 'o')
    plt.show()

# i, j = sorted(random_subset_track(s, len(s), 2))
# print "min radius of curvature is " + str(1./curvature(i, j))
# plot_clothoid(i, j)

"""
C = 2.
D = 5.


def dz_tol(s):
    if s < 2 * C / D:
        return (s / 2)**2 * D
    else:
        return (s - C / D) * C

print "2_c/D is " + str(2 * C / D)
print "C^2/D is " + str(C**2 / D)

x = np.arange(0, 2, .01)
y = map(dz_tol, x)
plt.plot(x, y)
plt.show()
"""
