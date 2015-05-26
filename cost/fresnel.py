#!/usr/bin/env python
import math as m
import numpy as np
import scipy as sp
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 


def CosF(t):
	return math.cos((m.pi/2)*m.pow(t,2))

def SinF(t):
	return math.sin((m.pi/2)*m.pow(t,2))


def C(t):
	return sp.integrate(CosF, 0, t, full_output = 0)

def S(t):
	return sp.integrate(SinF, 0, t, full_output = 0)
