import math
import numpy as np
import quintic as quint
import interpolation
#import genVelocity as gen
#import matplotlib.pyplot as plt
#import time

R =  6.371*(10**6)

def txPointstoxVals(tPoints, xPoints, n , mu):
  xPoints = [point[mu] for point in xPoints]
  N = n-1
  M = int(math.ceil((len(tPoints)-1.)/ N))
  G = [0 for i in range(M)]
  if M == 1:
  	G = [[tPoints, xPoints, 0, 0, 0, 0]]
  elif M == 2:
    G[0] = [tPoints[0:N+1],xPoints[0:N+1], 0, 0, (xPoints[N+1]-xPoints[N-1])/(tPoints[N+1]-tPoints[N-1]),0]
    G[M-1] = [tPoints[0:N+1],xPoints[0:N+1], (xPoints[N+1]-xPoints[N-1])/(tPoints[N+1]-tPoints[N-1]),0,0,0]
  else:
    G[0] = [tPoints[0:N+1],xPoints[0:N+1],0,0, (xPoints[N+1]-xPoints[N-1])/(tPoints[N+1]-tPoints[N-1]),0]  
    for k in range(2,M):
      G[k-1] = [tPoints[(k-1)*N:k*N+1],xPoints[(k-1)*N:k*N+1], (xPoints[(k-1)*N+1]-xPoints[(k-1)*N-1])/(tPoints[(k-1)*N+1]-tPoints[(k-1)*N-1]),0,(xPoints[k*N+1]-xPoints[k*N-1])/(tPoints[k*N+1]-tPoints[k*N-1]),0]
    G[M-1] = [tPoints[(M-1)*N:len(tPoints)], xPoints[(M-1)*N:len(xPoints)],(xPoints[(M-1)*N+1]-xPoints[(M-1)*N-1])/(tPoints[(M-1)*N+1]-tPoints[(M-1)*N-1]) ,0,0,0]
  xCoeffs = sum([quint.interp(g) for g in G],[])
  tVals = sum([[tPoints[j]+(i/128.)*(tPoints[j+1]-tPoints[j]) for i in range(2,128)] for j in range(len(tPoints)-1)],[])
  xVals = interpolation.Coeffs_to_Vals(xCoeffs, tVals, tPoints)
  return [tVals, xVals]

def txPointstoxyVals(tPoints, xPoints, n):
	return [txPointstoxVals(tPoints, xPoints, n, mu)[1] for mu in [0,1]]

#start = time.time()
#xPoints = np.genfromtxt('/Users/Droberts/Dropbox/The Hyperloop/keys/route2.csv', delimiter = ",")
#sPoints, vPoints = gen.xPointstovPoints(xPoints)
#tPoints = np.arange(10,200.000001,(200-10.)/(len(xPoints)-1))
#xVals, yVals = txPointstoxyVals(tPoints, xPoints, 7)

#plt.plot([p[0] for p in xPoints], [p[1] for p in xPoints], 'o', xVals, yVals, '-')
#print time.time()-start
#plt.show()





















