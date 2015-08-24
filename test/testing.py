import random
import clothoid


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


s = sorted(list(set([random.uniform(0,100) for i in range(10)])))
z = [random.uniform(0,150) for i in range(len(s))]


def curvature(i, j):   #Computes the curvature of the clothoid 
    x0, x1 = [s[i], s[j]]
    y0, y1 = [z[i], z[j]]
    tht0, tht1  = [0, 0]
    k, K, L = clothoid.buildClothoid(x0, y0, theta0, x1, y1, theta1)
    extremalCurvatures = [k + L*K, k]
    return max(np.absolute(extremalCurvatures))

i, j = random_subset_track(s, len(s), 2)
print curvature(i,j)

