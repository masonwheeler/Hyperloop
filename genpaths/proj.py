"""
Jonathan Ward 3/18/2015

This file contains the function definitions for generating and validating
routes on the lattice.
"""

import mpl_toolkits.basemap.pyproj as pyproj

isn2004=pyproj.Proj("+proj=lcc +lat_1=64.25 +lat_2=65.75 +lat_0=65 +lon_0=-19 +x_0=1700000 +y_0=300000 +no_defs +a=6378137 +rf=298.257222101 +to_meter=1")