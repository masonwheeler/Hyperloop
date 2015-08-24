import random
import clothoid
import matplotlib.pyplot as plt
import numpy as np

def random_subset_track( a, N, K ):
    used = [ False ] * N
    result = []

    for i in range( 0, K ):
        # get a random element between 0 and N.
        j = int( random.random() * N )
        while ( used[j] ):
            j = int( random.random() * N )
        result.append( j )
        used[j] = True

    return result


# s = sorted(list(set([random.uniform(0,100) for i in range(10)])))
# z = [random.uniform(0,150) for i in range(len(s))]


def curvature(i, j):   #Computes the curvature of the clothoid 
    x0, x1 = [s[i], s[j]]
    y0, y1 = [z[i], z[j]]
    tht0, tht1  = [0, 0]
    k, K, L = clothoid.buildClothoid(x0, y0, tht0, x1, y1, tht1)
    extremalCurvatures = [k + L*K, k]
    return max(np.absolute(extremalCurvatures))

def plot_clothoid(i, j):
    x0, x1 = [s[i], s[j]]
    y0, y1 = [z[i], z[j]]
    tht0, tht1  = [0, 0]
    k, K, L = clothoid.buildClothoid(x0, y0, tht0, x1, y1, tht1)
    sVals = np.arange(0, L, 1)
    xVals = [s[i] + sVal * clothoid.evalXY(K*sVal**2, k*sVal, 0, 1)[0][0] for sVal in sVals]
    yVals = [z[i] + sVal * clothoid.evalXY(K*sVal**2, k*sVal, 0, 1)[1][0] for sVal in sVals]

    plt.plot(xVals, yVals, '.', s, z, 'o')
    plt.show()

# i, j = sorted(random_subset_track(s, len(s), 2))
# print "min radius of curvature is " + str(1./curvature(i, j))
# plot_clothoid(i, j)


C = 2.
D = 5.

def dzTol(s):
    if s < 2*C/D:
        return (s/2)**2*D
    else:
        return (s-C/D)*C

print "2C/D is " + str(2*C/D)
print "C^2/D is " + str(C**2/D)

x = np.arange(0,2,.01)
y = map(dzTol, x)
plt.plot(x, y)
plt.show()
