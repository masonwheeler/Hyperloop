import comfort as cmft
import interpolation as intrp

def Coeffs_to_VelAccel(a, s):
    da = [[j * quintic[j+1] for j in range(5)] for quintic in a]
    d2a = [[j * quartic[j+1] for j in range(4)] for quartic in da]
    v = [intrp.Coeffs_to_Vals(da, five_minute_interval, t) for five_minute_interval in s]
    A = [intrp.Coeffs_to_Vals(d2a, five_minute_interval, t) for five_minute_interval in s]
    return [v, A]

def comfort_and_Triptime(tht_i_phi_i):
    #Input is waypoints in long-lat (in radians): tht_i_phi_i
    #Compute coefficients of piecewise quintic polynomial:
    ax, ay, az, t = intrp.Points_to_Coeffs(tht_i_phi_i, 6)

    # Form list "s" of sampling times:
    Q = 2**8 # number of rectangles in the Riemann sum (for efficiency, keep this a power of two).
    L = int(math.floor(t[-1]/300))
    s = [[t[-1] * (i + j/Q)/L for j in range(Q)] for i in range(L)]

    # Sample velocity and acceleration at "s":
    vx, Ax = Coeffs_to_VelAccel(ax, s)
    vy, Ay = Coeffs_to_VelAccel(ay, s)
    vz, Az = Coeffs_to_VelAccel(az, s)
    v = [[[vx[i][j], vy[i][j], vz[i][j]] for j in range(len(vx[i]))] for i in range(len(vx))]
    a = [[[Ax[i][j], Ay[i][j], Az[i][j]] for j in range(len(Ax[i]))] for i in range(len(Ax))]

    #Output is comfort rating and triptime:
    T = t[-1] / L
    mu = 1
    comfort_Ratings = [cmft.comfort(v[i], a[i], T, mu) for i in range(len(v))]
    comfort = max(comfort_Ratings)
    triptime = t[-1]

    return [comfort, triptime]
