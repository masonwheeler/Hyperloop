"""
Original Developer: Jonathan Ward
Purpose of Module: To perform the core computations for each city pair.
Last Modified: 8/29/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To validate using pylint
"""

# Standard Modules:
import time

# Our Modules:
import cacher
import saver
import spatial
import spatiotemporal
import routes


def pair_analysis(start, end):
    """Builds routes between start and end points
    """
    cacher.create_necessaryfolders(start, end)
    time_a = time.time()
    paths_3d = spatial.city_pair_to_paths_3d(start, end)
    paths_4d = spatiotemporal.paths_3d_to_paths_4d(paths_3d)
    routes_set = routes.RoutesSet(paths_4d)
    saver.save_routes_set(routes_set)
    time_b = time.time()
    print "City pair analysis took " + str(time_b - time_a) + " seconds."
    return 0
