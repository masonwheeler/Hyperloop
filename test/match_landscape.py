"""
Original Developer: David Roberts
Purpose of Module: To house an important algorithm which extracts
as many features of the route geometry as permitted by comfort constraints.
"""
import util
import config
import clothoid


def sortIndices(z, Type):
	zIndices = range(len(z))
	if Type == "elevation":
		return sorted(zIndices, key = lambda i: z[i], reverse=True)
	elif Type == "velocity":
		return sorted(zIndices, key = lambda i: z[i], reverse=False)


def curvature(i, j, z):   #Computes the curvature of the clothoid 
  x0, x1 = [i * config.pylonSpacing, j * config.pylonSpacing]
  tht0, tht1  = [0, 0]
  y0, y1 = [z[i], z[j]]
  k, K, L = clothoid.buildClothoid(x0, y0, theta0, x1, y1, theta1)
  extremalCurvatures = [k + L*K, k]
  return max(np.absolute(extremalCurvatures))


def genLandscape(x, Type):
  s = [0]*len(x)
  for i in range(0, len(x)-1):
    s[i+1] = s[i] + np.linalg.norm(x[i+1] - x[i])

  if Type == "elevation":
	J = [] 
  	index = 0
  	for k in range(int(s[-1]/config.pylonSpacing)):
   	  while s[index] < k*config.pylonSpacing:
      	index+=1
      J+=[index]
  	x = [x[j] for j in J]
 	s = [s[j] for j in J]
 	xlnglat = proj.geospatials_to_latlngs(x, config.proj)
  	z = elevation.usgs_elevation(xlnglat)

  elif Type == "velocity":
  	R = [util.points_to_radius(x[i-1:i+2]) for i in range(1,len(x)-1)]
  	z = [0] + [min(np.sqrt(r*config.lateralAccelTol), config.maxSpeed) for r in R] + [0]

  return [s, z]



def matchLandscape(s, z, Type):
	J = sortIndices(z, Type)
	K = [0,len(z)-1]

	def bad(index, Type):
	  new = util.placeIndexinList(index, K) # append newcomer to list; try it on for size
      
      if Type == "elevation":
      	curvatures = [curvature(K[new], K[new+1], z), curvature(K[new-1], K[new], z)]
      	bools = [k > config.latAccelTol/config.maxSpeed**2 for curvature in curvatures]

  	  elif Type == "velocity":
  	  	dz = [np.absolute(z[K[new+1]]-z[K[new]]), np.absolute(z[K[new]]-z[K[new-1]])]
  	  	ds = [s[K[new+1]]-s[K[new]], s[K[new]]-z[K[new-1]]]

  	  	V = [(z[K[new+1]]+z[K[new]])/2, (z[K[new]]+z[K[new-1]])/2]
  	  	C = [v * config.linearAccelTol for v in V] 
  	  	D = [v**2 * config.jerkTol for v in V] 
  	  	def dzTol(s):
  	  	  if s < 2*C/D:
  	  	  	return (s/2)**2*D
  	  	  else:
  	  	  	return (s-C/D)*C
       	bools = [dz[i] > dzTol(ds[i]) for i in range(len(ds))]
      
      K.pop(new) # return list back to normal

      return (bools[0] or bools[1])


	def matchPoint():
		i = 0
		while bad(J[i], Type) or i < len(J):
			i += 1
		if i !< len(J):
			return "Exhausted the landscape. Could not find a point to match."
		else:
			util.placeIndexinList(J.pop(i), K)
			return "Success! See if we can match another point."

	while matchLandscape() == "Success! See if we can match another point.":
		pass
	return [[s[k] for k in K], [z[k] for k in K]]


