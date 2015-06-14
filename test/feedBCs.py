import math
import numpy as np
#from matplotlib import pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
import radiusOfCurvature as rad
import quintic as quint

def parse(tht_i_phi_i):
  N = len(tht_i_phi_i)-1
  p = rad.r_i(tht_i_phi_i)
  r = [rad.radius(p[(i - 1):(i + 2)]) for i in range(1, N-1)]
  v = [150]+[min([(math.sqrt(r[i]*.5*9.81)+math.sqrt(r[i+1]*.5*9.81))/2,330]) for i in range(0,N-3)]+[250,150]
  t = rad.t_i(v, p)
  return [t, p, v]

def process(t, p, v, n, mu):
	N = len(p) - 1
	def u(i):
		u_unnormalized = np.subtract(np.array(p[i+1]),np.array(p[i]))
		u_normalized = u_unnormalized / np.linalg.norm(u_unnormalized)
		return u_normalized.tolist()
	m = int(math.ceil((N+0.0) / (n+0.0)))
	G = [[0]*6 for i in range(m)]
	x = [point[mu] for point in p]
	if m == 1:
		G = [[t,p,0,0,0,0]]
	elif m == 2:
		G[0] = [t[0:n+1],x[0:n+1],0,0,v[n]* u(n)[mu],0]
		G[1] = [t[n:N+1],x[n:N+1], v[n] *u(n)[mu],0,0,0]
	else:
		G[0] = [t[0:n+1],x[0:n+1],0,0,v[n] *u(n)[mu],0]
		for j in range(1,m-1):
			G[j] = [t[j*n:(j+1)*n+1], x[j*n:(j+1)*n+1], v[j*n]*u(j*n)[mu],0,v[(j+1)*n]*u((j+1)*n)[mu],0]
		G[-1] = [t[(m-1)*n:N+1],x[(m-1)*n:N+1], v[(m-1)*n]* u((m-1)*n)[mu],0,0,0]
	return G






