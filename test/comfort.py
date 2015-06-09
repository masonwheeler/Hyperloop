import config
import math
import numpy as np
#from matplotlib import pyplot as plt

#OUTLINE of SCRIPT (comfort.py):
#input vars: {t_i}, {x_i}, {v_i}, {a_i} (four lists of points in 3D space)
#output vars: c (comfort rating)

#SUB-SCRIPTS:
# 1. Find acceleration in passenger frame:
#      {t_i}, {v_i}, {a_i}  -->  {ap_i}
# 2. Take Fast Fourier Transform of psnger accel:
#      {ap_i}  -->  {ap_f}
# 3. Apply weighting filter and sum results
#      {ap_f} --> {w(f)*ap_f} --> c = sum_f |w(f)*ap_f|^2


# 1. Find acceleration in passenger frame:
#      {t_i}, {v_i}, {a_i}  -->  {T_i}, {N_i}, {B_i} -->  {ap_i}

def aPassenger(v, a, mu):
    T = [v[i]/np.linalg.norm(v[i]) for i in range(len(v))]   #tangent
    N = [np.cross(v[i], np.cross(a[i], v[i]))/np.linalg.norm(np.cross(v[i], np.cross(a[i], v[i])))  for i in range(len(v))]   #normal
    B = [np.cross(T[i], N[i]) for i in range(len(v))]   #binormal

    # Form change of basis matrix to the T,N,B frame.
    A = [np.linalg.inv(np.matrix.transpose(np.array([T[i],N[i],B[i]]))) for i in range(len(v))]

    # Apply change of basis to write accel in T,N,B (psnger) frame.
    ap = [np.dot(A[i],a[i]) for i in range(len(v))]
    return [acceleration[mu] for acceleration in ap]
    

# UNIT TEST (script #1):
#v = [[11.5554, 3.12132, 0.854199], 
#[3.56488, -8.25572, 7.94574], 
#[-10.4556, -5.66823, 1.59708], 
#[-6.79048, 6.50705, -7.45303], 
#[8.36076, 7.67568, -3.89636]]
#a = [[-5.41209, 26.5291, -23.7259],
#[33.4165, 13.344, -1.12782], 
#[15.7212, -22.4124, 23.3779], 
#[-28.5665, -20.2583, 8.33999], 
#[-24.534, 16.1627, -20.805]]

#print aPassenger(v, a, 1)
# should get [36, 36, 36, 36, 36]


# 2. Take Fast Fourier Transform of psnger accel:
#      {ap_i}  -->  {ap_f}
# 3. Apply weighting filter and sum results
#      {ap_f} --> {w(f)*ap_f} --> c = sum_f |w(f)*ap_f|^2

def wz(f):
	return 0.588*math.sqrt((1.911 * f**2 + (.25 * f**2)**2) / ((1 - 0.2777 *f**2)**2 + (1.563 * f - 0.0368 * f**3)**2))

def w(f):
	return [0, wz(f), 1.25 * wz(f)]

def fw_RMS(af, T, mu):
	N = len(af)+0.0
	T = T+0.0
	L = int(math.floor(N/2))
	awf = [w(m/T)[mu] * af[m] for m in range(-L, L+1)]
 	Sum = sum([np.absolute(accel)**2 for accel in awf])
	return (T/(N**2)) * Sum

def comfort(v, a, T, mu):
	N = len(v)
	al = aPassenger(v, a, mu)
	alf = np.fft.fft(al) / (N + 0.0)
	afw_RMS = fw_RMS(alf, T, mu)
	return (((100*math.sqrt(2))**2)*afw_RMS)**0.15


#UNIT TEST (script #2):
#v = [[-3.83292, 2.99503, -3.05167],
#[2.21044, -7.71139, 4.37497]]
#a = [[-1.86223, -8.09352, 9.76449], 
#[-8.83573, 7.20539, -6.74363]]

#print comfort(v, a, 500, 2)





