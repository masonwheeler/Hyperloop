import math
import numpy as np
import time
import scipy
import scipy.interpolate
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def Gamma(t):
	return np.array([[1, t, t**2, t**3, t**4, t**5], 
		[0, 1, 2*t, 3*t**2, 4*t**3, 5*t**4],
		[0, 0, 2, 6*t, 12*t**2, 20*t**3]])

def GammaEn(t):
	return np.array([[1, t, t**2, t**3, t**4, t**5], 
		[0, 1, 2*t, 3*t**2, 4*t**3, 5*t**4],
		[0, 0, 2, 6*t, 12*t**2, 20*t**3],
		[0, 0, 0, 6, 24*t, 60*t**2],
		[0, 0, 0, 0, 24, 120*t],
		[0, 0, 0, 0, 0, 0]])

def GammaSt(t):
	return np.array([[0, 0, 0, 0, 0, 0], 
		[0, -1, -2*t, -3*t**2, -4*t**3, -5*t**4],
		[0, 0, -2, -6*t, -12*t**2, -20*t**3],
		[0, 0, 0, -6, -24*t, -60*t**2],
		[0, 0, 0, 0, -24, -120*t],
		[1, t, t**2, t**3, t**4, t**5]])


def interpolate_quintic(x, t, dx0, d2x0, dxN, d2xN):
	N = len(x)-1
	b0 = np.array([x[0], dx0, d2x0])
	bN = np.array([x[N], dxN, d2xN])
	def bj(j):
		return np.array([x[j], 0, 0, 0, 0, x[j]])
	C = np.zeros((6*N, 6*N))
	b = np.zeros(6*N)
	b[0:3] = b0
	b[6*N - 3 :6*N] = bN
	for j in range(1, N):
		b[3 + 6*(j-1):3 + 6*j] = bj(j)
	C[0:3,0:6] = Gamma(t[0])
	C[6*N - 3:6*N, 6*N - 6:6*N] = Gamma(t[N])
	for j in range(1, N):
		C[3 + 6*(j-1) : 3 + 6*j,6*(j-1):6*j] = GammaEn(t[j])
		C[3 + 6*(j-1) : 3 + 6*j,6*j:6*(j+1)] = GammaSt(t[j])
	a = np.linalg.solve(C,b)
	return 5

t = [2,3,4,5,6]
x = [0,1,2,3,4]
dx0 = 1
d2x0 = 2
dxN = 5
d2xN = 6


print interpolate_quintic(x,t,dx0,d2x0,dxN,d2xN)