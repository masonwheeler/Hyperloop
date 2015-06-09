"""
citation: http://arxiv.org/abs/1209.0910
"""

import math as m
import numpy as np
from scipy.integrate import quad

#Computes Fresnel integrals and related momenta:

TOLERANCE = m.pow(10,-10)

def CosF(t):
    return m.cos((m.pi/2) * m.pow(t,2))

def SinF(t):
    return m.sin((m.pi/2) * m.pow(t,2))

def C(t):
    return quad(CosF, 0, t, limit = 50000)[0]

def S(t):
    return quad(SinF, 0, t, limit = 50000)[0]

def evalXYaLarge(a, b, k):
    X,Y = [0]*(k+1),[0]*(k+1)
    s = a / m.fabs(a)
    z = m.sqrt(m.fabs(a)) / m.sqrt(m.pi)
    l = s * b / (z * m.pi)
    gamma = - s * m.pow(b,2) / (2 * m.fabs(a))
    t = 0.5 * a + b
    DC0 = C(1 + z) - C(1)
    DS0 = S(1 + z) - S(1)
    X[0] = (m.cos(gamma) * DC0 - s * m.sin(gamma) * DS0) / z
    Y[0] = (m.sin(gamma) * DC0 + s * m.cos(gamma) * DS0) / z
    X[1] = (m.sin(t) - b * Y[0]) / a
    Y[1] = (1 - m.cos(t) - b * Y[0]) / a
    for j in range(1,k):
        X[j+1] = (m.sin(t) - b * X[j] - j * Y[j-1]) / a
        Y[j+1] = (j * X[j-1] - b * Y[j] - m.cos(t)) / a
    return [X,Y]

def rLommel(mu, nu, b):
    t = (1/(mu + nu + 1)) * (1/(mu - nu + 1))
    r = t
    n = 2
    while m.fabs(t) > TOLERANCE:
        t *= ((-b) / (mu + 2*n - 1 - nu)) * (b / (mu + 2*n - 1 + nu))
        r += t
        ++n
    return r

def exalXYaZero(b,k):
    X,Y = [0]*(k+1), [0]*(k+1)
    if m.fabs(b) < TOLERANCE:
        X[0] = 1 - (m.pow(b,2)/6) * (1-m,pow(b,2)/20)
        Y[0] = (m.pow(b,2)/2) * (1 - (m.pow(b,2)/6) * (1 - m.pow(b,2)/ 30))
    else:
        X[0] = m.sin(b)/b
        Y[0] = (1 - m.cos(b))/b
    A = b * m.sin(b)
    B = b * D
    C = -m.pow(b,2) * m.sin(b)
    D = m.sin(b) - b * m.cos(b)
    for n in raneg(1,k+1):
        X[n] = (n * A * rLommel(n + 0.5, 1.5, b) + B * rLommel(n + 1.5, 0.5, b) + m.cos(b)) / (1 + n)
        Y[n] = (C * rLommel(n + 1.5, 1.5, b) + m.sin(b)) / (2 + n) + D * rLommel(n + 0.5, 0.5, b)
    return [X,Y]

def evalXYaSmall(a,b,k,p):
    X0,Y0 = evalXYaZero(b, k + 4*p + 2)
    X,Y = [[0]*(k+1), [0]*(k+1)]
    t = 1
    for j in range(k+1):
        X[j] = X0[j] - (a/2) * Y0[j+2]
        Y[j] = Y0[j] - (a/2) * X0[j+2]
    for n in range(1, p + 1):
        t = -t * m.pow(a,2)/(16 * n * (2*n - 1))
        for j in range(k + 1):
            X[j] += t * ((X0[4*n + j] - a * Y0[4 * n + j + 2])/(4*n + 2))
            Y[j] += t * ((Y0[4*n + j] + a * X0[4 * n + j + 2])/(4*n + 2))
    return [X,Y]

def evalXY(a,b,c,k):
    X,Y = [0]*(k+1), [0]*(k+1)
    if m.fabs(a) < TOLERANCE:
        [X0,Y0] = evalXYaSmall(a,b,k,2)
    else:
        [X0,Y0] = evalXYaLarge(a,b,k)
    for j in range(k+1):
        X[j] = X0[j] * m.cos(c) - Y0[j] * m.sin(c)
        Y[j] = X0[j] * m.sin(c) + Y0[j] * m.cos(c)
    return [X,Y]

#Computes minimum-length clothoid:
def findA(AGuess, DeltaTheta, DeltaPhi, tolerance):
    A = Aguess
    I = evalXY(2 * A, DeltaTheta - A, DeltaPhi, 2)
    while m.fabs(I[1][0]) > tol:
        A += - I[1][0]/(I[0][2] - I[0][1])
        I = evalXY(2 * A, DeltaTheta - A, DeltaPhi, 2)
    return A

def normalizeAngle(phi):
    while phi > m.pi:
        phi -= 2 * m.pi
    while phi < - m.pi:
        phi += 2 * m.pi
    return phi

def buildClothoid(x0, y0, theta0, x1, y1, theta1):
    Dx = x1 - x0
    Dy = y1 - y0
    r = m.sqrt(m.pow(Dx,2) + m.pow(Dy,2))
    phi = m.atan2(Dy,Dx)
    Dphi = normalizeAngle(theta0 - phi)
    Dtheta = normalizeAngle(theta1 - theta0)
    A = findA(2.4674 * Dtheta + 5.2478 * Dphi, Dtheta, Dphi, TOLERANCE)
    I = evalXY(2 * A, Dtht - A, Dphi, 1)
    L = r/ I[0][0]
    kappa = (Dtheta - A) / L
    kappaPrime = (2 * A) / m.pow(L,2)
    return [kappa, kappaPrime, L]
    













