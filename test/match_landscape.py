"""
Original Developer: David Roberts
Purpose of Module: To house an important algorithm which extracts
as many features of the route geometry as permitted by comfort constraints.
"""

def sortIndices(z, Type):
	zIndices = range(len(z))
	if Type == "elevation":
		return sorted(zIndices, key = lambda i: z[i], reverse=True)
	elif Type == "curvature":
		return sorted(zIndices, key = lambda i: z[i], reverse=False)

def genLandscape(x, Type):


# if Type = "curvature", please make sure that z|_∂ = 0!
def matchLandscape(s, z, Type):
	J = sortIndices(z, Type)
	K = [0,len(z)-1]

	def bad(index, Type):
	  new = util.placeIndexinList(index, K) # append newcomer to list; try it on for size
      
      dzForward = np.absolute(z[K[new+1]]-z[K[new]])
      dzBackward = np.absolute(z[K[new]]-z[K[new-1]])

      # compute forward and backwards tolerances, given comfort constraints:
      if Type == "elevation":



  	  elif Type == "curvature":
      	if (np.absolute(s[K[new+1]] - s[K[new]]) < 2*C/D):
        	forwardTol = np.absolute((z[K[new+1]] - s[K[new+1]])/2)**2*D
	    else: 
	      forwardTol = np.absolute(s[K[new+1]] - s[K[new]]-C/D)*C

	    if (np.absolute(s[K[new]] - s[K[new-1]]) < 2*C/D):
	      backwardTol = np.absolute((s[K[new]] - s[K[new-1]])/2)**2*D
	    else: 
	      backwardTol = np.absolute(s[K[new]] - s[K[new-1]]-C/D)*C


      K.pop(newLocation) # return list back to normal
      if (dzForward > forwardTol or dzBackward > backwardTol):  # Let's see; how did we do?
        return True
      else:
        return False


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


