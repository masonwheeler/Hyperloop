"""
Original Developer: David Roberts
Purpose of Module: To evaluate passenger comfort using
                   Sperling's comfort index (Wz).

Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify naming and add citations.

Citations:
   "Ride comfort in Tilting Trains"
    - Johan Forstberg
   "Experimental and Analytical Ride Comfort Evaluation of a Railway Coach"
    - K. V. Gangadharan

OUTLINE of SCRIPT (comfort.py):
input vars: {t_i}, {x_i}, {v_i}, {a_i} (four lists of points in 3D space)
output vars: c (comfort rating)

SUB-SCRIPTS:
 1. Find acceleration in passenger frame:
      {t_i}, {v_i}, {a_i}  -->  {ap_i}
 2. Take Fast Fourier Transform of passenger accel:
      {ap_i}  -->  {ap_f}
 3. Apply weighting filter and sum results
      {ap_f} --> {w(f)*ap_f} --> c = sum_f |w(f)*ap_f|^2
"""

#Standard Modules:
import math
import numpy as np

#Our Modules:
import config



def accel_passenger(vel, accel, component):
    """
    Find acceleration in passenger frame:
       {t_i}, {v_i}, {a_i}  -->  {T_i}, {N_i}, {B_i} -->  {ap_i}
    """
    tangentVector = [vel[i] / np.linalg.norm(vel[i]) for i in range(len(vel))]
    normalVector = [np.cross(vel[i], np.cross(accel[i], vel[i]))/
                   np.linalg.norm(np.cross(vel[i], np.cross(accel[i], vel[i])))
                   for i in range(len(vel))]
    binormalVector = [np.cross(tangentVector[i], normalVector[i])
                      for i in range(len(vel))]

    # Change of basis matrix for transforming to the tangent, normal, binormal
    # (passenger) frame.
    changeOfBasisMatrix = [np.linalg.inv(np.matrix.transpose(
             np.array([tangentVector[i], normalVector[i], binormalVector[i]])))
             for i in range(len(vel))]

    # Apply change of basis to write the acceleration in tangent, normal, binormal
    # (passenger) frame.
    accelPassenger = [np.dot(changeOfBasisMatrix[i], accel[i]) for i in range(len(vel))]
    accelPassengerComponents = [accelPassengerVal[component] for
                                accelPassengerVal in accelPassenger]
    return accelPassengerComponents

# UNIT TEST (script #1):

"""
v = [[11.5554, 3.12132, 0.854199], 
     [3.56488, -8.25572, 7.94574], 
     [-10.4556, -5.66823, 1.59708], 
     [-6.79048, 6.50705, -7.45303], 
     [8.36076, 7.67568, -3.89636]]

a = [[-5.41209, 26.5291, -23.7259],
     [33.4165, 13.344, -1.12782], 
     [15.7212, -22.4124, 23.3779], 
     [-28.5665, -20.2583, 8.33999], 
     [-24.534, 16.1627, -20.805]]

assert(aPassenger(v, a, 1) == [36, 36, 36, 36, 36])
"""

"""
2. Take Fast Fourier Transform of psnger accel:
      {ap_i}  -->  {ap_f}
3. Apply weighting filter and sum results
      {ap_f} --> {w(f)*ap_f} --> c = sum_f |w(f)*ap_f|^2
"""

"""
See (Gangadharan) equations (7) and (8) for weighting factors.
"""

def vertical_weighting_factor(frequency):
    verticalWeightingFactor = 0.588 * math.sqrt(
      (1.911 * frequency**2 + (.25 * frequency**2)**2) /
      ((1 - 0.2777 * frequency**2)**2 + 
       (1.563 * frequency - 0.0368 * frequency**3)**2))
    return verticalWeightingFactor

def horizontal_weighting_factor(frequency):
    return 1.25 * vertical_weighting_factor(frequency)

def weighting_factors(frequency):
    weightingFactors = [0, vertical_weighing_factor(frequency),
                        horizontal_weighing_factor(frequency)]
    return weightingFactors

"""
See (Forstberg) equation (3.1) for Sperling Comfort Index equation.
"""

def frequency_weighted_rms(accelFrequency, timeInterval, component):
    frequencyWidth = float(len(accelFrequency))
    timeInterval = float(timeInterval)
    frequencyHalfWidth = int(math.floor(frequencyWidth/2.0))
    accelFrequencyWeighted = [
        (weighting_factors(frequencyIndex/timeInterval)[accelComponent]
        * accelFrequency[frequencyIndex]) for frequencyIndex
        in range(-frequencyHalfWidth, frequencyHalfWidth+1)]
    sfrequencyWeightedRMS = np.sqrt(sum([np.absolute(accelVal)**2
                                    for accelVal in accelFrequencyWeighted]))
    return frequencyWeightedRMS

def sperling_comfort_index(vel, accel, timeInterval, component):
    numTimePoints = len(vel)
    accelPassengerComponents = accel_passenger(vel, accel, component)
    accelPassengerFrequency = np.fft.fft(accelPassengerComponents) / numTimePoints
    accelFrequencyWeightedRMS = frequencyWeightedRMS(accelPassengerFrequency,
                                                     timeInterval, component)
    sperlingComfortIndex =  4.42*(accelFrequencyWeightedRMS)**0.3
    return sperlingComfortIndex



"""
T = 300
N = 10000
al = [5*math.cos(2*math.pi*2*t/T) for t in np.linspace(0,T,N)]
alf = np.fft.fft(al)/ N
afw_RMS = fw_RMS(alf, T, 1)
print 4.42*(afw_RMS)**0.3
print 4.42*(w(2./T)[1]**2*(25/2.))**0.3
"""

#UNIT TEST (script #2):
"""
v = [[-3.83292, 2.99503, -3.05167],
     [2.21044, -7.71139, 4.37497]]

a = [[-1.86223, -8.09352, 9.76449], 
     [-8.83573, 7.20539, -6.74363]]

print comfort(v, a, 500, 2)
"""

