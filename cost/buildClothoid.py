#!/usr/bin/env python
import math as m
import numpy as np
from scipy.integrate import quad
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 
import time


#Computes Fresnel integrals and related momenta:
def CosF(t):
	return m.cos((m.pi/2) * m.pow(t,2))

def SinF(t):
	return m.sin((m.pi/2) * m.pow(t,2))

def C(t):
	return quad(CosF, 0, t, limit = 50000)[0]

def S(t):
	return quad(SinF, 0, t, limit = 50000)[0]

def evalXYaLarge(a, b, k):
	X, Y = [[0]*(k + 1), [0]*(k + 1)]
	s = a / m.fabs(a)
	z = m.sqrt(m.fabs(a)) / m.sqrt(m.pi)
	l = s * b / (z * m.pi)
	gamma = - s * m.pow(b,2) / (2 * m.fabs(a))
	t = 0.5 * a + b
	DC0 = C(l + z) - C(l)
	DS0 = S(l + z) - S(l)
	X[0] = (m.cos(gamma) * DC0 - s * m.sin(gamma) * DS0) / z
	Y[0] = (m.sin(gamma) * DC0 + s * m.cos(gamma) * DS0) / z
	X[1] = (m.sin(t) - b * X[0]) / a
	Y[1] = (1 - m.cos(t) - b * Y[0]) / a
	for j in range(1, k):
		X[j + 1] = (m.sin(t) - b * X[j] - j * Y[j - 1]) / a
		Y[j + 1] = (j * X[j - 1] - b * Y[j] - m.cos(t)) / a
	return [X, Y]

def rLommel(mu, nu, b):
	t = (1/(mu + nu + 1)) * (1/(mu - nu + 1))
	r = t
	n = 2
	while m.fabs(t) > m.pow(10,-10):
		t = t * ((-b) / (mu + 2*n - 1 - nu)) * (b / (mu + 2*n - 1 + nu)) 
		r = r + t
		n = n + 1
	return r

def evalXYaZero(b, k):
	X, Y = [[0]*(k + 1), [0]*(k + 1)]
	if m.fabs(b) < m.pow(10,-10):
		X[0] = 1 - (m.pow(b,2)/6) * (1-m.pow(b,2)/20)
		Y[0] = (m.pow(b,2)/2) * (1 - (m.pow(b,2)/6) * (1-m.pow(b,2)/30))
	else:
		X[0] = m.sin(b)/b
		Y[0] = (1 - m.cos(b))/b
	A = b * m.sin(b)
	D = m.sin(b) - b * m.cos(b)
	B = b * D
	C = -m.pow(b,2) * m.sin(b)
	for n in range(1, k + 1):
		X[n] = (n * A * rLommel(n + 0.5, 1.5, b) + B * rLommel(n + 1.5, 0.5, b) + m.cos(b)) / (1 + n)
		Y[n] = (C * rLommel(n + 1.5, 1.5, b) + m.sin(b)) / (2 + n) + D * rLommel(n + 0.5, 0.5, b)
	return [X, Y]


def evalXYaSmall(a, b, k, p):
	X0, Y0 = evalXYaZero(b, k + 4*p + 2)
	X, Y = [[0]*(k + 1), [0]*(k + 1)]
	t = 1
	for j in range(k + 1):
		X[j] = X0[j] - (a/2) * Y0[j + 2]
		Y[j] = Y0[j] - (a/2) * X0[j + 2]
	for n in range(1, p + 1):
		t = -t * m.pow(a,2)/(16 * n * (2*n - 1))
		for j in range(k + 1):
			X[j] += t * ((X0[4*n + j] - a * Y0[4*n + j + 2])/(4*n + 2))
			Y[j] += t * ((Y0[4*n + j] + a * X0[4*n + j + 2])/(4*n + 2))
	return [X, Y]

def evalXY(a, b, c, k):
	X, Y = [[0]*(k + 1), [0]*(k + 1)]
	if m.fabs(a) < m.pow(10,-10):
		[X0, Y0] = evalXYaSmall(a, b, k, 2)
	else:
		[X0, Y0] = evalXYaLarge(a, b, k)
	for j in range(k + 1):
		X[j] = X0[j] * m.cos(c) - Y0[j] * m.sin(c)
		Y[j] = X0[j] * m.sin(c) + Y0[j] * m.cos(c)
	return [X, Y]


#Computes minimum-length clothoid:
def findA(Ag, Dtht, Dphi, tol):
	A = Ag
	I = evalXY(2 * A, Dtht - A, Dphi, 2)
	while m.fabs(I[1][0]) > tol:
		A += - I[1][0]/(I[0][2]-I[0][1])
		I = evalXY(2 * A, Dtht - A, Dphi, 2)
	return A

def normalizeAngle(phi):
	while phi > m.pi:
		phi = phi - 2 * m.pi
	while phi < - m.pi:
		phi += 2 * m.pi
	return phi


def buildClothoid(x0, y0, tht0, x1, y1, tht1):
	Dx = x1 - x0
	Dy = y1 - y0
	r = m.sqrt(m.pow(Dx,2) + m.pow(Dy,2))
	phi = m.atan2(Dy, Dx)
	Dphi = normalizeAngle(tht0 - phi)
	Dtht = normalizeAngle(tht1 - tht0)
	A = findA(2.4674 * Dtht + 5.2478 * Dphi, Dtht, Dphi, m.pow(10,-10))
	I = evalXY(2 * A, Dtht - A, Dphi, 1)
	L = r / I[0][0]
	kappa = (Dtht - A) / L
	kappa_prime = (2 * A) / m.pow(L,2)
	return [kappa, kappa_prime, L]



#x0 = 1000.0
#y0 = 2000.0
#x1 = 80000.90679
#y1 = 10000.0062
#tht0 = -0.349066
#tht1 = 0.0


#start_time = time.time()

#kappa, kappa_prime, L = buildClothoid(x0, y0, tht0, x1, y1, tht1)
#xvals = [x0 + s * evalXY(kappa_prime * m.pow(s,2), kappa * s, tht0, 1)[0][0] for s in np.linspace(0, L , 100)]
#yvals = [y0 + s * evalXY(kappa_prime * m.pow(s,2), kappa * s, tht0, 1)[1][0] for s in np.linspace(0, L , 100)]
#fig = plt.figure()
#plt.plot(xvals, yvals)
#fig.suptitle('Clothoid, tht0 = 0, tht1 = 0.')
#plt.xlabel('x')
#plt.ylabel('y')

#print("--- %s seconds ---" % (time.time() - start_time))

#plt.show()



