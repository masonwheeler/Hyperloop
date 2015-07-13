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
  N = len(xPoints) - 1
  m = int(math.ceil((N+0.0) / (n+0.0)))
  G = [0 for i in range(m)]
  if m == 1:
  	G = [[tPoints, xPoints, 0, 0, 0, 0]]
  elif m == 2:
    G[0] = [tPoints[0:n+1],xPoints[0:n+1], 0, 0, (xPoints[n+1]-xPoints[n])/(tPoints[n+1]-tPoints[n]),0]
    G[1] = [tPoints[n:N+1],xPoints[n:N+1], (xPoints[n+1]-xPoints[n])/(tPoints[n+1]-tPoints[n]),0,0,0]
  else:
    G[0] = [tPoints[0:n+1],xPoints[0:n+1],0,0, (xPoints[n+1]-xPoints[n])/(tPoints[n+1]-tPoints[n]),0]  
    for j in range(1,m-1):
      G[j] = [tPoints[j*n:(j+1)*n+1],xPoints[j*n:(j+1)*n+1], (xPoints[j*n+1]-xPoints[j*n])/(tPoints[j*n+1]-tPoints[j*n]),0,(xPoints[(j+1)*n+1]-xPoints[(j+1)*n])/(tPoints[(j+1)*n+1]-tPoints[(j+1)*n]),0]
    G[-1] = [tPoints[(m-1)*n:N+1], xPoints[(m-1)*n:N+1],(xPoints[(m-1)*n+1]-xPoints[(m-1)*n])/(tPoints[(m-1)*n+1]-tPoints[(m-1)*n]) ,0,0,0]
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





















