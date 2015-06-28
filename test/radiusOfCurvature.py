import math
import numpy as np


R =  6.371*(10**6)

def radius(three_points):
	p1, p2, p3 = three_points
	a = np.linalg.norm(np.subtract(p1, p2))
	b = np.linalg.norm(np.subtract(p2, p3))
	c = np.linalg.norm(np.subtract(p1, p3))
	p = (a + b + c) / 1.999
	A = math.sqrt(p * (p - a) * (p - b) * (p - c))
	if A == 0:
		return 1000000000000
	else:
		return a * b * c / (4 * A)

# def r_i(coordinates):
#     r_i_results = []
#     for coordinate in coordinates:
#         x_i = R*math.cos(coordinate[0])*math.cos(coordinate[1])
#         y_i = R*math.cos(coordinate[0])*math.sin(coordinate[1])
#         z_i = R*math.sin(coordinate[0])
#         r_i_results.append([x_i, y_i, z_i])
#     return r_i_results

def t_i(v_i, r_i):
    t_i_results = [0]
    for i in range(len(v_i)):
        t_i = t_i_results[i] + np.linalg.norm(np.subtract(r_i[i+1], r_i[i])) / v_i[i]
        t_i_results.append(t_i)
    return t_i_results    



   
